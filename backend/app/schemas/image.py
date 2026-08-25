"""Image upload Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Image upload response.

    Every upload now carries a globally unique ``requestId`` so the frontend
    can always trace back from an analysis result to its originating upload.
    The image is stored in an isolated directory at ``uploads/<requestId>/``.
    """

    id: str = Field(..., description="Image ID (UUID)")
    requestId: str = Field(
        ..., alias="request_id",
        description="Globally unique request ID for this upload; used as the isolated storage sub-directory",
    )
    filename: str = Field(..., description="Original filename")
    url: str = Field(..., description="Accessible image URL")
    size: int = Field(..., description="File size in bytes")
    mimeType: str = Field(..., alias="mime_type", description="MIME type")
    uploadedAt: datetime = Field(
        ..., alias="uploaded_at", description="Upload timestamp"
    )

    class Config:
        populate_by_name = True


class ImageResponse(BaseModel):
    """Image detail response."""

    id: str = Field(..., description="Image ID")
    original_filename: str = Field(..., description="Original filename")
    stored_filename: str = Field(..., description="Stored filename")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    image_url: str = Field(..., description="Image URL")
    width: int | None = Field(None, description="Image width")
    height: int | None = Field(None, description="Image height")
    created_at: datetime = Field(..., description="Upload timestamp")
