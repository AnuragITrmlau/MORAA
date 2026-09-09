"""Meta WhatsApp Cloud API service — ingestion + generation + delivery.

Responsibilities:
    - Parse incoming Meta webhook payloads
    - Retrieve media from Meta's authenticated media API
    - Validate downloaded images
    - Store images using existing GemVision UploadService
    - Create WhatsAppIngestion records for traceability
    - Trigger existing GemVision generation pipeline
    - Upload generated images to Meta media API
    - Send generated images back to WhatsApp users
"""

import hashlib
import io
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.config import settings
from app.utils.logger import logger

# ─── Constants ────────────────────────────────────────────────────────────

META_MEDIA_URL_TEMPLATE = "https://graph.facebook.com/v21.0/{media_id}"
META_SEND_MESSAGE_URL = "https://graph.facebook.com/v21.0/{phone_number_id}/messages"
META_MEDIA_UPLOAD_URL = "https://graph.facebook.com/v21.0/{phone_number_id}/media"

SUPPORTED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp"}


# ─── Webhook payload parsing ─────────────────────────────────────────────


def parse_webhook_entry(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse a single Meta webhook entry into a list of normalised change events."""
    events: List[Dict[str, Any]] = []

    changes = entry.get("changes", [])
    for change in changes:
        value = change.get("value", {})

        statuses = value.get("statuses", [])
        if statuses:
            for status in statuses:
                events.append({
                    "type": "status",
                    "message_id": status.get("id", ""),
                    "status": status.get("status", ""),
                    "timestamp": status.get("timestamp", ""),
                })
            continue

        messages = value.get("messages", [])
        for message in messages:
            msg_type = message.get("type", "")
            msg_id = message.get("id", "")
            sender = message.get("from", "")
            timestamp = message.get("timestamp", "")

            if msg_type == "image":
                image_data = message.get("image", {})
                events.append({
                    "type": "image",
                    "message_id": msg_id,
                    "sender": sender,
                    "timestamp": timestamp,
                    "media_id": image_data.get("id", ""),
                    "mime_type": image_data.get("mime_type", ""),
                    "caption": image_data.get("caption", ""),
                })
            elif msg_type == "text":
                text_data = message.get("text", {})
                events.append({
                    "type": "text",
                    "message_id": msg_id,
                    "sender": sender,
                    "timestamp": timestamp,
                    "body": text_data.get("body", ""),
                })
            elif msg_type == "interactive":
                interactive_data = message.get("interactive", {})
                interactive_type = interactive_data.get("type", "")
                button_reply = interactive_data.get("button_reply", {})

                if interactive_type == "button_reply":
                    events.append({
                        "type": "interactive",
                        "subtype": "button_reply",
                        "message_id": msg_id,
                        "sender": sender,
                        "timestamp": timestamp,
                        "button_reply": {
                            "id": button_reply.get("id", ""),
                            "title": button_reply.get("title", ""),
                        },
                    })
                else:
                    events.append({
                        "type": "unsupported",
                        "message_id": msg_id,
                        "sender": sender,
                        "timestamp": timestamp,
                        "raw_type": f"interactive:{interactive_type}",
                    })
            else:
                events.append({
                    "type": "unsupported",
                    "message_id": msg_id,
                    "sender": sender,
                    "timestamp": timestamp,
                    "raw_type": msg_type,
                })

    return events


# ─── Media retrieval ─────────────────────────────────────────────────────


async def get_media_url(media_id: str) -> Optional[str]:
    """Retrieve the temporary download URL for a Meta media ID."""
    if not settings.META_WHATSAPP_TOKEN:
        logger.error("META_WHATSAPP_TOKEN not configured — cannot retrieve media")
        return None

    url = META_MEDIA_URL_TEMPLATE.format(media_id=media_id)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}"},
            )

            if response.status_code != 200:
                logger.error(
                    f"Meta media metadata request failed: status={response.status_code} "
                    f"media_id={media_id[:20]}..."
                )
                return None

            data = response.json()
            media_url = data.get("url")
            if not media_url:
                logger.error(f"Meta media metadata response missing 'url' field: media_id={media_id[:20]}...")
                return None

            return media_url

    except httpx.TimeoutException:
        logger.error(f"Meta media metadata request timed out: media_id={media_id[:20]}...")
        return None
    except Exception as e:
        logger.error(f"Meta media metadata request failed: {e}")
        return None


async def download_media(media_url: str) -> Optional[Tuple[bytes, str]]:
    """Download media from Meta CDN using Bearer auth and redirect handling."""
    if not media_url:
        return None

    headers = {
        "Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}",
        "User-Agent": "curl/7.68.0",
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            response = await client.get(media_url, headers=headers)

            if response.status_code != 200:
                logger.error(
                    f"Media download failed: status={response.status_code} "
                    f"body={response.text[:200]}"
                )
                return None

            content_type = response.headers.get("content-type", "application/octet-stream")
            if ";" in content_type:
                content_type = content_type.split(";")[0].strip()

            image_bytes = response.content
            if len(image_bytes) == 0:
                logger.error("Downloaded media is empty (0 bytes)")
                return None

            return image_bytes, content_type

    except httpx.TimeoutException:
        logger.error("Media download timed out")
        return None
    except Exception as e:
        logger.error(f"Media download failed: {e}")
        return None


# ─── Image validation ────────────────────────────────────────────────────


def validate_image(
    image_bytes: bytes,
    content_type: str,
) -> Tuple[bool, Optional[str]]:
    """Validate downloaded image bytes before storage."""
    if len(image_bytes) == 0:
        return False, "Downloaded image is empty (0 bytes)"

    if len(image_bytes) > settings.META_MAX_MEDIA_BYTES:
        max_mb = settings.META_MAX_MEDIA_BYTES / (1024 * 1024)
        return False, f"Image too large: {len(image_bytes)} bytes (max {max_mb:.0f} MB)"

    normalized_ct = content_type.lower().split(";")[0].strip()
    if normalized_ct not in SUPPORTED_IMAGE_MIMES:
        return False, f"Unsupported image format: {content_type} (supported: {', '.join(sorted(SUPPORTED_IMAGE_MIMES))})"

    try:
        from PIL import Image as PILImage

        img = PILImage.open(io.BytesIO(image_bytes))
        img.verify()
        img = PILImage.open(io.BytesIO(image_bytes))
        w, h = img.size
        if w < 16 or h < 16:
            return False, f"Image too small: {w}x{h} (minimum 16x16)"
    except Exception as e:
        return False, f"Invalid image data: {e}"

    return True, None


# ─── Webhook signature verification ──────────────────────────────────────


def verify_webhook_signature(
    payload_body: bytes,
    signature_header: Optional[str],
) -> bool:
    """Verify Meta's X-Hub-Signature-256 HMAC-SHA256 signature."""
    if not settings.META_APP_SECRET:
        logger.info("META_APP_SECRET not configured — skipping webhook signature verification")
        return True

    if not signature_header:
        logger.warning("Webhook request missing X-Hub-Signature-256 header")
        return False

    import hmac

    expected_prefix = "sha256="
    if not signature_header.startswith(expected_prefix):
        logger.warning(f"Invalid signature format: {signature_header[:20]}...")
        return False

    signature_hash = signature_header[len(expected_prefix):]

    computed = hmac.new(
        settings.META_APP_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed, signature_hash):
        logger.warning("Webhook signature mismatch — possible tampering")
        return False

    return True


# ─── Interactive button message ─────────────────────────────────────────


async def send_prompt_selection_buttons(recipient_id: str, ingestion_id: str) -> bool:
    """Send an interactive button message to the user asking them to select a style.

    Button layout:
        Button 1: "Clean E-Commerce" (ID: "prompt_ecommerce:<ingestion_id>")
        Button 2: "Close-up on Ear" (ID: "prompt_close_up:<ingestion_id>")
        Button 3: "UGC Lifestyle"     (ID: "prompt_ugc:<ingestion_id>")
    """
    if not settings.META_WHATSAPP_TOKEN:
        logger.error("META_WHATSAPP_TOKEN not configured — cannot send button message")
        return False

    if not settings.META_PHONE_NUMBER_ID:
        logger.error("META_PHONE_NUMBER_ID not configured — cannot send button message")
        return False

    url = META_SEND_MESSAGE_URL.format(phone_number_id=settings.META_PHONE_NUMBER_ID)

    prompt_ecommerce_id = f"prompt_ecommerce:{ingestion_id}"
    prompt_close_up_id = f"prompt_close_up:{ingestion_id}"
    prompt_ugc_id = f"prompt_ugc:{ingestion_id}"

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": (
                    "Please select the style for your earring image:\n"
                    "• Clean E-Commerce — catalog product shot on neutral backdrop\n"
                    "• Close-up on Ear — macro close-up worn on a model's ear\n"
                    "• UGC Lifestyle — authentic customer-style lifestyle photo"
                ),
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": prompt_ecommerce_id,
                            "title": "Clean E-Commerce",
                        },
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": prompt_close_up_id,
                            "title": "Close-up on Ear",
                        },
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": prompt_ugc_id,
                            "title": "UGC Lifestyle",
                        },
                    },
                ],
            },
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if response.status_code != 200:
                logger.error(
                    f"Meta send button message failed: status={response.status_code}"
                )
                return False

            data = response.json()
            messages = data.get("messages", [])
            if not messages:
                logger.error(f"Meta send button message response missing 'messages': {data}")
                return False

            logger.info(
                f"Meta button message sent: recipient={recipient_id} "
                f"message_id={messages[0].get('id', '')} "
                f"ingestion_id={ingestion_id}"
            )
            return True

    except httpx.TimeoutException:
        logger.error("Meta send button message timed out")
        return False
    except Exception as e:
        logger.error(f"Meta send button message failed: {e}")
        return False


# ─── Generation trigger ──────────────────────────────────────────────────


async def process_whatsapp_generation(
    ingestion_id: str,
    prompt_type: str = "prompt_ecommerce",
) -> bool:
    """Trigger the existing GemVision generation pipeline for a WhatsApp ingestion.

    Args:
        ingestion_id: The WhatsAppIngestion record ID.
        prompt_type: One of "prompt_ecommerce", "prompt_close_up", or "prompt_ugc".
            Defaults to "prompt_ecommerce" for backward compatibility.
    """
    from app.database import SessionLocal
    from app.models.image import Image
    from app.models.whatsapp_ingestion import WhatsAppIngestion
    from app.services.earring_ecommerce_prompt import build_earring_ecommerce_prompt
    from app.services.earring_close_up_ears_prompt import build_close_up_ears_prompt
    from app.services.earring_ugc_style_prompt import build_ugc_style_prompt
    from app.ai.image_generation_manager import ImageGenerationManager

    db = SessionLocal()
    try:
        ingestion = db.query(WhatsAppIngestion).filter(
            WhatsAppIngestion.id == ingestion_id
        ).first()

        if not ingestion:
            logger.error(f"WhatsApp generation: ingestion not found: {ingestion_id}")
            return False

        # Only block in-flight runs: terminal/awaiting states (stored, failed,
        # awaiting_selection, generated, delivered, delivery_failed) may all
        # re-run so the user can pick a different style for the same image.
        if ingestion.status == "processing":
            logger.info(
                f"WhatsApp generation: skipping ingestion {ingestion_id} "
                f"(status={ingestion.status}) — already in progress"
            )
            return False

        ingestion.status = "processing"
        ingestion.error_message = None
        db.commit()

        logger.info(
            f"WhatsApp generation started: ingestion_id={ingestion_id} "
            f"request_id={ingestion.request_id} user={ingestion.external_user_id} "
            f"prompt_type={prompt_type}"
        )

        image_record = db.query(Image).filter(
            Image.id == ingestion.image_id
        ).first()

        if not image_record:
            _fail_ingestion(db, ingestion, "Image record not found")
            return False

        from pathlib import Path

        image_path = Path(image_record.file_path)
        if not image_path.exists():
            _fail_ingestion(db, ingestion, f"Image file not found: {image_path}")
            return False

        reference_image_bytes = image_path.read_bytes()
        if len(reference_image_bytes) == 0:
            _fail_ingestion(db, ingestion, "Image file is empty")
            return False

        logger.info(
            f"WhatsApp generation: read image file "
            f"{len(reference_image_bytes)} bytes from {image_path}"
        )

        # ── Route to the correct prompt builder based on prompt_type ───
        if prompt_type == "prompt_ecommerce":
            prompt = build_earring_ecommerce_prompt()
            logger.info(
                f"WhatsApp generation: built Prompt 1 (E-Commerce) "
                f"prompt_len={len(prompt)} request_id={ingestion.request_id}"
            )
        elif prompt_type == "prompt_close_up":
            prompt = build_close_up_ears_prompt()
            logger.info(
                f"WhatsApp generation: built Prompt 2 (Close-up on Ear) "
                f"prompt_len={len(prompt)} request_id={ingestion.request_id}"
            )
        elif prompt_type == "prompt_ugc":
            prompt = build_ugc_style_prompt()
            logger.info(
                f"WhatsApp generation: built Prompt 6 (UGC Lifestyle) "
                f"prompt_len={len(prompt)} request_id={ingestion.request_id}"
            )
        else:
            logger.warning(
                f"Unknown prompt_type '{prompt_type}' — falling back to prompt_ecommerce "
                f"ingestion_id={ingestion_id}"
            )
            prompt = build_earring_ecommerce_prompt()

        manager = ImageGenerationManager()
        result = await manager.generate_image(
            prompt=prompt,
            context={"request_id": ingestion.request_id, "aspect_ratio": "4:5"},
            reference_image=reference_image_bytes,
            reference_mime_type=ingestion.mime_type or "image/jpeg",
        )

        if not result.success:
            _fail_ingestion(
                db, ingestion,
                f"Generation failed: {result.error} (provider={result.provider_name})"
            )
            return False

        logger.info(
            f"WhatsApp generation: succeeded "
            f"provider={result.provider_name} "
            f"time={result.processing_time:.2f}s request_id={ingestion.request_id}"
        )

        ingestion.status = "generated"
        db.commit()

        image_data_url = result.image_url
        if not image_data_url:
            _fail_ingestion(db, ingestion, "Generation succeeded but no image data returned")
            return False

        generated_image_bytes = _data_url_to_bytes(image_data_url)
        if not generated_image_bytes:
            _fail_ingestion(db, ingestion, "Failed to decode generated image data")
            return False

        media_id = await upload_media_to_meta(generated_image_bytes)
        if not media_id:
            _fail_delivery(db, ingestion, "Meta media upload failed")
            return False

        logger.info(
            f"WhatsApp generation: Meta media uploaded "
            f"media_id={media_id[:20]}... request_id={ingestion.request_id}"
        )

        # Caption reflects the style selected via the button reply
        caption_map = {
            "prompt_ecommerce": "Your e-commerce image is ready.",
            "prompt_close_up": "Your Close-up on Ear image is ready.",
            "prompt_ugc": "Your UGC Lifestyle image is ready.",
        }
        send_caption = caption_map.get(prompt_type, "Your e-commerce image is ready.")

        send_ok = await send_image_to_whatsapp(
            recipient_id=ingestion.external_user_id,
            media_id=media_id,
            caption=send_caption,
        )

        if not send_ok:
            _fail_delivery(db, ingestion, "Meta message send failed")
            return False

        ingestion.status = "delivered"
        ingestion.error_message = None
        db.commit()

        logger.info(
            f"WhatsApp generation: delivered successfully "
            f"ingestion_id={ingestion_id} user={ingestion.external_user_id}"
        )
        return True

    except Exception as e:
        logger.error(f"WhatsApp generation: unexpected error: {e}")
        try:
            ingestion = db.query(WhatsAppIngestion).filter(
                WhatsAppIngestion.id == ingestion_id
            ).first()
            if ingestion and ingestion.status in ("stored", "processing"):
                _fail_ingestion(db, ingestion, f"Unexpected error: {str(e)}")
        except Exception:
            pass
        return False
    finally:
        db.close()


def _fail_ingestion(db, ingestion, error_message: str) -> None:
    """Mark an ingestion as failed with an error message."""
    ingestion.status = "failed"
    ingestion.error_message = error_message
    db.commit()
    logger.error(
        f"WhatsApp generation failed: ingestion_id={ingestion.id} "
        f"error={error_message}"
    )


def _fail_delivery(db, ingestion, error_message: str) -> None:
    """Mark delivery failure separately from generation failure."""
    ingestion.status = "delivery_failed"
    ingestion.error_message = error_message
    db.commit()
    logger.error(
        f"WhatsApp delivery failed: ingestion_id={ingestion.id} "
        f"error={error_message}"
    )


def _data_url_to_bytes(data_url: str) -> Optional[bytes]:
    """Convert a data:image/...;base64,... URL to raw bytes."""
    import base64

    try:
        if not data_url.startswith("data:"):
            return None

        header, payload = data_url.split(",", 1)
        return base64.b64decode(payload)
    except Exception:
        return None


# ─── Meta media upload ───────────────────────────────────────────────────


async def upload_media_to_meta(
    image_bytes: bytes,
    mime_type: str = "image/png",
) -> Optional[str]:
    """Upload an image to Meta's WhatsApp media API."""
    if not settings.META_WHATSAPP_TOKEN:
        logger.error("META_WHATSAPP_TOKEN not configured — cannot upload media")
        return None

    if not settings.META_PHONE_NUMBER_ID:
        logger.error("META_PHONE_NUMBER_ID not configured — cannot upload media")
        return None

    url = META_MEDIA_UPLOAD_URL.format(
        phone_number_id=settings.META_PHONE_NUMBER_ID
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            ext_map = {
                "image/png": ".png",
                "image/jpeg": ".jpg",
                "image/webp": ".webp",
            }
            ext = ext_map.get(mime_type, ".png")

            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}"},
                files={"file": (f"generated{ext}", image_bytes, mime_type)},
                data={"messaging_product": "whatsapp", "type": mime_type},
            )

            if response.status_code != 200:
                logger.error(
                    f"Meta media upload failed: status={response.status_code}"
                )
                return None

            data = response.json()
            media_id = data.get("id")
            if not media_id:
                logger.error(f"Meta media upload response missing 'id': {data}")
                return None

            return media_id

    except httpx.TimeoutException:
        logger.error("Meta media upload timed out")
        return None
    except Exception as e:
        logger.error(f"Meta media upload failed: {e}")
        return None


# ─── WhatsApp message send ───────────────────────────────────────────────


async def send_image_to_whatsapp(
    recipient_id: str,
    media_id: str,
    caption: str = "Your e-commerce image is ready.",
) -> bool:
    """Send an image message to a WhatsApp user via Meta Send API."""
    if not settings.META_WHATSAPP_TOKEN:
        logger.error("META_WHATSAPP_TOKEN not configured — cannot send message")
        return False

    if not settings.META_PHONE_NUMBER_ID:
        logger.error("META_PHONE_NUMBER_ID not configured — cannot send message")
        return False

    url = META_SEND_MESSAGE_URL.format(
        phone_number_id=settings.META_PHONE_NUMBER_ID
    )

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "image",
        "image": {
            "id": media_id,
            "caption": caption,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if response.status_code != 200:
                logger.error(
                    f"Meta send message failed: status={response.status_code}"
                )
                return False

            data = response.json()
            messages = data.get("messages", [])
            if not messages:
                logger.error(f"Meta send message response missing 'messages': {data}")
                return False

            logger.info(
                f"Meta message sent: recipient={recipient_id} "
                f"message_id={messages[0].get('id', '')}"
            )
            return True

    except httpx.TimeoutException:
        logger.error("Meta send message timed out")
        return False
    except Exception as e:
        logger.error(f"Meta send message failed: {e}")
        return False
