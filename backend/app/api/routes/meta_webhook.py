"""Meta WhatsApp Cloud API webhook routes.

Strict Concurrency Lock:
- Only 1 image processes per batch/window.
- Extra concurrent images immediately receive a quoted recharge warning.
- No background queue leaks for secondary images.
"""

from typing import Any, Dict, List, Optional, Tuple
import asyncio
import json
import re
import time
import httpx

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import update

from app.config import settings
from app.database import get_db, SessionLocal
from app.models.customer import Customer
from app.models.whatsapp_ingestion import WhatsAppIngestion
from app.repositories.base import BaseRepository
from app.services.image_quality_guard import validate_jewelry_image_with_gemini
from app.services.meta_whatsapp_service import (
    CATALOG_PACK_ACK_TEMPLATE,
    download_media,
    get_media_url,
    parse_webhook_entry,
    process_whatsapp_generation,
    send_feedback_buttons,
    send_prompt_selection_buttons,
    send_whatsapp_cta_url_button,
    send_whatsapp_text,
    validate_image,
    verify_webhook_signature,
)
from app.tasks.whatsapp_generation_tasks import process_whatsapp_7_pack_task
from app.services.razorpay_service import create_recharge_payment_link
from app.services.onboarding_service import get_or_create_customer
from app.services.upload_service import UploadService
from app.services.wallet_service import get_customer
from app.utils.logger import logger

router = APIRouter(prefix="/api/meta", tags=["Meta WhatsApp Webhook"])

DEFAULT_PAYMENT_URL = "https://rzp.io/rzp/FbuLh9je"
COST_PER_PRODUCT = 500

# In-memory concurrency guard to absorb rapid multi-image webhook hits (5 second window)
_USER_IMAGE_LOCKS: Dict[str, float] = {}


def _find_customer_safe(db: Session, sender: str) -> Optional[Customer]:
    """Helper to find customer regardless of leading + or 91 country code differences."""
    clean_sender = sender.lstrip("+").strip()
    c = get_customer(db, clean_sender) or get_customer(db, sender)
    if not c and len(clean_sender) >= 10:
        c = db.query(Customer).filter(Customer.whatsapp_id.contains(clean_sender[-10:])).first()
    return c


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
                        cust, _created = get_or_create_customer(
                            db,
                            clean_sender,
                            defaults={
                                "full_name": user_name,
                                "business_name": biz_name,
                                "gst_number": gst_val,
                                "address": addr_val,
                                "wallet_balance": 0,
                                "is_registered": True,
                            },
                            update_fields=[
                                "full_name",
                                "business_name",
                                "gst_number",
                                "address",
                            ],
                        )

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
    clean_sender = sender.lstrip("+").strip()
    customer = _find_customer_safe(db, sender)
    now = time.time()

    # ── CONCURRENCY & BATCH FILTER ──
    # Check if this sender already triggered an image processing in the last 4 seconds
    last_processed_time = _USER_IMAGE_LOCKS.get(clean_sender, 0)
    is_concurrency_blocked = (now - last_processed_time) < 4.0

    processed_ingestion_ids: List[str] = []

    for idx, img_ev in enumerate(image_events):
        message_id = img_ev.get("message_id", "")
        media_id = img_ev.get("media_id", "")
        mime_type = img_ev.get("mime_type", "")
        caption = img_ev.get("caption", "")
        timestamp = img_ev.get("timestamp", "")

        # Row update: atomicity check
        phone_match = clean_sender[-10:] if len(clean_sender) >= 10 else clean_sender
        
        # Agar ye concurrency window ke andar doosri/teesri image hai ya idx > 0 hai
        if is_concurrency_blocked or idx > 0:
            warning_text = (
                "⚠️ Your balance is ₹0 for this image.\n\n"
                "₹500 required to generate photos for this design.\n"
                f"Tap to recharge: {DEFAULT_PAYMENT_URL}"
            )
            # Seedhe quote karke WhatsApp text bhejo (100% delivered)
            await send_whatsapp_text(
                recipient_id=sender,
                message_text=warning_text,
                reply_to_message_id=message_id,
            )
            continue

        # Check & Deduct from DB atomically
        result = db.execute(
            update(Customer)
            .where(
                Customer.whatsapp_id.contains(phone_match),
                Customer.wallet_balance >= COST_PER_PRODUCT,
            )
            .values(wallet_balance=Customer.wallet_balance - COST_PER_PRODUCT)
        )
        db.commit()

        # Balance nahi tha (0 balance)
        if result.rowcount == 0:
            warning_text = (
                "⚠️ Your balance is ₹0 for this image.\n\n"
                "₹500 required to generate photos for this design.\n"
                f"Tap to recharge: {DEFAULT_PAYMENT_URL}"
            )
            await send_whatsapp_text(
                recipient_id=sender,
                message_text=warning_text,
                reply_to_message_id=message_id,
            )
            continue

        # Set concurrency lock: image A ne slot le liya
        _USER_IMAGE_LOCKS[clean_sender] = now
        is_concurrency_blocked = True

        existing = ingestion_repo.find_first(external_message_id=message_id)
        if existing:
            continue

        media_url = await get_media_url(media_id)
        if not media_url:
            continue

        download_result = await download_media(media_url)
        if not download_result:
            continue

        image_bytes, content_type = download_result
        is_valid, _ = validate_image(image_bytes, content_type)
        if not is_valid:
            continue

        # AI Quality Guard
        ai_valid, tip_msg = await validate_jewelry_image_with_gemini(image_bytes, content_type)
        if not ai_valid:
            # Refund
            db.execute(
                update(Customer)
                .where(Customer.whatsapp_id.contains(phone_match))
                .values(wallet_balance=Customer.wallet_balance + COST_PER_PRODUCT)
            )
            db.commit()
            reject_text = f"Photo quality check ⚠️\n\n{tip_msg}\n\nPlease snap a new photo and upload again!"
            await send_whatsapp_text(sender, reject_text, reply_to_message_id=message_id)
            continue

        ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
        ext = ext_map.get(content_type, "jpg")
        filename = f"whatsapp_{message_id[:20]}.{ext}"

        upload_service = UploadService(db)
        upload_result = await upload_service.process_upload(
            file_data=image_bytes,
            filename=filename,
            file_size=len(image_bytes),
            mime_type=content_type,
        )

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

        # Quoted ACK strictly on Image A
        await send_whatsapp_text(sender, CATALOG_PACK_ACK_TEMPLATE, reply_to_message_id=message_id)

        # Trigger generation for Image A only
        process_whatsapp_7_pack_task.delay(ingestion.id)

    return {
        "status": "ok",
        "queued": len(processed_ingestion_ids),
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