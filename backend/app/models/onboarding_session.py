"""Onboarding session model — WhatsApp registration conversation state.

The project has no existing conversation/session store and does not use
Redis for state, so onboarding keeps the smallest isolated state mechanism
possible: ONE small additive table, accessed exclusively through the
existing SQLAlchemy ORM.

States (see ``app/services/onboarding_service.OnboardingState``):
    NOT_REGISTERED        — no customer record, no registration in progress
    AWAITING_REGISTRATION — registration instructions sent, waiting for details
    REGISTERED            — customer record exists (also derivable from the
                            ``customers`` table — this mirror lets us answer
                            "what was this user doing?" without a join)

Partially supplied registration fields are kept in ``pending_data`` (JSON
text) so nothing the customer already sent is lost while we ask only for
the fields that are still missing.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OnboardingSession(Base):
    """Per-WhatsApp-ID onboarding state row (additive, isolated)."""

    __tablename__ = "onboarding_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    whatsapp_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="WhatsApp sender phone number — one session row per WhatsApp user",
    )
    state: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="NOT_REGISTERED",
        comment="NOT_REGISTERED | AWAITING_REGISTRATION | REGISTERED",
    )
    pending_data: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="JSON of partially supplied registration fields (never guessed)",
    )

    # ── Timestamps ─────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<OnboardingSession(whatsapp_id={self.whatsapp_id}, "
            f"state={self.state})>"
        )
