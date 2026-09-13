"""Razorpay payment webhook routes — wallet recharge lifecycle.

This module is ADDITIVE: it wires Razorpay's asynchronous ``payment_link.paid``
webhook to the existing Moraa Studio wallet. No existing ingestion, media
download or Gemini generation handler is touched.

Request flow implemented here:

    1. Read the RAW request body first. Signature verification must run on the
       exact bytes Razorpay signed — re-serialising parsed JSON changes key
       ordering/spacing and would invalidate a perfectly good signature.
    2. Verify the ``X-Razorpay-Signature`` header with HMAC-SHA256 using
       ``settings.RAZORPAY_WEBHOOK_SECRET``. A mismatch is a hard HTTP 400 and
       no wallet is ever credited. When the secret is not configured the
       endpoint fails CLOSED (HTTP 400) rather than accepting unsigned calls.
    3. On ``payment_link.paid``:
         * resolve the WhatsApp ``sender_id`` from
           ``payload.payment_link.entity.notes.sender_id``
         * convert the paise amount to whole Indian Rupees (integer maths only)
         * credit the customer's ``wallet_balance`` through the shared
           ``wallet_service`` helpers (single source of money arithmetic)
         * send the official Moraa Studio payment-confirmation message over
           WhatsApp via ``meta_whatsapp_service.send_whatsapp_text``

    Every other event type is acknowledged with ``{"status": "ok"}`` and
    ignored, so Razorpay does not retry events this service does not handle.

Reliability notes:

    * Razorpay retries webhooks, so a captured payment is recorded once in the
      existing ``audit_logs`` table (``action='razorpay_payment_captured'``,
      ``resource_id=<payment id>``) and a duplicate delivery is a no-op.
      The guard is deliberately fail-OPEN: if the idempotency lookup itself
      errors, the payment is still processed so a real recharge can never be
      silently dropped.
    * Message delivery failures never fail the webhook — the money has already
      been credited and Razorpay must not be told to retry. Failures are
      logged for operations.
"""

import hashlib
import hmac
import json
from typing import Any, Dict, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.services.meta_whatsapp_service import send_whatsapp_text
from app.services.wallet_service import credit_wallet, get_customer
from app.utils.logger import logger

router = APIRouter(prefix="/api/payments", tags=["Payments"])

# ─── Constants ───────────────────────────────────────────────────────────

#: Header Razorpay signs the raw body with.
SIGNATURE_HEADER = "X-Razorpay-Signature"

#: The only event this router acts on.
EVENT_PAYMENT_LINK_PAID = "payment_link.paid"

#: Razorpay amounts are always in the minor unit — paise for INR.
PAISE_PER_RUPEE = 100

#: Audit identifiers used to record (and de-duplicate) a captured payment.
AUDIT_ACTION_PAYMENT_CAPTURED = "razorpay_payment_captured"
AUDIT_RESOURCE_TYPE = "razorpay_payment"

#: Official Moraa Studio payment confirmation message. ``{amount}`` is
#: substituted with the captured amount in whole Rupees.
PAYMENT_CONFIRMATION_MESSAGE = (
    "Payment received, thank you 🙏\n\n"
    "Current balance: ₹{amount} 💰\n\n"
    "You’re ready to go! For the best results:\n"
    "📸 Shoot in a well-lit space\n"
    "💎 Only one pair of earrings per photo\n"
    "🔍 Keep it sharp — avoid lens blur\n"
    "📱 Upload in HD\n\n"
    "Send your photo whenever you’re ready!"
)


# ─── Signature verification ──────────────────────────────────────────────


def verify_razorpay_signature(raw_body: bytes, signature_header: Optional[str]) -> bool:
    """Verify Razorpay's HMAC-SHA256 ``X-Razorpay-Signature`` header.

    Razorpay signs the raw request body with the webhook secret and sends the
    lowercase hex digest with no prefix. The comparison uses
    ``hmac.compare_digest`` so it is timing-safe.

    Args:
        raw_body: The exact bytes received in the request body.
        signature_header: Value of the ``X-Razorpay-Signature`` header.

    Returns:
        ``True`` only when a configured secret produced the supplied digest.
        Missing configuration, a missing header and a mismatch all return
        ``False`` (fail-closed).
    """
    secret = (settings.RAZORPAY_WEBHOOK_SECRET or "").strip()
    if not secret:
        logger.error(
            "RAZORPAY_WEBHOOK_SECRET not configured — rejecting Razorpay webhook"
        )
        return False

    if not signature_header:
        logger.warning("Razorpay webhook missing X-Razorpay-Signature header")
        return False

    computed = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed, signature_header.strip()):
        logger.warning("Razorpay webhook signature mismatch — possible tampering")
        return False

    return True


# ─── Payload extraction ──────────────────────────────────────────────────


def _nested_get(payload: Dict[str, Any], *path: str) -> Any:
    """Walk ``path`` through nested dicts, returning ``None`` on any miss."""
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def _paise_to_rupees(amount_paise: int) -> int:
    """Convert paise to whole Rupees without float rounding error."""
    return (amount_paise + PAISE_PER_RUPEE // 2) // PAISE_PER_RUPEE


def extract_payment_link_paid(
    payload: Dict[str, Any],
) -> Optional[Tuple[str, int, str]]:
    """Extract ``(sender_id, amount_paid_rupees, payment_reference)``.

    Reads ``payload.payment_link.entity.notes.sender_id`` and the link amount
    (falling back to the captured payment's amount when the link entity does
    not carry one). Returns ``None`` when the payload cannot be used, so the
    caller can acknowledge it without retrying forever.
    """
    entity = _nested_get(payload, "payload", "payment_link", "entity")
    if not isinstance(entity, dict):
        logger.warning("payment_link.paid webhook missing payload.payment_link.entity")
        return None

    notes = entity.get("notes")
    sender_id = ""
    if isinstance(notes, dict):
        sender_id = str(notes.get("sender_id") or "").strip()

    amount_paise: Any = entity.get("amount")
    if amount_paise is None:
        amount_paise = _nested_get(
            payload, "payload", "payment", "entity", "amount"
        )

    try:
        amount_paise = int(amount_paise)
    except (TypeError, ValueError):
        logger.warning("payment_link.paid webhook has a non-numeric amount")
        return None

    if amount_paise <= 0:
        logger.warning(
            f"payment_link.paid webhook has a non-positive amount: {amount_paise}"
        )
        return None

    amount_paid = _paise_to_rupees(amount_paise)

    payment_reference = _nested_get(payload, "payload", "payment", "entity", "id")
    if not payment_reference:
        payment_reference = entity.get("id")

    return sender_id, amount_paid, str(payment_reference or "")


def _resolve_customer(db: Session, sender_id: str) -> Optional[Customer]:
    """Look up a customer by WhatsApp ID, tolerating a leading ``+``."""
    if not sender_id:
        return None

    customer = get_customer(db, sender_id)
    if customer is not None:
        return customer

    normalized = sender_id.lstrip("+").strip()
    if normalized and normalized != sender_id:
        customer = get_customer(db, normalized)
        if customer is not None:
            return customer

    return None


# ─── Idempotency (Razorpay retries deliveries) ───────────────────────────


def _already_processed(db: Session, payment_reference: str) -> bool:
    """True when this captured payment was already credited.

    Fail-OPEN: any lookup error returns ``False`` so the payment is still
    processed rather than silently dropped.
    """
    if not payment_reference:
        return False

    try:
        existing = (
            db.query(AuditLog.id)
            .filter(
                AuditLog.action == AUDIT_ACTION_PAYMENT_CAPTURED,
                AuditLog.resource_id == payment_reference,
            )
            .first()
        )
        return existing is not None
    except Exception as e:
        db.rollback()
        logger.error(f"Razorpay webhook idempotency check failed: {e}")
        return False


def _record_payment(
    db: Session,
    payment_reference: str,
    sender_id: str,
    amount_paid: int,
) -> None:
    """Record a credited payment in the audit log (de-duplication key)."""
    if not payment_reference:
        return

    try:
        db.add(
            AuditLog(
                user_id=None,
                action=AUDIT_ACTION_PAYMENT_CAPTURED,
                resource_type=AUDIT_RESOURCE_TYPE,
                resource_id=payment_reference,
                status="success",
                details=json.dumps(
                    {
                        "sender_id": sender_id,
                        "amount_paid": amount_paid,
                        "currency": "INR",
                    }
                ),
            )
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(
            f"Razorpay webhook audit record failed: payment={payment_reference} error={e}"
        )


# ─── Webhook endpoint ────────────────────────────────────────────────────


@router.post(
    "/razorpay/webhook",
    summary="Razorpay payment webhook",
    status_code=status.HTTP_200_OK,
)
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Receive a Razorpay webhook, credit the wallet and confirm on WhatsApp.

    Always answers HTTP 400 when the signature cannot be verified. Every
    verifiable request is acknowledged with ``{"status": "ok"}`` so Razorpay
    stops retrying; business-level problems are logged, never surfaced as a
    5xx (which would trigger a retry of an already-applied credit).
    """
    raw_body = await request.body()

    signature_header = request.headers.get(SIGNATURE_HEADER)
    if not verify_razorpay_signature(raw_body, signature_header):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay webhook signature",
        )

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        logger.error(f"Razorpay webhook payload is not valid JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    if not isinstance(payload, dict):
        logger.error("Razorpay webhook payload is not a JSON object")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    event = payload.get("event", "")
    if event != EVENT_PAYMENT_LINK_PAID:
        logger.info(f"Razorpay webhook ignored: event={event}")
        return {"status": "ok"}

    extracted = extract_payment_link_paid(payload)
    if extracted is None:
        logger.error("Razorpay webhook payment_link.paid payload unusable — ignored")
        return {"status": "ok"}

    sender_id, amount_paid, payment_reference = extracted

    if not sender_id:
        logger.error(
            "Razorpay webhook payment_link.paid missing notes.sender_id — "
            f"no wallet credited (payment={payment_reference})"
        )
        return {"status": "ok"}

    if _already_processed(db, payment_reference):
        logger.info(
            f"Razorpay webhook duplicate ignored: payment={payment_reference} "
            f"sender={sender_id}"
        )
        return {"status": "ok"}

    customer = _resolve_customer(db, sender_id)
    if customer is None:
        logger.error(
            f"Razorpay webhook: no customer found for sender_id={sender_id} — "
            f"payment={payment_reference} amount={amount_paid} not credited"
        )
    else:
        new_balance = credit_wallet(db, customer.whatsapp_id, amount_paid)
        logger.info(
            f"Razorpay webhook credited wallet: sender={customer.whatsapp_id} "
            f"amount={amount_paid} balance={new_balance} "
            f"payment={payment_reference}"
        )

    _record_payment(db, payment_reference, sender_id, amount_paid)

    try:
        await send_whatsapp_text(
            recipient_id=sender_id,
            message_text=PAYMENT_CONFIRMATION_MESSAGE.format(amount=amount_paid),
        )
    except Exception as e:
        # The money is already credited — never fail the webhook over a
        # message that can be resent from the operations side.
        logger.error(f"Razorpay webhook confirmation message failed: {e}")

    return {"status": "ok"}
