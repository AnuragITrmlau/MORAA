"""Analysis model for jewellery image analysis results."""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.database import Base


class JSONType(TypeDecorator):
    """Generic JSON type that works with both SQLite and PostgreSQL."""

    impl = Text

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import JSONB

            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if dialect.name == "postgresql":
            return value
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if dialect.name == "postgresql":
            return value
        if value is not None:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return None
        return None


class Analysis(Base):
    """Jewellery analysis result model.

    Every analysis is permanently linked to its ``request_id`` so the result
    can never be confused with another image, even under concurrent execution.

    Extended with ``retry_count`` and ``version_number`` for retry and
    version history support (Parts 10 & 11).
    """

    __tablename__ = "analyses"

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
        comment="Globally unique request ID linking this analysis to its upload",
    )
    image_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("images.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="processing", nullable=False
    )  # processing, completed, failed

    # Processing metrics
    processing_time: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Total processing time in seconds"
    )

    # Retry and version tracking
    retry_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        comment="Number of retry attempts for this analysis"
    )
    version_number: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False,
        comment="Analysis version number (1 = original, 2+ = regenerations)"
    )

    # Analysis results from AI
    material: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gold_purity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estimated_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gemstones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string array
    style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    era: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    condition: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Raw AI response - uses compatible JSON type for both SQLite and PostgreSQL
    raw_response: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Last update timestamp; auto-updated on record modification",
    )

    # Relationships
    image = relationship(
        "Image", back_populates="analyses",
        foreign_keys=[image_id],
    )
    user = relationship("User", back_populates="analyses")
    history_entry = relationship(
        "HistoryEntry", back_populates="analysis", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, request_id={self.request_id}, status={self.status})>"
