"""Meta WhatsApp Cloud API webhook routes.

Implements the official WhatsApp webhook verification and event reception
endpoints. Ingests incoming WhatsApp images and forwards to AI generation.
"""

from typing import Any, Dict, List, Optional, Tuple
import asyncio
import json
import traceback
import httpx

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.whatsapp_ingestion import WhatsAppIngestion
from app.repositories.base import BaseRepository
from app.services.meta_whatsapp_service import (
    download_media,
    get_media_url,
    parse_webhook_entry,
    process_whatsapp_generation,
    send_prompt_selection_buttons,
    send_whatsapp_cta_url_button,
    send_whatsapp_text,
    validate_image,
    verify_webhook_signature,
)
from app.services.upload_service import UploadService
from app.utils.logger import logger

router = APIRouter(prefix="/api/meta", tags=["Meta WhatsApp Webhook"])

# Default recharge payment link (Update with your live Razorpay / payment link)
DEFAULT_PAYMENT_URL = "https://rzp.io/l/moraa-recharge"


# ─── Direct WhatsApp Message Sender Helper ──────────────────────────────


async def send_direct_whatsapp_text(recipient_id: str, message_text: str) -> bool:
    """Sends a direct WhatsApp text message using Meta Cloud API."""
    return await send_whatsapp_text(recipient_id, message_text)


# ─── Background generation trigger ──────────────────────────────────────


async def _trigger_generation(ingestion_id: str) -> None:
    """Background task that triggers GemVision generation for a stored ingestion."""
    try:
        success = await process_whatsapp_generation(ingestion_id)
        if success:
            logger.info(f"Background generation completed: ingestion_id={ingestion_id}")
        else:
            logger.warning(f"Background generation failed: ingestion_id={ingestion_id}")
    except Exception as e:
        logger.error(f"Background generation exception: ingestion_id={ingestion_id} error={e}")


def _handle_button_reply(
    event: Dict[str, Any],
    db: Session,
) -> Optional[Tuple[str, str]]:
    """Handle an interactive button_reply event."""
    button_reply = event.get("button_reply", {})
    button_id = button_reply.get("id", "")
    button_title = button_reply.get("title", "")
    sender = event.get("sender", "")
    message_id = event.get("message_id", "")

    if not button_id:
        logger.warning(f"Button reply missing id: sender={sender} message_id={message_id[:20]}...")
        return None

    parts = button_id.split(":", 1)
    if len(parts) != 2:
        logger.warning(f"Invalid button_reply.id format: id={button_id}")
        return None

    prompt_type = parts[0]
    ingestion_id = parts[1]

    if not ingestion_id:
        logger.warning(f"Empty ingestion_id in button_reply.id: id={button_id}")
        return None

    if prompt_type not in ("prompt_ecommerce", "prompt_close_up", "prompt_ugc"):
        logger.warning(f"Unknown prompt type in button_reply: type={prompt_type}")
        return None

    logger.info(
        f"Button reply received: sender={sender} button='{button_title}' prompt_type={prompt_type} ingestion_id={ingestion_id}"
    )

    try:
        ingestion_repo = BaseRepository(WhatsAppIngestion, db)
        existing = ingestion_repo.find_first(id=ingestion_id)
        if not existing or not existing.image_id:
            logger.warning(f"Button reply references invalid ingestion: {ingestion_id}")
            return None
    except Exception as e:
        logger.error(f"Button reply ingestion lookup failed: {e}")
        db.rollback()
        return None

    return prompt_type, ingestion_id


# ─── GET — Webhook Verification ──────────────────────────────────────────


@router.get(
    "/webhook",
    summary="Meta webhook verification",
)
async def verify_webhook(
    hub_mode: Optional[str] = None,
    hub_verify_token: Optional[str] = None,
    hub_challenge: Optional[str] = None,
) -> PlainTextResponse:
    """Verify webhook ownership with Meta."""
    if hub_mode != "subscribe" or not hub_verify_token or hub_verify_token != settings.META_VERIFY_TOKEN:
        logger.warning("Webhook verification token mismatch")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid verification token or mode",
        )

    if not hub_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing challenge parameter",
        )

    logger.info("Webhook verification successful")
    return PlainTextResponse(content=hub_challenge)


# ─── POST — Webhook Event Receiver ───────────────────────────────────────


@router.post(
    "/webhook",
    summary="Receive WhatsApp webhook events",
)
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Receive and process WhatsApp webhook events safely without body-stream locks."""

    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook JSON payload: {e}")
        return {"status": "error", "message": "Invalid JSON payload"}

    if settings.META_APP_SECRET:
        signature = request.headers.get("X-Hub-Signature-256")
        raw_body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        if not verify_webhook_signature(raw_body_bytes, signature):
            logger.warning("Webhook signature verification failed")
            return {"status": "error", "message": "Invalid signature"}

    if payload.get("object") == "whatsapp_business_account" and "entry" not in payload:
        return {"status": "ok"}

    if payload.get("object") != "whatsapp_business_account":
        return {"status": "ignored", "message": "Not a WhatsApp business account event"}

    entries = payload.get("entry", [])
    if not entries:
        return {"status": "ignored", "message": "No entries in webhook payload"}

    ingestion_repo = BaseRepository(WhatsAppIngestion, db)
    image_count = 0
    stored_count = 0
    button_sent_count = 0
    button_reply_count = 0
    skipped_count = 0
    onboarding_handled_count = 0

    for entry in entries:
        events = parse_webhook_entry(entry)

        for event in events:
            event_type = event.get("type", "")

            # ── Status events ──────────────────────────────────────────
            if event_type == "status":
                continue

            # ── Text messages (Scenario 1: Welcome & Registration) ────
            if event_type == "text":
                sender = event.get("sender", "")
                raw_text = event.get("body", "").strip()
                lower_text = raw_text.lower()
                logger.info(f"Text message received: sender={sender} text='{raw_text}'")

                # Check 1: Greeting triggers two sequential bubbles
                if any(greet in lower_text for greet in ["hi", "hii", "hello", "hey", "start"]):
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

                    ok_1 = await send_whatsapp_text(sender, msg_part_1)
                    await asyncio.sleep(1)
                    ok_2 = await send_whatsapp_text(sender, msg_part_2)

                    if ok_1 or ok_2:
                        onboarding_handled_count += 1
                    continue

                # Check 2: Filled Registration Details Received -> Confirm + Payment CTA
                if "name:" in lower_text and "business" in lower_text:
                    user_name = "there"
                    for line in raw_text.splitlines():
                        if line.lower().startswith("name:"):
                            extracted = line.split(":", 1)[1].strip()
                            if extracted:
                                user_name = extracted.split()[0]
                            break

                    confirm_msg = (
                        f"Congratulations {user_name}! You’re registered with Moraa Studio 🎉\n"
                        f"You’re all set to start creating stunning product photos."
                    )

                    # Send CTA URL button for recharging (Scenario 1)
                    cta_sent = await send_whatsapp_cta_url_button(
                        recipient_id=sender,
                        body_text=confirm_msg,
                        button_label="Recharge to use",
                        url=DEFAULT_PAYMENT_URL,
                    )

                    # Fallback to plain text if CTA fails
                    if not cta_sent:
                        fallback_msg = (
                            f"{confirm_msg}\n\n"
                            f"Current balance: ₹0 ⚠️\n"
                            f"Recharge ₹500 to get started: {DEFAULT_PAYMENT_URL}"
                        )
                        await send_whatsapp_text(sender, fallback_msg)

                    onboarding_handled_count += 1
                    continue

                continue

            # ── Interactive button replies ─────────────────────────────
            if event_type == "interactive" and event.get("subtype") == "button_reply":
                button_reply_count += 1
                button_selection = _handle_button_reply(event, db)
                if button_selection:
                    prompt_type, ingestion_id = button_selection
                    background_tasks.add_task(
                        process_whatsapp_generation,
                        ingestion_id,
                        prompt_type,
                    )
                    logger.info(
                        f"Generation queued via background task: ingestion_id={ingestion_id} prompt_type={prompt_type}"
                    )
                continue

            # ── Unsupported events ─────────────────────────────────────
            if event_type in ("interactive", "unsupported"):
                continue

            # ── Image messages ─────────────────────────────────────────
            if event_type != "image":
                continue

            image_count += 1
            message_id = event.get("message_id", "")
            sender = event.get("sender", "")
            media_id = event.get("media_id", "")
            mime_type = event.get("mime_type", "")
            caption = event.get("caption", "")
            timestamp = event.get("timestamp", "")

            # ── Scenario 2: Zero Balance Wallet Gate (Configurable) ───
            # Set ENABLE_WALLET_GATE=True in .env to enforce payment before generation
            wallet_gate_active = getattr(settings, "ENABLE_WALLET_GATE", False)
            if wallet_gate_active:
                zero_balance_msg = (
                    "Your current balance is ₹0 ⚠️\n"
                    "Please make a payment to continue."
                )
                sent_gate = await send_whatsapp_cta_url_button(
                    recipient_id=sender,
                    body_text=zero_balance_msg,
                    button_label="Pay ₹500",
                    url=DEFAULT_PAYMENT_URL,
                )
                if not sent_gate:
                    await send_whatsapp_text(
                        sender,
                        f"{zero_balance_msg}\n\nPay ₹500 here: {DEFAULT_PAYMENT_URL}",
                    )
                logger.info(f"Wallet gate held image for user={sender} (balance=0)")
                continue

            # Idempotency check
            try:
                existing = ingestion_repo.find_first(external_message_id=message_id)
                if existing:
                    skipped_count += 1
                    continue
            except Exception as e:
                logger.error(f"Idempotency check query failed: {e}")
                db.rollback()

            if not media_id:
                continue

            try:
                media_url = await get_media_url(media_id)
            except Exception as e:
                logger.error(f"Exception calling get_media_url: {e}")
                media_url = None

            if not media_url:
                continue

            try:
                download_result = await download_media(media_url)
            except Exception as e:
                logger.error(f"Exception downloading media: {e}")
                download_result = None

            if not download_result:
                continue

            image_bytes, content_type = download_result

            is_valid, error_msg = validate_image(image_bytes, content_type)
            if not is_valid:
                continue

            try:
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
                stored_count += 1

                send_ok = await send_prompt_selection_buttons(
                    recipient_id=sender,
                    ingestion_id=ingestion.id,
                )
                if send_ok:
                    button_sent_count += 1
                    ingestion.status = "awaiting_selection"
                    db.commit()

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to store WhatsApp image: {e}")

    logger.info(
        f"Webhook batch processed: images={image_count} stored={stored_count} "
        f"buttons_sent={button_sent_count} button_replies={button_reply_count} "
        f"skipped={skipped_count} onboarding_handled={onboarding_handled_count}"
    )

    return {
        "status": "ok",
        "images_received": image_count,
        "images_stored": stored_count,
        "buttons_sent": button_sent_count,
        "button_replies_handled": button_reply_count,
        "duplicates_skipped": skipped_count,
        "onboarding_handled": onboarding_handled_count,
    }


# ─── GET — Health Check ──────────────────────────────────────────────────


@router.get(
    "/webhook/health",
    summary="Meta webhook health check",
)
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