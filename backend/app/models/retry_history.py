"""Retry history model for tracking analysis retry attempts.

When an analysis fails, retries use the SAME request_id.  Each attempt
is recorded here so the full retry lifecycle is auditable.

Part 10 — Retry System.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RetryHistory(Base):
    """Record of a single retry attempt for an analysis."""

    __tablename__ = "retry_history"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    request_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("images.request_id"),
        nullable=False,
        index=True,
        comment="The upload request being retried",
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("analyses.id"),
        nullable=False,
        index=True,
        comment="The analysis being retried",
    )
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Attempt number (1 = first retry, 2 = second, etc.)",
    )
    retry_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="When this retry was initiated",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Retry status: pending, running, completed, failed",
    )
    result_summary: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Summary of the retry result",
    )
    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Error details if this retry failed",
    )
    processing_time: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        comment="Duration of this retry attempt in seconds",
    )

    def __repr__(self) -> str:
        return (
            f"<RetryHistory(id={self.id}, request_id={self.request_id}, "
            f"attempt={self.attempt_number}, status={self.status})>"
        )
