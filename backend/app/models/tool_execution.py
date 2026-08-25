"""Tool execution log model for tracking every AI module invocation.

Every AI tool — preprocessing, gem detection, stone classification,
image enhancement, report generation — logs its execution here with
timing, status, output summary, and error details.

Enables per-module performance analysis (Part 6).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ToolExecutionLog(Base):
    """Execution log for a single AI tool/module invocation."""

    __tablename__ = "tool_execution_logs"

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
        comment="The upload request this tool execution belongs to",
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("analyses.id"),
        nullable=True,
        index=True,
        comment="The analysis this tool execution was part of",
    )
    tool_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Name of the AI tool/module (e.g. gem_detection, stone_classifier, image_enhancer)",
    )
    execution_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Execution order within the pipeline (0-based)",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="When this tool began execution",
    )
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this tool finished execution",
    )
    execution_time: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        comment="Duration of this tool execution in seconds",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="running",
        comment="Execution status: pending, running, completed, failed",
    )
    output_summary: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Summary of the tool's output",
    )
    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Error details if execution failed",
    )

    def __repr__(self) -> str:
        return (
            f"<ToolExecutionLog(id={self.id}, request_id={self.request_id}, "
            f"tool={self.tool_name}, status={self.status})>"
        )
