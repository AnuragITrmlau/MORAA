"""Meta WhatsApp Cloud API webhook routes.

Implements Scenario 1 (Onboarding & Registration),
Scenario 2 (Zero-balance Wallet Gate),
Scenario 3 (Partial Order: e.g. ₹1000 balance for 3 uploaded images),
Dynamic Custom Recharges (>= ₹500), and AI Quality Guard.
"""

from typing import Any, Dict, List, Optional, Tuple
import asyncio
import json
import re
import traceback
import httpx

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, SessionLocal
from app.models.customer import Customer
from app.models.whatsapp_ingestion import WhatsAppIngestion
from app.repositories.base import BaseRepository
from app.services.image_quality_guard import validate_jewelry_image_with_gemini
from app.services.meta_whatsapp_service import (
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
from app.services.razorpay_service import create_recharge_payment_link
from app.services.upload_service import UploadService
from app.services.wallet_service import get_customer
from app.utils.logger import logger

router = APIRouter(prefix="/api/meta", tags=["Meta WhatsApp Webhook"])

DEFAULT_PAYMENT_URL = "https://rzp.io/l/moraa-recharge"
COST_PER_PRODUCT = 500


def _ordinal(n: int) -> str:
    """Helper for 1st, 2nd, 3rd, 4th."""
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"


def _find_customer_safe(db: Session, sender: str) -> Optional[Customer]:
    """Helper to find customer regardless of leading + or 91 country code differences."""
    clean_sender = sender.lstrip("+").strip()
    c = get_customer(db, clean_sender) or get_customer(db, sender)
    if not c and len(clean_sender) >= 10:
        c = db.query(Customer).filter(Customer.whatsapp_id.contains(clean_sender[-10:])).first()
    return c


# ─── Background Scenario 3 Delivery Worker ──────────────────────────────


async def process_partial_order_batch(
    sender: str,
    ingestion_ids: List[str],
    processed_count: int,
    unprocessed_count: int,
) -> None:
    total_images_in_packs = processed_count * 8

    for idx, ing_id in enumerate(ingestion_ids):
        is_last = (idx == len(ingestion_ids) - 1)
        pack_caption = (
            f"Here are your {total_images_in_packs} images across {processed_count} E-commerce Packs 📦✨\n"
            f"Remaining balance: ₹0"
            if is_last else ""
        )
        await process_whatsapp_generation(
            ingestion_id=ing_id,
            prompt_type="prompt_ecommerce",
            custom_caption=pack_caption,
            trigger_feedback=is_last,
        )
        await asyncio.sleep(1)

    if unprocessed_count > 0:
        unprocessed_idx = processed_count + 1
        ordinal_unprocessed = _ordinal(unprocessed_idx)

        try:
            recharge_url = await create_recharge_payment_link(
                customer_phone=sender,
                customer_name="Customer",
                amount=500,
            )
        except Exception:
            recharge_url = DEFAULT_PAYMENT_URL

        reminder_text = (
            f"To process your {ordinal_unprocessed} image, please make a "
            f"payment to continue ⚠️"
        )

        await asyncio.sleep(2)
        await send_whatsapp_cta_url_button(
            recipient_id=sender,
            body_text=reminder_text,
            button_label="Pay ₹500 to continue",
            url=recharge_url or DEFAULT_PAYMENT_URL,
        )


def _handle_button_reply(
    event: Dict[str, Any],
    db: Session,
) -> Optional[Tuple[str, str]]:
    button_reply = event.get("button_reply", {})
    button_id = button_reply.get("id", "")
    button_title = button_reply.get("title", "")
    sender = event.get("sender", "")
    message_id = event.get("message_id", "")

    if not button_id:
        return None

    parts = button_id.split(":", 1)
    if len(parts) != 2:
        return None

    prompt_type = parts[0]
    ingestion_id = parts[1]

    if not ingestion_id or prompt_type not in ("prompt_ecommerce", "prompt_close_up", "prompt_ugc"):
        return None

    try:
        ingestion_repo = BaseRepository(WhatsAppIngestion, db)
        existing = ingestion_repo.find_first(id=ingestion_id)
        if not existing or not existing.image_id:
            return None
    except Exception as e:
        logger.error(f"Button reply ingestion lookup failed: {e}")
        db.rollback()
        return None

    return prompt_type, ingestion_id


# ─── GET — Webhook Verification ──────────────────────────────────────────


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


# ─── POST — Webhook Event Receiver ───────────────────────────────────────


@router.post("/webhook", summary="Receive WhatsApp webhook events")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook JSON payload: {e}")
        return {"status": "error", "message": "Invalid JSON payload"}

    if settings.META_APP_SECRET:
        signature = request.headers.get("X-Hub-Signature-256")
        raw_body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        if not verify_webhook_signature(raw_body_bytes, signature):
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

            # ── Text messages ──
            if event_type == "text":
                sender = event.get("sender", "")
                raw_text = event.get("body", "").strip()
                lower_text = raw_text.lower()
                logger.info(f"Text message received: sender={sender} text='{raw_text}'")

                # PRIORITY 1: Registration Form Check (MUST BE CHECKED FIRST)
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
                    
                    if not cust:
                        cust = Customer(
                            whatsapp_id=clean_sender,
                            full_name=user_name,
                            business_name=biz_name,
                            gst_number=gst_val,
                            address=addr_val,
                            wallet_balance=0,
                            is_registered=True,
                        )
                        db.add(cust)
                    else:
                        cust.full_name = user_name
                        cust.business_name = biz_name
                        cust.gst_number = gst_val
                        cust.address = addr_val
                        cust.is_registered = True

                    db.commit()

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
                    except Exception:
                        pay_url = DEFAULT_PAYMENT_URL

                    await send_whatsapp_cta_url_button(
                        recipient_id=sender,
                        body_text=confirm_msg,
                        button_label="Recharge to use",
                        url=pay_url or DEFAULT_PAYMENT_URL,
                    )
                    continue

                # PRIORITY 2: Standalone Greetings (Exact whole words via \b)
                if re.search(r"\b(hi|hii|hello|hey|start)\b", lower_text):
                    msg_part_1 = (
                        "Hi there! Welcome to Moraa Studio ✨\n"
                        "We help you turn raw jewelry photos into polished, e-commerce ready images — powered by AI 💎"
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

                # PRIORITY 3: Custom Recharge Command (>= ₹500)
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
                    except Exception:
                        pay_url = DEFAULT_PAYMENT_URL

                    await send_whatsapp_cta_url_button(
                        recipient_id=sender,
                        body_text=f"Here is your recharge link for ₹{requested_amount} 💳\nTap below to complete the payment.",
                        button_label=f"Pay ₹{requested_amount}"[:20],
                        url=pay_url or DEFAULT_PAYMENT_URL,
                    )
                    continue

                continue

            # ── Interactive button replies ──
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

                button_selection = _handle_button_reply(event, db)
                if button_selection:
                    prompt_type, ingestion_id = button_selection
                    background_tasks.add_task(
                        process_whatsapp_generation,
                        ingestion_id,
                        prompt_type,
                    )
                continue

            if event_type in ("interactive", "unsupported"):
                continue

            # ── Collect images ──
            if event_type == "image":
                image_events.append(event)

    if not image_events:
        return {"status": "ok", "images_processed": 0}

    sender = image_events[0].get("sender", "")
    customer = _find_customer_safe(db, sender)
    current_balance = customer.wallet_balance if customer else 0
    total_images = len(image_events)

    logger.info(f"Image received from {sender}. DB Balance: ₹{current_balance}")

    # Scenario 2: Zero Balance Wallet Gate
    if current_balance <= 0:
        cust_name = getattr(customer, "full_name", "Customer") if customer else "Customer"
        try:
            pay_url = await create_recharge_payment_link(
                customer_phone=sender,
                customer_name=cust_name,
                amount=500,
            )
        except Exception:
            pay_url = DEFAULT_PAYMENT_URL

        zero_balance_msg = (
            "Your current balance is ₹0 ⚠️\n"
            "Please make a payment to continue."
        )
        await send_whatsapp_cta_url_button(
            recipient_id=sender,
            body_text=zero_balance_msg,
            button_label="Pay ₹500",
            url=pay_url or DEFAULT_PAYMENT_URL,
        )
        return {"status": "held_zero_balance"}

    # Scenario 3: Partial Order Calculation
    allowed_count = current_balance // COST_PER_PRODUCT
    is_partial = (total_images > allowed_count and allowed_count > 0)

    if is_partial:
        unprocessed_idx = allowed_count + 1
        ordinal_unprocessed = _ordinal(unprocessed_idx)

        msg_partial_breakdown = (
            f"Your balance is ₹{current_balance:,} — enough for {allowed_count} of "
            f"these {total_images} images (₹{COST_PER_PRODUCT} each) 💰\n"
            f"We’ll process {allowed_count} now, and you’ll need to recharge for the {ordinal_unprocessed}."
        )
        await send_whatsapp_text(sender, msg_partial_breakdown)
        await asyncio.sleep(1)

        msg_processing_now = (
            f"Processing your {allowed_count} images now ✅\n"
            f"Ready in 2-3 minutes ⏳"
        )
        await send_whatsapp_text(sender, msg_processing_now)

    images_to_process = image_events[:allowed_count] if is_partial else image_events
    processed_ingestion_ids: List[str] = []

    for img_ev in images_to_process:
        message_id = img_ev.get("message_id", "")
        media_id = img_ev.get("media_id", "")
        mime_type = img_ev.get("mime_type", "")
        caption = img_ev.get("caption", "")
        timestamp = img_ev.get("timestamp", "")

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
            reject_text = f"Photo quality check ⚠️\n\n{tip_msg}\n\nPlease snap a new photo and upload again!"
            await send_whatsapp_text(sender, reject_text)
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
            status="stored",
        )
        db.commit()

        # Deduct wallet per processed item
        if customer and customer.wallet_balance >= COST_PER_PRODUCT:
            customer.wallet_balance -= COST_PER_PRODUCT
            db.commit()

        processed_ingestion_ids.append(ingestion.id)

        if not is_partial:
            send_ok = await send_prompt_selection_buttons(recipient_id=sender, ingestion_id=ingestion.id)
            if send_ok:
                ingestion.status = "awaiting_selection"
                db.commit()

    if is_partial and processed_ingestion_ids:
        background_tasks.add_task(
            process_partial_order_batch,
            sender=sender,
            ingestion_ids=processed_ingestion_ids,
            processed_count=allowed_count,
            unprocessed_count=total_images - allowed_count,
        )

    return {"status": "ok", "queued": len(processed_ingestion_ids)}


# ─── GET — Health Check ──────────────────────────────────────────────────


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