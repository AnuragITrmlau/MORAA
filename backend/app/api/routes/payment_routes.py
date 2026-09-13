"""Razorpay payment webhook routes — wallet recharge lifecycle.

Wires Razorpay's asynchronous payment_link.paid webhook to Moraa Studio wallet.
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
EVENT_PAYMENT_LINK_PAID = "payment_link.paid"
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
        return False
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


def extract_payment_link_paid(
    payload: Dict[str, Any],
) -> Optional[Tuple[str, int, str]]:
    entity = _nested_get(payload, "payload", "payment_link", "entity")
    if not isinstance(entity, dict):
        return None

    notes = entity.get("notes")
    sender_id = ""
    if isinstance(notes, dict):
        sender_id = str(notes.get("sender_id") or "").strip()

    amount_paise: Any = entity.get("amount")
    if amount_paise is None:
        amount_paise = _nested_get(payload, "payload", "payment", "entity", "amount")

    try:
        amount_paise = int(amount_paise)
    except (TypeError, ValueError):
        return None

    if amount_paise <= 0:
        return None

    amount_paid = _paise_to_rupees(amount_paise)
    payment_reference = _nested_get(payload, "payload", "payment", "entity", "id")
    if not payment_reference:
        payment_reference = entity.get("id")

    return sender_id, amount_paid, str(payment_reference or "")


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
        db.rollback()
        return False


def _record_payment(
    db: Session,
    payment_reference: str,
    sender_id: str,
    amount_paid: int,
) -> None:
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay webhook signature",
        )

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    event = payload.get("event", "")
    if event != EVENT_PAYMENT_LINK_PAID:
        return {"status": "ok"}

    extracted = extract_payment_link_paid(payload)
    if extracted is None:
        return {"status": "ok"}

    sender_id, amount_paid, payment_reference = extracted
    if not sender_id:
        return {"status": "ok"}

    if _already_processed(db, payment_reference):
        return {"status": "ok"}

    clean_sender = sender_id.lstrip("+").strip()
    customer = _resolve_customer(db, sender_id)
    customer_name = "Valued Customer"

    # Schema compliant auto-create
    if customer is None:
        customer = Customer(
            whatsapp_id=clean_sender,
            full_name="Valued Customer",
            business_name="Jewelry Business",
            wallet_balance=amount_paid,
            is_registered=True,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    else:
        credit_wallet(db, customer.whatsapp_id, amount_paid)
        if getattr(customer, "full_name", None):
            customer_name = customer.full_name

    _record_payment(db, payment_reference, sender_id, amount_paid)

    try:
        # 1. Confirmation text
        await send_whatsapp_text(
            recipient_id=sender_id,
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
            recipient_id=sender_id,
            document_bytes=pdf_bytes,
            filename=f"{inv_number}.pdf",
            caption="",
        )

        # 3. Tips text
        await asyncio.sleep(1)
        await send_whatsapp_text(
            recipient_id=sender_id,
            message_text=PAYMENT_TIPS_MESSAGE.format(amount=amount_paid),
        )
    except Exception as e:
        logger.error(f"Post payment dispatch error: {e}")

    return {"status": "ok"}