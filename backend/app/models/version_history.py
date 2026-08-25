"""Version history model for preserving regenerated analysis results.

When a user regenerates an analysis, previous results are NOT overwritten.
Each version is stored separately, linked to the same ``request_id``,
so the full version lineage is preserved.

Part 11 — Version History.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VersionHistory(Base):
    """Immutable record of an analysis version for a given request."""

    __tablename__ = "version_history"

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
        comment="The upload request this version belongs to",
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("analyses.id"),
        nullable=True,
        index=True,
        comment="The analysis record for this version",
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Version number (1 = original, 2 = first regenerate, etc.)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="When this version was created",
    )
    result_json: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Full analysis result as JSON for this version",
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable summary of this version",
    )

    def __repr__(self) -> str:
        return (
            f"<VersionHistory(id={self.id}, request_id={self.request_id}, "
            f"version={self.version_number})>"
        )
