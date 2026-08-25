"""Processing log model for tracking every stage of image processing.

Each processing step — upload, validation, storage, queue, AI analysis,
report generation — gets its own log entry so the full lifecycle of a
request is fully traceable and queryable.

Provides the event timeline (Part 12) and performance metrics (Part 13).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProcessingLog(Base):
    """Granular processing log for a single request lifecycle event."""

    __tablename__ = "processing_logs"

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
        comment="The upload request this log belongs to",
    )
    processing_step: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Name of the processing step (e.g. upload, validation, storage, queue, ai_analysis, report)",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="started",
        comment="Step status: started, completed, failed",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="When this step began",
    )
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this step finished",
    )
    processing_time: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        comment="Duration of this step in seconds",
    )
    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Error details if the step failed",
    )
    metadata_json: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Optional JSON metadata for this step (e.g. image dimensions, file size)",
    )

    # Relationships
    image = relationship("Image", back_populates="processing_logs")

    def __repr__(self) -> str:
        return (
            f"<ProcessingLog(id={self.id}, request_id={self.request_id}, "
            f"step={self.processing_step}, status={self.status})>"
        )
