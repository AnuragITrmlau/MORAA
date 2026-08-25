"""Report Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReportConfigRequest(BaseModel):
    """Report configuration for generation."""

    type: str = Field(..., description="Report type: summary, market, competitor, full")
    format: str = Field(..., description="Report format: pdf, csv, excel")
    includeCharts: bool = Field(True, alias="include_charts", description="Include charts")
    dateRange: Optional[dict] = Field(None, alias="date_range", description="Date range filter")

    class Config:
        populate_by_name = True


class ReportGenerateRequest(BaseModel):
    """Report generation request."""

    type: str = Field(..., description="Report type")
    format: str = Field("pdf", description="Report format")
    includeCharts: bool = Field(True, alias="include_charts")
    analysis_id: Optional[str] = Field(None, description="Specific analysis ID")

    class Config:
        populate_by_name = True


class ReportResponse(BaseModel):
    """Report metadata response."""

    id: str = Field(..., description="Report ID")
    url: str = Field("", description="Download URL")
    filename: str = Field(..., description="Report filename")
    size: int = Field(0, description="File size in bytes")
    pages: int = Field(0, description="Number of pages")
    generatedAt: datetime = Field(
        ..., description="Generation timestamp"
    )
    type: str = Field("", description="Report type")
    format: str = Field("pdf", description="Report format")


class ReportDownloadResponse(BaseModel):
    """Report download response."""

    filename: str = Field(..., description="Download filename")
    content_type: str = Field("application/pdf", description="Content type")
    content_length: int = Field(0, description="Content length")
