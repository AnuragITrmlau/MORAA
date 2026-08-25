"""Pydantic schemas for enterprise request tracking models.

Covers ProcessingLogs, ToolExecutionLogs, RetryHistory, VersionHistory,
and AuditLog responses for querying the event timeline (Part 12) and
performance metrics (Part 13).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Processing Log ─────────────────────────────────────────────────────────


class ProcessingLogResponse(BaseModel):
    """A single processing step in the request lifecycle."""

    id: str = Field(..., description="Log entry ID")
    requestId: str = Field(..., alias="request_id", description="Upload request ID")
    processingStep: str = Field(
        ..., alias="processing_step", description="Step name (e.g. upload, validation, ai_analysis)"
    )
    status: str = Field(..., description="Step status: started, completed, failed")
    startedAt: datetime = Field(..., alias="started_at", description="When the step began")
    finishedAt: Optional[datetime] = Field(
        None, alias="finished_at", description="When the step finished"
    )
    processingTime: Optional[float] = Field(
        None, alias="processing_time", description="Step duration in seconds"
    )
    errorMessage: Optional[str] = Field(
        None, alias="error_message", description="Error details if failed"
    )

    class Config:
        populate_by_name = True


class ProcessingLogListResponse(BaseModel):
    """Paginated list of processing logs."""

    logs: List[ProcessingLogResponse] = Field(..., description="Processing log entries")
    total: int = Field(..., description="Total number of log entries")


# ── Tool Execution Log ─────────────────────────────────────────────────────


class ToolExecutionLogResponse(BaseModel):
    """Execution log for a single AI tool/module."""

    id: str = Field(..., description="Log entry ID")
    requestId: str = Field(..., alias="request_id", description="Upload request ID")
    toolName: str = Field(..., alias="tool_name", description="AI tool/module name")
    executionOrder: int = Field(
        ..., alias="execution_order", description="Execution order in pipeline"
    )
    startedAt: datetime = Field(..., alias="started_at", description="When execution began")
    finishedAt: Optional[datetime] = Field(
        None, alias="finished_at", description="When execution finished"
    )
    executionTime: Optional[float] = Field(
        None, alias="execution_time", description="Execution duration in seconds"
    )
    status: str = Field(..., description="Execution status")
    outputSummary: Optional[str] = Field(
        None, alias="output_summary", description="Summary of tool output"
    )
    errorMessage: Optional[str] = Field(
        None, alias="error_message", description="Error details if failed"
    )

    class Config:
        populate_by_name = True


# ── Retry History ──────────────────────────────────────────────────────────


class RetryHistoryResponse(BaseModel):
    """A single retry attempt record."""

    id: str = Field(..., description="Retry entry ID")
    requestId: str = Field(..., alias="request_id", description="Upload request ID")
    analysisId: str = Field(..., alias="analysis_id", description="Analysis ID")
    attemptNumber: int = Field(..., alias="attempt_number", description="Attempt number")
    retryTime: datetime = Field(..., alias="retry_time", description="When retry was initiated")
    status: str = Field(..., description="Retry status")
    resultSummary: Optional[str] = Field(
        None, alias="result_summary", description="Retry result summary"
    )
    errorMessage: Optional[str] = Field(
        None, alias="error_message", description="Error details if failed"
    )
    processingTime: Optional[float] = Field(
        None, alias="processing_time", description="Retry duration in seconds"
    )

    class Config:
        populate_by_name = True


# ── Version History ────────────────────────────────────────────────────────


class VersionHistoryResponse(BaseModel):
    """A single analysis version record."""

    id: str = Field(..., description="Version entry ID")
    requestId: str = Field(..., alias="request_id", description="Upload request ID")
    versionNumber: int = Field(..., alias="version_number", description="Version number")
    createdAt: datetime = Field(..., alias="created_at", description="When this version was created")
    summary: Optional[str] = Field(None, description="Version summary")

    class Config:
        populate_by_name = True


# ── Event Timeline ─────────────────────────────────────────────────────────


class TimelineEvent(BaseModel):
    """A single event in the request processing timeline."""

    timestamp: datetime = Field(..., description="When the event occurred")
    eventType: str = Field(
        ..., alias="event_type",
        description="Event type: processing_step, tool_execution, audit_event",
    )
    title: str = Field(..., description="Human-readable event title")
    description: str = Field(default="", description="Detailed event description")
    status: str = Field(default="", description="Event status")
    duration: Optional[float] = Field(None, description="Duration in seconds")

    class Config:
        populate_by_name = True


class TimelineResponse(BaseModel):
    """Complete event timeline for a request, ordered by timestamp."""

    requestId: str = Field(..., alias="request_id", description="Upload request ID")
    events: List[TimelineEvent] = Field(default_factory=list, description="Ordered event list")

    class Config:
        populate_by_name = True


# ── Audit Log ──────────────────────────────────────────────────────────────


class AuditLogResponse(BaseModel):
    """Audit log entry response."""

    id: str = Field(..., description="Audit entry ID")
    userId: Optional[str] = Field(None, alias="user_id", description="User ID")
    sessionId: Optional[str] = Field(None, alias="session_id", description="Session ID")
    requestId: Optional[str] = Field(None, alias="request_id", description="Request ID")
    action: str = Field(..., description="Action performed")
    resourceType: Optional[str] = Field(None, alias="resource_type", description="Resource type")
    resourceId: Optional[str] = Field(None, alias="resource_id", description="Resource ID")
    status: str = Field(..., description="Action status")
    ipAddress: Optional[str] = Field(None, alias="ip_address", description="Client IP")
    details: Optional[str] = Field(None, description="Action details")
    createdAt: datetime = Field(..., alias="created_at", description="When the action occurred")

    class Config:
        populate_by_name = True
