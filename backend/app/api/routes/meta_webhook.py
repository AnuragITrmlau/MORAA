"""Meta WhatsApp Cloud API webhook routes.

Implements the official WhatsApp webhook verification and event reception
endpoints. Ingests incoming WhatsApp images and forwards to AI generation.
"""

from typing import Any, Dict, List, Optional
import json
import traceback

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
    validate_image,
    verify_webhook_signature,
)
from app.services.upload_service import UploadService
from app.utils.logger import logger

router = APIRouter(prefix="/api/meta", tags=["Meta WhatsApp Webhook"])


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


# ─── GET — Webhook Verification ──────────────────────────────────────────


@router.get(
    "/webhook",
    summary="Meta webhook verification",
    description=(
        "Handles Meta's webhook verification challenge. "
        "Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge. "
        "If the verify_token matches, the challenge is returned."
    ),
)
async def verify_webhook(
    hub_mode: Optional[str] = None,
    hub_verify_token: Optional[str] = None,
    hub_challenge: Optional[str] = None,
) -> PlainTextResponse:
    """Verify webhook ownership with Meta."""
    logger.info(
        f"Webhook verification request: mode={hub_mode} "
        f"token_provided={bool(hub_verify_token)} challenge_provided={bool(hub_challenge)}"
    )

    if hub_mode != "subscribe":
        logger.warning(f"Invalid webhook mode: {hub_mode}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid verification mode",
        )

    if not hub_verify_token or hub_verify_token != settings.META_VERIFY_TOKEN:
        logger.warning("Webhook verification token mismatch")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid verification token",
        )

    if not hub_challenge:
        logger.warning("Webhook verification request missing challenge")
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
    description=(
        "Receives inbound WhatsApp events from Meta. "
        "Image messages are ingested and stored. Other events are acknowledged. "
        "Returns 200 OK immediately after safe acceptance."
    ),
)
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Receive and process WhatsApp webhook events safely without body-stream locks."""

    # ── Read JSON body safely ──────────────────────────────────────────
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook JSON payload: {e}")
        return {"status": "error", "message": "Invalid JSON payload"}

    # ── Optional Signature Verification (Only if App Secret is set) ───
    if settings.META_APP_SECRET:
        signature = request.headers.get("X-Hub-Signature-256")
        raw_body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        if not verify_webhook_signature(raw_body_bytes, signature):
            logger.warning("Webhook signature verification failed")
            return {"status": "error", "message": "Invalid signature"}

    # ── Handle verification probe ──────────────────────────────────────
    if payload.get("object") == "whatsapp_business_account" and "entry" not in payload:
        return {"status": "ok"}

    # ── Validate payload structure ─────────────────────────────────────
    if payload.get("object") != "whatsapp_business_account":
        logger.warning(f"Unexpected webhook object type: {payload.get('object')}")
        return {"status": "ignored", "message": "Not a WhatsApp business account event"}

    entries = payload.get("entry", [])
    if not entries:
        return {"status": "ignored", "message": "No entries in webhook payload"}

    # ── Process each entry ─────────────────────────────────────────────
    ingestion_repo = BaseRepository(WhatsAppIngestion, db)
    image_count = 0
    processed_count = 0
    skipped_count = 0

    for entry in entries:
        events = parse_webhook_entry(entry)

        for event in events:
            event_type = event.get("type", "")

            if event_type == "status":
                logger.info(
                    f"Status event: message_id={event.get('message_id', '')[:20]} "
                    f"status={event.get('status', '')}"
                )
                continue

            if event_type == "text":
                logger.info(
                    f"Text message received: sender={event.get('sender', '')} "
                    f"body_len={len(event.get('body', ''))}"
                )
                continue

            if event_type == "unsupported":
                logger.info(
                    f"Unsupported event type: raw_type={event.get('raw_type', '')} "
                    f"sender={event.get('sender', '')}"
                )
                continue

            if event_type != "image":
                continue

            image_count += 1
            message_id = event.get("message_id", "")
            sender = event.get("sender", "")
            media_id = event.get("media_id", "")
            mime_type = event.get("mime_type", "")
            caption = event.get("caption", "")
            timestamp = event.get("timestamp", "")

            logger.info(
                f"Image message received: sender={sender} "
                f"message_id={message_id[:20]}... media_id={media_id[:20]}..."
            )

            # ── Idempotency check ─────────────────────────────────────
            try:
                existing = ingestion_repo.find_first(external_message_id=message_id)
                if existing:
                    logger.info(
                        f"Duplicate webhook event — already processed: "
                        f"message_id={message_id[:20]}... "
                        f"existing_status={existing.status}"
                    )
                    skipped_count += 1
                    continue
            except Exception as e:
                logger.error(f"Idempotency check query failed: {e}")
                db.rollback()

            # ── Retrieve media URL from Meta API ───────────────────────
            if not media_id:
                logger.warning(f"Image message missing media_id: message_id={message_id[:20]}...")
                try:
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
                except Exception as e:
                    db.rollback()
                    logger.error(f"Failed to record missing media_id state: {e}")
                continue

            try:
                media_url = await get_media_url(media_id)
            except Exception as e:
                logger.error(f"Exception calling get_media_url: {e}\n{traceback.format_exc()}")
                media_url = None

            if not media_url:
                logger.error(f"CRITICAL: Failed to get media URL for media_id={media_id}. Check META_WHATSAPP_TOKEN validity.")
                try:
                    ingestion_repo.create(
                        external_user_id=sender,
                        external_message_id=message_id,
                        external_media_id=media_id,
                        channel="whatsapp",
                        caption=caption,
                        mime_type=mime_type,
                        timestamp=timestamp,
                        status="failed",
                        error_message="Failed to retrieve media URL from Meta API (Check Token)",
                    )
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error(f"Failed to record media URL failure state: {e}")
                continue

            # ── Download image ─────────────────────────────────────────
            try:
                download_result = await download_media(media_url)
            except Exception as e:
                logger.error(f"Exception downloading media from {media_url}: {e}\n{traceback.format_exc()}")
                download_result = None

            if not download_result:
                logger.error(f"CRITICAL: Failed to download media binary from URL: {media_url}")
                try:
                    ingestion_repo.create(
                        external_user_id=sender,
                        external_message_id=message_id,
                        external_media_id=media_id,
                        channel="whatsapp",
                        caption=caption,
                        mime_type=mime_type,
                        timestamp=timestamp,
                        status="failed",
                        error_message="Failed to download media from Meta",
                    )
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error(f"Failed to record download failure state: {e}")
                continue

            image_bytes, content_type = download_result

            # ── Validate image ─────────────────────────────────────────
            is_valid, error_msg = validate_image(image_bytes, content_type)
            if not is_valid:
                logger.warning(
                    f"Image validation failed: {error_msg} "
                    f"sender={sender} message_id={message_id[:20]}..."
                )
                try:
                    ingestion_repo.create(
                        external_user_id=sender,
                        external_message_id=message_id,
                        external_media_id=media_id,
                        channel="whatsapp",
                        caption=caption,
                        mime_type=content_type,
                        timestamp=timestamp,
                        file_size=len(image_bytes),
                        status="failed",
                        error_message=error_msg,
                    )
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error(f"Failed to record validation failure state: {e}")
                continue

            # ── Store using existing UploadService ─────────────────────
            try:
                ext_map = {
                    "image/jpeg": "jpg",
                    "image/png": "png",
                    "image/webp": "webp",
                }
                ext = ext_map.get(content_type, "jpg")
                filename = f"whatsapp_{message_id[:20]}.{ext}"

                upload_service = UploadService(db)
                upload_result = await upload_service.process_upload(
                    file_data=image_bytes,
                    filename=filename,
                    file_size=len(image_bytes),
                    mime_type=content_type,
                )

                # ── Create ingestion record ────────────────────────────
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

                processed_count += 1
                logger.info(
                    f"WhatsApp image ingested successfully: "
                    f"ingestion_id={ingestion.id} "
                    f"request_id={ingestion.request_id} "
                    f"image_id={upload_result.id} "
                    f"sender={sender} "
                    f"file_size={len(image_bytes)} bytes"
                )

                # ── Trigger existing GemVision generation ──────────────
                background_tasks.add_task(
                    _trigger_generation,
                    ingestion.id,
                )

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to store WhatsApp image: {e}\n{traceback.format_exc()}")
                try:
                    ingestion_repo.create(
                        external_user_id=sender,
                        external_message_id=message_id,
                        external_media_id=media_id,
                        channel="whatsapp",
                        caption=caption,
                        mime_type=content_type,
                        timestamp=timestamp,
                        file_size=len(image_bytes),
                        status="failed",
                        error_message=f"Storage failure: {str(e)}",
                    )
                    db.commit()
                except Exception as inner_e:
                    db.rollback()
                    logger.error(f"Failed to log ingestion failure record: {inner_e}")

    logger.info(
        f"Webhook batch processed: images={image_count} "
        f"stored={processed_count} skipped={skipped_count}"
    )

    return {
        "status": "ok",
        "images_received": image_count,
        "images_stored": processed_count,
        "duplicates_skipped": skipped_count,
    }


# ─── GET — Health Check ──────────────────────────────────────────────────


@router.get(
    "/webhook/health",
    summary="Meta webhook health check",
)
async def webhook_health() -> Dict[str, Any]:
    """Check if the Meta webhook endpoint is ready."""
    return {
        "status": "ready",
        "service": "meta-whatsapp-webhook",
        "verify_token_configured": bool(settings.META_VERIFY_TOKEN),
        "access_token_configured": bool(settings.META_WHATSAPP_TOKEN),
        "phone_number_id_configured": bool(settings.META_PHONE_NUMBER_ID),
        "app_secret_configured": bool(settings.META_APP_SECRET),
        "generation_enabled": bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY),
    }


# ─── POST — Manual Retry (delivery failures) ────────────────────────────


@router.post(
    "/webhook/retry/{ingestion_id}",
    summary="Retry delivery for a failed ingestion",
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