"""Processing service for enterprise-grade request tracking and logging.

This service orchestrates all processing log, tool execution log, retry,
and version history operations.  It is the single source of truth for
the event timeline (Part 12) and performance metrics (Part 13).

Every stage of the pipeline — upload, validation, storage, queue, AI
processing, report generation — is logged through this service.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.audit_log import AuditLog
from app.models.image import Image
from app.models.processing_log import ProcessingLog
from app.models.retry_history import RetryHistory
from app.models.tool_execution import ToolExecutionLog
from app.models.version_history import VersionHistory
from app.repositories.base import BaseRepository
from app.utils.logger import logger


class ProcessingService:
    """Enterprise request tracking and logging service.

    Usage::

        svc = ProcessingService(db)
        svc.log_processing_step(request_id, "upload", "completed")
        svc.log_tool_execution(request_id, analysis_id, "gem_detection", 0, "completed")
    """

    def __init__(self, db: Session):
        self.db = db
        self.processing_log_repo = BaseRepository(ProcessingLog, db)
        self.tool_exec_repo = BaseRepository(ToolExecutionLog, db)
        self.retry_repo = BaseRepository(RetryHistory, db)
        self.version_repo = BaseRepository(VersionHistory, db)
        self.audit_repo = BaseRepository(AuditLog, db)

    # ── Processing Logs ───────────────────────────────────────────────────

    def log_processing_step(
        self,
        request_id: str,
        step: str,
        status: str,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProcessingLog:
        """Record a processing step lifecycle event.

        Args:
            request_id: The upload request UUID.
            step: Step name (e.g. ``upload``, ``validation``, ``storage``,
                  ``queue``, ``ai_analysis``, ``report``).
            status: ``started``, ``completed``, or ``failed``.
            error_message: Error details if status is ``failed``.
            metadata: Optional dict stored as JSON for step-specific data.

        Returns:
            The created ProcessingLog record.
        """
        metadata_json = json.dumps(metadata) if metadata else None
        now = datetime.now(timezone.utc)

        log_entry = self.processing_log_repo.create(
            request_id=request_id,
            processing_step=step,
            status=status,
            started_at=now if status == "started" else None,
            finished_at=now if status in ("completed", "failed") else None,
            error_message=error_message,
            metadata_json=metadata_json,
        )

        if status == "completed":
            # Calculate duration from the last "started" log for this step
            prev_log = (
                self.db.query(ProcessingLog)
                .filter(
                    ProcessingLog.request_id == request_id,
                    ProcessingLog.processing_step == step,
                    ProcessingLog.status == "started",
                    ProcessingLog.id != log_entry.id,
                )
                .order_by(ProcessingLog.started_at.desc())
                .first()
            )
            if prev_log and prev_log.started_at:
                # SQLite may return offset-naive datetimes; make it aware
                ref_time = prev_log.started_at
                if ref_time.tzinfo is None:
                    ref_time = ref_time.replace(tzinfo=timezone.utc)
                duration = (now - ref_time).total_seconds()
                log_entry.processing_time = round(duration, 3)
                log_entry.started_at = prev_log.started_at
                self.db.flush()

        logger.bind(category="processing").info(
            f"Processing step: request_id={request_id} "
            f"step={step} status={status} "
            f"time={log_entry.processing_time or 0:.2f}s"
        )

        return log_entry

    def get_processing_logs(
        self, request_id: str, limit: int = 100
    ) -> List[ProcessingLog]:
        """Get all processing logs for a request, ordered by time."""
        return (
            self.db.query(ProcessingLog)
            .filter(ProcessingLog.request_id == request_id)
            .order_by(ProcessingLog.started_at.asc())
            .limit(limit)
            .all()
        )

    def complete_processing_step(
        self, request_id: str, step: str
    ) -> ProcessingLog:
        """Mark a processing step as completed and calculate its duration.

        Expects a previous ``started`` log for the same step to exist.
        """
        return self.log_processing_step(request_id, step, "completed")

    def fail_processing_step(
        self, request_id: str, step: str, error: str
    ) -> ProcessingLog:
        """Mark a processing step as failed with error details."""
        return self.log_processing_step(request_id, step, "failed", error_message=error)

    # ── Tool Execution Logs ───────────────────────────────────────────────

    def log_tool_execution(
        self,
        request_id: str,
        analysis_id: str,
        tool_name: str,
        execution_order: int,
        status: str,
        output_summary: Optional[str] = None,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None,
    ) -> ToolExecutionLog:
        """Record an AI tool/module execution event.

        Args:
            request_id: The upload request UUID.
            analysis_id: The analysis UUID.
            tool_name: Tool name (e.g. ``preprocessing``, ``gem_detection``,
                      ``stone_classification``, ``image_enhancement``,
                      ``report_generation``).
            execution_order: Zero-based execution order in the pipeline.
            status: ``pending``, ``running``, ``completed``, ``failed``.
            output_summary: Summary of the tool's output.
            error_message: Error details if failed.
            execution_time: Duration in seconds (calculated from start/end
                           if not provided).
        """
        now = datetime.now(timezone.utc)

        log_entry = self.tool_exec_repo.create(
            request_id=request_id,
            analysis_id=analysis_id,
            tool_name=tool_name,
            execution_order=execution_order,
            started_at=now,
            finished_at=now if status in ("completed", "failed") else None,
            execution_time=execution_time,
            status=status,
            output_summary=output_summary,
            error_message=error_message,
        )

        logger.bind(category="tool_exec").info(
            f"Tool execution: request_id={request_id} "
            f"tool={tool_name} order={execution_order} "
            f"status={status} time={execution_time or 0:.2f}s"
        )

        return log_entry

    def get_tool_execution_logs(
        self, request_id: str, limit: int = 100
    ) -> List[ToolExecutionLog]:
        """Get all tool execution logs for a request, ordered by execution order."""
        return (
            self.db.query(ToolExecutionLog)
            .filter(ToolExecutionLog.request_id == request_id)
            .order_by(ToolExecutionLog.execution_order.asc())
            .limit(limit)
            .all()
        )

    def start_tool_execution(
        self, request_id: str, analysis_id: str, tool_name: str, order: int
    ) -> ToolExecutionLog:
        """Start tracking a tool execution (status = running)."""
        return self.log_tool_execution(
            request_id, analysis_id, tool_name, order, "running"
        )

    def complete_tool_execution(
        self,
        request_id: str,
        analysis_id: str,
        tool_name: str,
        order: int,
        output: str,
        duration: float,
    ) -> ToolExecutionLog:
        """Mark a tool execution as completed with timing."""
        return self.log_tool_execution(
            request_id, analysis_id, tool_name, order,
            "completed", output_summary=output, execution_time=duration,
        )

    def fail_tool_execution(
        self,
        request_id: str,
        analysis_id: str,
        tool_name: str,
        order: int,
        error: str,
        duration: float,
    ) -> ToolExecutionLog:
        """Mark a tool execution as failed."""
        return self.log_tool_execution(
            request_id, analysis_id, tool_name, order,
            "failed", error_message=error, execution_time=duration,
        )

    # ── Retry History ─────────────────────────────────────────────────────

    def record_retry(
        self,
        request_id: str,
        analysis_id: str,
        attempt_number: int,
        status: str = "pending",
        result_summary: Optional[str] = None,
        error_message: Optional[str] = None,
        processing_time: Optional[float] = None,
    ) -> RetryHistory:
        """Record a retry attempt for an analysis.

        Retries use the SAME ``request_id`` — a new request is only generated
        when the user uploads a new image (Part 10).
        """
        entry = self.retry_repo.create(
            request_id=request_id,
            analysis_id=analysis_id,
            attempt_number=attempt_number,
            retry_time=datetime.now(timezone.utc),
            status=status,
            result_summary=result_summary,
            error_message=error_message,
            processing_time=processing_time,
        )

        logger.bind(category="retry").info(
            f"Retry recorded: request_id={request_id} "
            f"analysis_id={analysis_id} attempt={attempt_number} "
            f"status={status}"
        )

        return entry

    def get_retry_history(
        self, request_id: str, limit: int = 50
    ) -> List[RetryHistory]:
        """Get all retry attempts for a request."""
        return (
            self.db.query(RetryHistory)
            .filter(RetryHistory.request_id == request_id)
            .order_by(RetryHistory.attempt_number.asc())
            .limit(limit)
            .all()
        )

    # ── Version History ───────────────────────────────────────────────────

    def record_version(
        self,
        request_id: str,
        analysis_id: str,
        version_number: int,
        result_json: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> VersionHistory:
        """Record an analysis version.

        Each call creates a new version entry — previous versions are NEVER
        overwritten (Part 11).
        """
        entry = self.version_repo.create(
            request_id=request_id,
            analysis_id=analysis_id,
            version_number=version_number,
            result_json=result_json,
            summary=summary,
        )

        logger.bind(category="version").info(
            f"Version recorded: request_id={request_id} "
            f"analysis_id={analysis_id} version={version_number}"
        )

        return entry

    def get_version_history(
        self, request_id: str, limit: int = 50
    ) -> List[VersionHistory]:
        """Get all versions for a request, ordered by version number."""
        return (
            self.db.query(VersionHistory)
            .filter(VersionHistory.request_id == request_id)
            .order_by(VersionHistory.version_number.desc())
            .limit(limit)
            .all()
        )

    # ── Event Timeline ────────────────────────────────────────────────────

    def get_timeline(self, request_id: str) -> List[Dict[str, Any]]:
        """Build a complete, ordered event timeline for a request.

        Merges processing logs, tool execution logs, and audit events
        into a single chronological list (Part 12).
        """
        events: List[Dict[str, Any]] = []

        # Processing steps
        proc_logs = self.get_processing_logs(request_id)
        for log in proc_logs:
            events.append({
                "timestamp": log.started_at or log.finished_at or datetime.now(timezone.utc),
                "event_type": "processing_step",
                "title": log.processing_step.replace("_", " ").title(),
                "description": log.error_message or "",
                "status": log.status,
                "duration": log.processing_time,
            })

        # Tool executions
        tool_logs = self.get_tool_execution_logs(request_id)
        for log in tool_logs:
            events.append({
                "timestamp": log.started_at or datetime.now(timezone.utc),
                "event_type": "tool_execution",
                "title": log.tool_name.replace("_", " ").title(),
                "description": log.output_summary or log.error_message or "",
                "status": log.status,
                "duration": log.execution_time,
            })

        # Sort by timestamp
        events.sort(key=lambda e: e["timestamp"])

        return events

    # ── Audit Log ─────────────────────────────────────────────────────────

    def log_audit(
        self,
        action: str,
        status: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None,
    ) -> AuditLog:
        """Record an audit log entry for compliance and debugging (Part 14)."""
        entry = self.audit_repo.create(
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )

        logger.bind(category="audit").info(
            f"Audit: action={action} status={status} "
            f"user={user_id} request={request_id}"
        )

        return entry
