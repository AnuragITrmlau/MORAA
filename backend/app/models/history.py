"""History entry model for tracking analysis history."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HistoryEntry(Base):
    """Analysis history entry model."""

    __tablename__ = "history"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, index=True
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id"), nullable=False, index=True
    )
    image_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("images.id"), nullable=False
    )
    product_name: Mapped[str] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="completed", nullable=False
    )  # completed, processing, failed
    estimated_price: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="history_entries")
    analysis = relationship("Analysis", back_populates="history_entry")
    image = relationship("Image")

    def __repr__(self) -> str:
        return f"<HistoryEntry(id={self.id}, status={self.status})>"
