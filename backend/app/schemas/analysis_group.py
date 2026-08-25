"""Schemas for multi-image analysis groups.

Multiple images can be uploaded together and analysed as a single
analysis group, producing one merged report.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BatchUploadImage(BaseModel):
    """Metadata for a single image within a batch upload."""

    id: str = Field(..., description="Image ID (UUID)")
    filename: str = Field(..., description="Original filename")
    url: str = Field(..., description="Accessible image URL")
    size: int = Field(..., description="File size in bytes")
    order: int = Field(0, description="Display order within the group")


class BatchUploadResponse(BaseModel):
    """Response returned after a batch image upload."""

    group_id: str = Field(..., description="Analysis group ID (UUID)")
    images: List[BatchUploadImage] = Field(
        ..., description="List of uploaded images"
    )
    count: int = Field(..., description="Number of images uploaded")


class GroupAnalysisRequest(BaseModel):
    """Request to start analysis on a group of images."""

    group_id: str = Field(..., description="Analysis group ID")
    image_ids: List[str] = Field(
        ..., description="IDs of images to analyse", min_length=1
    )


class GroupAnalysisResponse(BaseModel):
    """Response after starting a group analysis."""

    status: str = Field("processing", description="Analysis status")
    group_id: str = Field(..., description="Analysis group ID")
    analysis_id: str = Field(..., description="Analysis ID")


class GroupAnalysisStatus(BaseModel):
    """Status of a group analysis."""

    group_id: str = Field(..., description="Analysis group ID")
    status: str = Field("processing", description="Current status")
    total_images: int = Field(0, description="Total images in group")
    processed_images: int = Field(0, description="Images processed so far")
    failed_images: int = Field(0, description="Images that failed")
    provider_used: Optional[str] = Field(None, description="AI provider used")
    fallback_used: bool = Field(False, description="Whether fallback was used")
    processing_time: Optional[float] = Field(
        None, description="Total processing time in seconds"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
