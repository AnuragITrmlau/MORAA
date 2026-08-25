"""Audit log model for tracking system actions."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    """Audit log entry for tracking API actions.

    Extended with ``session_id`` and ``request_id`` to correlate audit events
    with specific upload requests and browser sessions (Part 14).
    """

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    session_id: Mapped[str] = mapped_column(
        String(36), nullable=True, index=True,
        comment="Browser/client session ID for correlating audit events",
    )
    request_id: Mapped[str] = mapped_column(
        String(36), nullable=True, index=True,
        comment="Upload request ID for correlating audit events to a specific upload",
    )
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # upload, analyze, retry, regenerate, download, login, etc.
    resource_type: Mapped[str] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # success, failure, pending
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, request_id={self.request_id})>"
