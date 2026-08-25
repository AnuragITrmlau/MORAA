"""Image model for tracking uploaded jewellery images.

Every uploaded image gets a globally unique ``request_id`` and is stored
inside its own isolated directory at ``uploads/<request_id>/original.<ext>``.
This guarantees that no two uploads can ever collide or overwrite each
other, even under heavy concurrency.

Extended with SHA-256 ``image_hash`` and ``session_id`` for enterprise-grade
request tracking (Part 3 — Request Database).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Image(Base):
    """Uploaded image model — also serves as the primary analysis request record.

    Every upload creates an ``Image`` row that functions as the canonical
    request record, linking the uploaded file to its analysis lifecycle.
    """

    __tablename__ = "images"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    request_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
        comment="Globally unique request ID for this upload; used as the isolated storage sub-directory",
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        nullable=True,
        index=True,
        comment="Browser/client session ID for correlating requests from the same session",
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    image_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=True,
        comment="SHA-256 hex digest of the uploaded image for deduplication and integrity verification",
    )
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=True)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    processing_status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False,
        comment="Current processing status: pending, validated, stored, queued, processing, completed, failed"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Last update timestamp; auto-updated on record modification",
    )

    # Relationships
    user = relationship("User", back_populates="images")
    analyses = relationship(
        "Analysis", back_populates="image", lazy="dynamic",
        foreign_keys="Analysis.image_id",
    )
    processing_logs = relationship(
        "ProcessingLog", back_populates="image", lazy="dynamic",
        foreign_keys="ProcessingLog.request_id",
        primaryjoin="Image.request_id == ProcessingLog.request_id",
    )

    def __repr__(self) -> str:
        return f"<Image(id={self.id}, request_id={self.request_id}, filename={self.original_filename})>"
