"""Razorpay payment webhook routes — wallet recharge lifecycle.

Handles both standard payment links and Razorpay Payment Pages.
"""

import asyncio
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
from app.services.invoice_service import generate_invoice_pdf
from app.services.meta_whatsapp_service import (
    send_document_to_whatsapp,
    send_whatsapp_text,
)
from app.services.wallet_service import credit_wallet, get_customer
from app.utils.logger import logger

router = APIRouter(prefix="/api/payments", tags=["Payments"])

SIGNATURE_HEADER = "X-Razorpay-Signature"
PAISE_PER_RUPEE = 100

AUDIT_ACTION_PAYMENT_CAPTURED = "razorpay_payment_captured"
AUDIT_RESOURCE_TYPE = "razorpay_payment"

PAYMENT_TIPS_MESSAGE = (
    "Current balance: ₹{amount} 💰\n\n"
    "You’re ready to go! For the best results:\n"
    "📸 Shoot in a well-lit space\n"
    "💎 Only one pair of earrings per photo\n"
    "🔍 Keep it sharp — avoid lens blur\n"
    "📱 Upload in HD\n\n"
    "Send your photo whenever you’re ready!"
)


def verify_razorpay_signature(raw_body: bytes, signature_header: Optional[str]) -> bool:
    secret = (settings.RAZORPAY_WEBHOOK_SECRET or "").strip()
    if not secret:
        return True
    if not signature_header:
        return False

    computed = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, signature_header.strip())


def _nested_get(payload: Dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def _paise_to_rupees(amount_paise: int) -> int:
    return (amount_paise + PAISE_PER_RUPEE // 2) // PAISE_PER_RUPEE


def _as_id(value: Any) -> str:
    """Coerce a JSON scalar to a clean id string; reject non-scalars."""
    if isinstance(value, bool):
        return ""
    if isinstance(value, (str, int, float)):
        return str(value).strip()
    return ""


def _extract_sender_id(payment_entity: Dict[str, Any], payment_link_entity: Dict[str, Any]) -> str:
    """
    Safely resolve the payer's phone (or id) without ANY KeyError.

    Priority: notes.sender_id -> notes.phone/whatsapp_id/mobile ->
    contact (Payment Pages) -> customer_id (last resort, e.g. "cust_XXXX").
    Every access is a guarded ``.get()`` so an unexpected payload shape can
    never raise.
    """
    entities = [e for e in (payment_entity, payment_link_entity) if isinstance(e, dict)]

    # 1. Notes set at link-creation time are the most reliable.
    for ent in entities:
        notes = ent.get("notes")
        if not isinstance(notes, dict):
            continue
        for key in ("sender_id", "phone", "whatsapp_id", "mobile"):
            candidate = str(notes.get(key) or "").strip()
            if candidate:
                return candidate

    # 2. Direct contact captured by Payment Pages at checkout.
    for ent in entities:
        candidate = str(ent.get("contact") or "").strip()
        if candidate:
            return candidate

    # 3. Last resort: customer_id still enables wallet credit + dedupe.
    for ent in entities:
        candidate = str(ent.get("customer_id") or "").strip()
        if candidate:
            return candidate

    return ""


def extract_payment_data(payload: Dict[str, Any]) -> Optional[Tuple[str, int, str]]:
    """
    Safely extract (sender_id, amount_in_rupees, payment_id) without ANY KeyError,
    supporting 'payment.captured' (Payment Pages), 'payment_link.paid' (Dynamic
    Links) and 'order.paid' events.

    Returns ``None`` when the payload carries no usable payment reference;
    ``sender_id`` may be "" when the payer's phone is absent (the route then
    reports ``missing_phone``). Never raises — malformed payloads are logged
    and rejected.
    """
    try:
        if not isinstance(payload, dict):
            logger.warning("Razorpay webhook payload is not a JSON object")
            return None

        payment_entity = _nested_get(payload, "payload", "payment", "entity")
        payment_link_entity = _nested_get(payload, "payload", "payment_link", "entity")

        if not isinstance(payment_entity, dict):
            payment_entity = {}
        if not isinstance(payment_link_entity, dict):
            payment_link_entity = {}

        if not payment_entity and not payment_link_entity:
            return None

        # Safe extraction of Payment ID (required, must be a scalar).
        payment_id = _as_id(
            payment_entity.get("id") or payment_link_entity.get("id")
        )
        if not payment_id:
            logger.warning("Razorpay webhook payload missing payment entity id")
            return None

        # Safe extraction of Amount (required, in paise).
        amount_paise_raw = payment_entity.get("amount")
        if amount_paise_raw is None:
            amount_paise_raw = payment_link_entity.get("amount")

        try:
            amount_paise = int(amount_paise_raw)
        except (TypeError, ValueError):
            logger.warning("Razorpay webhook payload has a non-numeric amount")
            return None

        if amount_paise <= 0:
            return None

        # Safe extraction of Customer Phone / Sender ID (optional).
        sender_id = _extract_sender_id(payment_entity, payment_link_entity)

        return sender_id, _paise_to_rupees(amount_paise), payment_id

    except Exception as e:
        # Absolute safety net: payload parsing must never bubble a KeyError
        # (or anything else) into the middleware as a 500.
        logger.error(f"Razorpay webhook payload extraction failed unexpectedly: {e}")
        return None


def _resolve_customer(db: Session, sender_id: str) -> Optional[Customer]:
    if not sender_id:
        return None

    clean_id = sender_id.lstrip("+").strip()
    customer = (
        get_customer(db, clean_id)
        or get_customer(db, sender_id)
        or db.query(Customer).filter(Customer.whatsapp_id.contains(clean_id[-10:])).first()
    )
    return customer


def _already_processed(db: Session, payment_reference: str) -> bool:
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
        logger.error(f"Audit lookup error: {e}")
        db.rollback()
        return False


def _record_payment(
    db: Session,
    payment_reference: str,
    sender_id: str,
    amount_paid: int,
) -> None:
    try:
        db.add(
            AuditLog(
                user_id=None,
                action=AUDIT_ACTION_PAYMENT_CAPTURED,
                resource_id=payment_reference,
                resource_type=AUDIT_RESOURCE_TYPE,
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
        logger.error(f"Audit log write failed: {e}")
        db.rollback()


@router.post(
    "/razorpay/webhook",
    summary="Razorpay payment webhook",
    status_code=status.HTTP_200_OK,
)
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    raw_body = await request.body()
    signature_header = request.headers.get(SIGNATURE_HEADER)

    if not verify_razorpay_signature(raw_body, signature_header):
        logger.error("Razorpay webhook signature verification failed.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay webhook signature",
        )

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception as e:
        logger.error(f"Malformed JSON in webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    if not isinstance(payload, dict):
        logger.error("Razorpay webhook JSON body is not an object")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    event = payload.get("event", "")
    logger.info(f"Received Razorpay webhook event: '{event}'")

    if event not in ("payment_link.paid", "payment.captured", "order.paid"):
        return {"status": "ignored", "event": event}

    extracted = extract_payment_data(payload)
    if extracted is None:
        logger.warning(f"Unable to extract required payment data from payload for event: {event}")
        return {"status": "unparseable"}

    sender_id, amount_paid, payment_reference = extracted
    if not sender_id:
        logger.warning(f"Payment {payment_reference} processed but sender phone number not found.")
        return {"status": "missing_phone"}

    if _already_processed(db, payment_reference):
        logger.info(f"Payment {payment_reference} already processed, skipping duplicate.")
        return {"status": "already_processed"}

    clean_sender = sender_id.lstrip("+").strip()
    customer = _resolve_customer(db, sender_id)
    customer_name = "Valued Customer"

    if customer is None:
        # gst_number / address are NOT NULL columns populated by the WhatsApp
        # onboarding flow; a payer who has not onboarded yet gets the same
        # "N/A" placeholder values that flow uses for unknown fields.
        customer = Customer(
            whatsapp_id=clean_sender,
            full_name="Valued Customer",
            business_name="Jewelry Business",
            gst_number="N/A",
            address="N/A",
            wallet_balance=amount_paid,
            is_registered=True,
        )
        db.add(customer)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Payment webhook: customer creation failed for {clean_sender}: {e}")
            return {"status": "error", "message": "Customer provisioning failed"}
        db.refresh(customer)
    else:
        credit_wallet(db, customer.whatsapp_id, amount_paid)
        if getattr(customer, "full_name", None):
            customer_name = customer.full_name

    _record_payment(db, payment_reference, clean_sender, amount_paid)
    logger.info(f"Wallet credited ₹{amount_paid} for {clean_sender}. Now sending WhatsApp confirmation.")

    # WhatsApp Notifications Dispatch
    try:
        # 1. Immediate confirmation
        await send_whatsapp_text(
            recipient_id=clean_sender,
            message_text="Payment received, thank you 🙏",
        )

        # 2. PDF Invoice Dispatch
        inv_suffix = payment_reference[-4:] if len(payment_reference) >= 4 else "1042"
        inv_number = f"Invoice_MoraaStudio_{inv_suffix}"
        pdf_bytes = generate_invoice_pdf(
            customer_name=customer_name,
            invoice_number=inv_number,
            amount=amount_paid,
        )

        await asyncio.sleep(1)
        await send_document_to_whatsapp(
            recipient_id=clean_sender,
            document_bytes=pdf_bytes,
            filename=f"{inv_number}.pdf",
            caption="",
        )

        # 3. Balance and tips text
        await asyncio.sleep(1)
        await send_whatsapp_text(
            recipient_id=clean_sender,
            message_text=PAYMENT_TIPS_MESSAGE.format(amount=amount_paid),
        )
        logger.info(f"Successfully sent confirmation, invoice and tips to {clean_sender}")
    except Exception as e:
        logger.error(f"Post-payment WhatsApp dispatch failed: {e}")

    return {"status": "ok"}