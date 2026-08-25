"""Tracking API routes for enterprise request lifecycle visibility.

Provides endpoints to query the full processing event timeline (Part 12),
performance metrics (Part 13), processing logs (Part 5), tool execution
logs (Part 6), retry history (Part 10), version history (Part 11), and
audit logs (Part 14).

All endpoints are read-only and backward compatible — they do not modify
the existing upload or analysis workflows.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.image import Image
from app.repositories.base import BaseRepository
from app.services.processing_service import ProcessingService
from app.schemas.tracking import (
    ProcessingLogListResponse,
    ProcessingLogResponse,
    TimelineResponse,
    TimelineEvent,
    ToolExecutionLogResponse,
    RetryHistoryResponse,
    VersionHistoryResponse,
)

router = APIRouter(prefix="/api", tags=["Tracking"])


# ── Processing Logs ────────────────────────────────────────────────────────


@router.get(
    "/requests/{request_id}/logs",
    response_model=ProcessingLogListResponse,
    summary="Get processing logs for a request",
    description="Returns all processing step logs for a given request, ordered by time. (Part 5)",
)
def get_processing_logs(
    request_id: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum logs to return"),
    db: Session = Depends(get_db),
):
    """Get the full processing log for a request — every lifecycle step."""
    svc = ProcessingService(db)
    logs = svc.get_processing_logs(request_id, limit=limit)
    return ProcessingLogListResponse(
        logs=[
            ProcessingLogResponse(
                id=log.id,
                request_id=log.request_id,
                processing_step=log.processing_step,
                status=log.status,
                started_at=log.started_at,
                finished_at=log.finished_at,
                processing_time=log.processing_time,
                error_message=log.error_message,
            )
            for log in logs
        ],
        total=len(logs),
    )


# ── Tool Execution Logs ────────────────────────────────────────────────────


@router.get(
    "/requests/{request_id}/tools",
    response_model=list[ToolExecutionLogResponse],
    summary="Get tool execution logs for a request",
    description="Returns all AI tool/module execution logs for a request. (Part 6)",
)
def get_tool_execution_logs(
    request_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get all AI module execution logs for a request."""
    svc = ProcessingService(db)
    logs = svc.get_tool_execution_logs(request_id, limit=limit)
    return [
        ToolExecutionLogResponse(
            id=log.id,
            request_id=log.request_id,
            tool_name=log.tool_name,
            execution_order=log.execution_order,
            started_at=log.started_at,
            finished_at=log.finished_at,
            execution_time=log.execution_time,
            status=log.status,
            output_summary=log.output_summary,
            error_message=log.error_message,
        )
        for log in logs
    ]


# ── Retry History ──────────────────────────────────────────────────────────


@router.get(
    "/requests/{request_id}/retries",
    response_model=list[RetryHistoryResponse],
    summary="Get retry history for a request",
    description="Returns all retry attempts for a given request. (Part 10)",
)
def get_retry_history(
    request_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get the retry history for a request."""
    svc = ProcessingService(db)
    retries = svc.get_retry_history(request_id, limit=limit)
    return [
        RetryHistoryResponse(
            id=r.id,
            request_id=r.request_id,
            analysis_id=r.analysis_id,
            attempt_number=r.attempt_number,
            retry_time=r.retry_time,
            status=r.status,
            result_summary=r.result_summary,
            error_message=r.error_message,
            processing_time=r.processing_time,
        )
        for r in retries
    ]


# ── Version History ────────────────────────────────────────────────────────


@router.get(
    "/requests/{request_id}/versions",
    response_model=list[VersionHistoryResponse],
    summary="Get version history for a request",
    description="Returns all analysis versions for a given request. (Part 11)",
)
def get_version_history(
    request_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get the version history for a request — previous results are never overwritten."""
    svc = ProcessingService(db)
    versions = svc.get_version_history(request_id, limit=limit)
    return [
        VersionHistoryResponse(
            id=v.id,
            request_id=v.request_id,
            version_number=v.version_number,
            created_at=v.created_at,
            summary=v.summary,
        )
        for v in versions
    ]


# ── Event Timeline ─────────────────────────────────────────────────────────


@router.get(
    "/requests/{request_id}/timeline",
    response_model=TimelineResponse,
    summary="Get event timeline for a request",
    description="Returns the complete, ordered event timeline for a request. (Part 12)",
)
def get_timeline(
    request_id: str,
    db: Session = Depends(get_db),
):
    """Get the full event timeline — merge of processing steps, tool executions, and audit events."""
    svc = ProcessingService(db)
    raw_events = svc.get_timeline(request_id)
    return TimelineResponse(
        request_id=request_id,
        events=[
            TimelineEvent(
                timestamp=e["timestamp"],
                event_type=e["event_type"],
                title=e["title"],
                description=e["description"],
                status=e["status"],
                duration=e["duration"],
            )
            for e in raw_events
        ],
    )


# ── Request Lookup ─────────────────────────────────────────────────────────


@router.get(
    "/requests/by-image/{image_id}",
    response_model=dict,
    summary="Get request info by image ID",
    description="Lookup the request_id and processing status for a given image. (Part 3)",
)
def get_request_by_image(
    image_id: str,
    db: Session = Depends(get_db),
):
    """Get request information linked to an image."""
    repo = BaseRepository(Image, db)
    image = repo.get(image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    return {
        "request_id": image.request_id,
        "image_id": image.id,
        "session_id": image.session_id,
        "image_hash": image.image_hash,
        "filename": image.original_filename,
        "processing_status": image.processing_status,
        "created_at": image.created_at.isoformat() if image.created_at else None,
    }
