"""Meta WhatsApp Cloud API webhook routes.

Funded-slot batch gate:
- Every image = one ₹500 Earring Catalog Pack (7 styles).
- slots = wallet_balance // 500 -> exactly that many packs execute.
- Every unfunded image immediately receives the exact recharge hold message.
- Funded packs execute via FastAPI BackgroundTasks (no Celery/Redis dependency).
"""

from typing import Any, Dict, List, Optional, Tuple
import asyncio
import json
import re

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.customer import Customer
from app.models.whatsapp_ingestion import WhatsAppIngestion
from app.repositories.base import BaseRepository
from app.services.image_quality_guard import validate_jewelry_image_with_gemini
from app.services.meta_whatsapp_service import (
    CATALOG_PACK_ACK_TEMPLATE,
    download_media,
    get_media_url,
    parse_webhook_entry,
    process_whatsapp_catalog_pack,
    send_whatsapp_cta_url_button,
    send_whatsapp_text,
    validate_image,
    verify_webhook_signature,
)
from app.services.razorpay_service import create_recharge_payment_link
from app.services.upload_service import UploadService
from app.services.wallet_service import get_customer
from app.utils.logger import logger

router = APIRouter(prefix="/api/meta", tags=["Meta WhatsApp Webhook"])

DEFAULT_PAYMENT_URL = "https://rzp.io/rzp/FbuLh9je"
COST_PER_PRODUCT = 500

# Exact unfunded-image hold message (sent quoted against the user's photo).
HOLD_MESSAGE_TEMPLATE = (
    "⚠️ Your balance is ₹0 for this image.\n\n"
    "₹500 required to generate photos for this design.\n"
    f"Tap to recharge: {DEFAULT_PAYMENT_URL}"
)


def _find_customer_safe(db: Session, sender: str) -> Optional[Customer]:
    """Helper to find customer regardless of leading + or 91 country code differences."""
    clean_sender = sender.lstrip("+").strip()
    c = get_customer(db, clean_sender) or get_customer(db, sender)
    if not c and len(clean_sender) >= 10:
        c = db.query(Customer).filter(Customer.whatsapp_id.contains(clean_sender[-10:])).first()
    return c


def _refund_pack_charge(db: Session, customer: Optional[Customer]) -> None:
    """Refund a single ₹500 pack charge after a post-deduction failure."""
    if customer is None:
        return
    customer.wallet_balance = int(customer.wallet_balance or 0) + COST_PER_PRODUCT
    db.commit()
    db.refresh(customer)
    logger.warning(f"Refunded ₹{COST_PER_PRODUCT} pack charge: whatsapp_id={customer.whatsapp_id}")


# ─── Background generation trigger ──────────────────────────────────────


async def _trigger_generation(ingestion_id: str) -> None:
    """Background task that re-runs the 7-style catalog pack for an ingestion.

    Called via BackgroundTasks after successful image ingestion (and by the
    manual retry endpoint). This keeps the webhook response fast (< 5s) while
    generation runs async — no Celery/Redis required.
    """
    try:
        success = await process_whatsapp_catalog_pack(ingestion_id)
        if success:
            logger.info(f"Background generation completed: ingestion_id={ingestion_id}")
        else:
            logger.warning(f"Background generation failed: ingestion_id={ingestion_id}")
    except Exception as e:
        logger.error(f"Background generation exception: ingestion_id={ingestion_id} error={e}")


@router.get("/webhook", summary="Meta webhook verification")
async def verify_webhook(
    hub_mode: Optional[str] = None,
    hub_verify_token: Optional[str] = None,
    hub_challenge: Optional[str] = None,
) -> PlainTextResponse:
    if hub_mode != "subscribe" or not hub_verify_token or hub_verify_token != settings.META_VERIFY_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid verification token or mode",
        )

    if not hub_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing challenge parameter",
        )

    return PlainTextResponse(content=hub_challenge)


@router.post("/webhook", summary="Receive WhatsApp webhook events")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        raw_body = await request.body()
        if not raw_body:
            return {"status": "ignored", "message": "Empty body"}
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception as e:
        logger.error("Failed to parse webhook JSON payload: {}", e)
        return {"status": "error", "message": "Invalid JSON payload"}

    if settings.META_APP_SECRET:
        signature = request.headers.get("X-Hub-Signature-256")
        if not verify_webhook_signature(raw_body, signature):
            return {"status": "error", "message": "Invalid signature"}

    if payload.get("object") == "whatsapp_business_account" and "entry" not in payload:
        return {"status": "ok"}

    if payload.get("object") != "whatsapp_business_account":
        return {"status": "ignored", "message": "Not a WhatsApp business account event"}

    entries = payload.get("entry", [])
    if not entries:
        return {"status": "ignored", "message": "No entries in webhook payload"}

    ingestion_repo = BaseRepository(WhatsAppIngestion, db)
    image_events: List[Dict[str, Any]] = []

    for entry in entries:
        events = parse_webhook_entry(entry)

        for event in events:
            event_type = event.get("type", "")

            if event_type == "status":
                continue

            if event_type == "text":
                sender = event.get("sender", "")
                raw_text = event.get("body", "").strip()
                lower_text = raw_text.lower()
                logger.info("Text message received: sender={} text='{}'", sender, raw_text)

                if "name:" in lower_text and ("business" in lower_text or "gst" in lower_text):
                    user_name = "there"
                    biz_name = "Jewelry Business"
                    gst_val = "N/A"
                    addr_val = "N/A"

                    for line in raw_text.splitlines():
                        line_clean = line.strip()
                        l_low = line_clean.lower()
                        if l_low.startswith("name:"):
                            extracted = line_clean.split(":", 1)[1].strip()
                            if extracted:
                                user_name = extracted.split()[0]
                        elif "business name" in l_low and ":" in line_clean:
                            extracted_biz = line_clean.split(":", 1)[1].strip()
                            if extracted_biz:
                                biz_name = extracted_biz
                        elif "gst" in l_low and ":" in line_clean:
                            extracted_gst = line_clean.split(":", 1)[1].strip()
                            if extracted_gst:
                                gst_val = extracted_gst
                        elif "address" in l_low and ":" in line_clean:
                            extracted_addr = line_clean.split(":", 1)[1].strip()
                            if extracted_addr:
                                addr_val = extracted_addr

                    clean_sender = sender.lstrip("+").strip()
                    cust = _find_customer_safe(db, sender)

                    if cust is not None:
                        cust.full_name = user_name
                        cust.business_name = biz_name
                        cust.gst_number = gst_val
                        cust.address = addr_val
                        cust.is_registered = True
                        db.commit()
                    else:
                        try:
                            cust = BaseRepository(Customer, db).create(
                                whatsapp_id=clean_sender,
                                full_name=user_name,
                                business_name=biz_name,
                                gst_number=gst_val,
                                address=addr_val,
                                wallet_balance=0,
                                is_registered=True,
                            )
                        except Exception as create_error:
                            db.rollback()
                            logger.error(f"Onboarding customer creation failed: {create_error}")
                            cust = _find_customer_safe(db, sender)

                    if cust is None:
                        continue

                    confirm_msg = (
                        f"Congratulations {user_name}! You’re registered with Moraa Studio 🎉\n"
                        f"You’re all set to start creating stunning product photos."
                    )
                    try:
                        pay_url = await create_recharge_payment_link(
                            customer_phone=sender,
                            customer_name=user_name,
                            amount=500,
                        )
                    except Exception as e:
                        logger.error("Failed to generate registration recharge link: {}", e)
                        pay_url = DEFAULT_PAYMENT_URL

                    await send_whatsapp_cta_url_button(
                        recipient_id=sender,
                        body_text=confirm_msg,
                        button_label="Recharge to use",
                        url=pay_url or DEFAULT_PAYMENT_URL,
                    )
                    continue

                if re.search(r"\b(hi|hii|hello|hey|start)\b", lower_text):
                    msg_part_1 = (
                        "Hi there! Welcome to Moraa Studio ✨\n"
                        "We help you turn raw jewelry photos into polished, e-commerce ready images "
                    )
                    msg_part_2 = (
                        "Let’s get you set up, it only takes a minute!\n\n"
                        "Quick registration 📋\n"
                        "Copy this, fill in your details and send it right back:\n\n"
                        "Name:\n"
                        "Business name:\n"
                        "GST number:\n"
                        "Business address:"
                    )
                    await send_whatsapp_text(sender, msg_part_1)
                    await asyncio.sleep(1)
                    await send_whatsapp_text(sender, msg_part_2)
                    continue

                recharge_match = re.search(r"\b(?:recharge|pay|add)\s*(?:rs\.?|inr|₹)?\s*(\d+)\b", lower_text)
                if recharge_match:
                    requested_amount = int(recharge_match.group(1))
                    if requested_amount < 500:
                        await send_whatsapp_text(
                            sender,
                            "Minimum recharge amount is ₹500 ⚠️\nPlease enter an amount of ₹500 or more."
                        )
                        continue

                    cust = _find_customer_safe(db, sender)
                    cust_name = getattr(cust, "full_name", "Customer") if cust else "Customer"
                    try:
                        pay_url = await create_recharge_payment_link(
                            customer_phone=sender,
                            customer_name=cust_name,
                            amount=requested_amount,
                        )
                    except Exception as e:
                        logger.error("Failed to generate custom recharge link: {}", e)
                        pay_url = DEFAULT_PAYMENT_URL

                    await send_whatsapp_cta_url_button(
                        recipient_id=sender,
                        body_text=f"Here is your recharge link for ₹{requested_amount} 💳\nTap below to complete the payment.",
                        button_label=f"Pay ₹{requested_amount}"[:20],
                        url=pay_url or DEFAULT_PAYMENT_URL,
                    )
                    continue

                continue

            if event_type == "interactive" and event.get("subtype") == "button_reply":
                button_reply = event.get("button_reply", {})
                b_id = button_reply.get("id", "")
                sender = event.get("sender", "")

                if b_id.startswith("feedback_"):
                    fb_response = (
                        "Thank you so much for the love! Glad you liked it 🎉 Send your next photo anytime!"
                        if b_id.startswith("feedback_positive")
                        else "Thanks for letting us know! We’re constantly training our model. You can retry with another angle or lighting 📸"
                    )
                    await send_whatsapp_text(recipient_id=sender, message_text=fb_response)
                    continue

                continue

            if event_type == "image":
                image_events.append(event)

    if not image_events:
        return {"status": "ok", "images_processed": 0}

    sender = image_events[0].get("sender", "")
    raw_sender = sender.strip()
    clean_sender = raw_sender.lstrip("+").strip()
    phone_suffix = clean_sender[-10:] if len(clean_sender) >= 10 else clean_sender

    # ── FUNDED SLOT GATE ──
    # Load the customer row ONCE with a clean contains() query (handles
    # "+91…", "91…" and bare numbers alike), then derive paid slots from the
    # real balance. Exactly `slots` images execute a full 7-style pack; every
    # remaining image immediately receives the exact hold message — never a
    # silent drop.
    customer = db.query(Customer).filter(Customer.whatsapp_id.contains(phone_suffix)).first()
    current_bal = int(customer.wallet_balance or 0) if customer else 0
    slots = current_bal // COST_PER_PRODUCT

    processed_ingestion_ids: List[str] = []

    for img_ev in image_events:
        message_id = img_ev.get("message_id", "")
        media_id = img_ev.get("media_id", "")
        mime_type = img_ev.get("mime_type", "")
        caption = img_ev.get("caption", "")
        timestamp = img_ev.get("timestamp", "")

        if not media_id:
            logger.warning(f"Image message missing media_id: message_id={message_id[:20]}...")
            ingestion_repo.create(
                external_user_id=sender,
                external_message_id=message_id,
                external_media_id="",
                channel="whatsapp",
                caption=caption,
                mime_type=mime_type,
                timestamp=timestamp,
                status="failed",
                error_message="Missing media_id in webhook payload",
            )
            db.commit()
            continue

        if slots <= 0:
            # Unfunded image — exact hold message, quoted against the photo.
            await send_whatsapp_text(
                recipient_id=sender,
                message_text=HOLD_MESSAGE_TEMPLATE,
                reply_to_message_id=message_id,
            )
            continue

        # Duplicate webhook deliveries must never double-charge or re-queue.
        existing = ingestion_repo.find_first(external_message_id=message_id)
        if existing:
            continue

        # REAL balance deduction — directly on the ORM row, then persist and
        # re-read so every subsequent iteration (and the 7/7 delivery caption)
        # sees the true remaining balance. No separate UPDATE statement that
        # can diverge from the identity-mapped object.
        customer.wallet_balance = int(customer.wallet_balance or 0) - COST_PER_PRODUCT
        db.commit()
        db.refresh(customer)
        slots -= 1

        media_url = await get_media_url(media_id)
        if not media_url:
            _refund_pack_charge(db, customer)
            continue

        download_result: Optional[Tuple[bytes, str]] = await download_media(media_url)
        if not download_result:
            _refund_pack_charge(db, customer)
            continue

        image_bytes, content_type = download_result
        is_valid, _validation_error = validate_image(image_bytes, content_type)
        if not is_valid:
            _refund_pack_charge(db, customer)
            continue

        # AI Quality Guard (Gemini) — reject unusable jewellery photos.
        ai_valid, tip_msg = await validate_jewelry_image_with_gemini(image_bytes, content_type)
        if not ai_valid:
            _refund_pack_charge(db, customer)
            reject_text = f"Photo quality check ⚠️\n\n{tip_msg}\n\nPlease snap a new photo and upload again!"
            await send_whatsapp_text(sender, reject_text, reply_to_message_id=message_id)
            continue

        ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
        ext = ext_map.get(content_type, "jpg")
        filename = f"whatsapp_{message_id[:20]}.{ext}"

        upload_service = UploadService(db)
        try:
            upload_result = await upload_service.process_upload(
                file_data=image_bytes,
                filename=filename,
                file_size=len(image_bytes),
                mime_type=content_type,
            )
        except Exception as upload_error:
            logger.error(
                f"WhatsApp upload failed: message_id={message_id[:20]}... error={upload_error}"
            )
            _refund_pack_charge(db, customer)
            continue

        ingestion = ingestion_repo.create(
            external_user_id=sender,
            external_message_id=message_id,
            external_media_id=media_id,
            channel="whatsapp",
            caption=caption,
            mime_type=content_type,
            timestamp=timestamp,
            image_id=upload_result.id,
            file_size=len(image_bytes),
            status="pack_queued",
        )
        db.commit()

        processed_ingestion_ids.append(ingestion.id)

        # Quoted ACK on the funded image.
        await send_whatsapp_text(sender, CATALOG_PACK_ACK_TEMPLATE, reply_to_message_id=message_id)

        # Execute the 7-style catalog pack via FastAPI background task (no Celery/Redis).
        background_tasks.add_task(process_whatsapp_catalog_pack, ingestion.id)

    return {
        "status": "ok",
        "queued": len(processed_ingestion_ids),
    }


@router.post(
    "/webhook/retry/{ingestion_id}",
    summary="Retry delivery for a failed ingestion",
    description=(
        "Manually retry generation/delivery for an ingestion that failed. "
        "Only works for status 'failed' or 'delivery_failed'. "
        "Re-runs the 7-style catalog pack and attempts delivery again."
    ),
)
async def retry_delivery(
    ingestion_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retry a failed WhatsApp ingestion."""
    ingestion = db.query(WhatsAppIngestion).filter(
        WhatsAppIngestion.id == ingestion_id
    ).first()

    if not ingestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingestion not found: {ingestion_id}",
        )

    if ingestion.status not in ("failed", "delivery_failed"):
        return {
            "status": "error",
            "message": f"Cannot retry ingestion in status '{ingestion.status}'",
        }

    # Reset status so the catalog pack will be re-processed.
    ingestion.status = "stored"
    ingestion.error_message = None
    db.commit()

    background_tasks.add_task(_trigger_generation, ingestion.id)

    logger.info(
        f"Retry triggered: ingestion_id={ingestion_id} "
        f"user={ingestion.external_user_id}"
    )

    return {
        "status": "queued",
        "message": "Generation retry queued",
        "ingestion_id": ingestion_id,
    }


# ─── GET — Ingestion Status ─────────────────────────────────────────────


@router.get(
    "/webhook/status/{ingestion_id}",
    summary="Check ingestion status",
)
async def get_ingestion_status(
    ingestion_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get the current status of a WhatsApp ingestion."""
    ingestion = db.query(WhatsAppIngestion).filter(
        WhatsAppIngestion.id == ingestion_id
    ).first()

    if not ingestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingestion not found: {ingestion_id}",
        )

    return {
        "id": ingestion.id,
        "request_id": ingestion.request_id,
        "status": ingestion.status,
        "channel": ingestion.channel,
        "external_user_id": ingestion.external_user_id,
        "image_id": ingestion.image_id,
        "file_size": ingestion.file_size,
        "error_message": ingestion.error_message,
        "created_at": str(ingestion.created_at),
        "updated_at": str(ingestion.updated_at),
    }


@router.get("/webhook/health", summary="Meta webhook health check")
async def webhook_health() -> Dict[str, Any]:
    return {
        "status": "ready",
        "service": "meta-whatsapp-webhook",
        "verify_token_configured": bool(settings.META_VERIFY_TOKEN),
        "access_token_configured": bool(settings.META_WHATSAPP_TOKEN),
        "phone_number_id_configured": bool(settings.META_PHONE_NUMBER_ID),
        "app_secret_configured": bool(settings.META_APP_SECRET),
        "generation_enabled": bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY),
    }