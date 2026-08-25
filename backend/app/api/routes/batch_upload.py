"""Batch upload API route — upload multiple images for one analysis.

All uploaded images share a single ``group_id`` and can be analysed
together via the group analysis endpoint.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analysis_group import (
    BatchUploadImage,
    BatchUploadResponse,
)
from app.services.processing_service import ProcessingService
from app.services.upload_service import UploadService
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Batch Upload"])


@router.post(
    "/upload/batch",
    response_model=BatchUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload multiple images for a single analysis",
    description=(
        "Upload multiple images at once. All images share a group_id "
        "so they can be analysed as a single analysis group."
    ),
)
async def upload_images_batch(
    files: List[UploadFile],
    db: Session = Depends(get_db),
):
    """Upload multiple images and assign them to a single analysis group.

    Each image is validated, stored, and linked via ``group_id``.
    All images must be valid JPEG, PNG, or WEBP files under the
    configured size limit.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided. Please select at least one image.",
        )

    if len(files) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 images per batch upload.",
        )

    service = UploadService(db)
    proc = ProcessingService(db)
    group_id = str(uuid.uuid4())
    uploaded_images: List[BatchUploadImage] = []
    errors: List[str] = []

    # Log group upload started
    proc.log_processing_step(
        group_id, "batch_upload", "started",
        metadata={"total_files": len(files)},
    )

    for order, file in enumerate(files):
        try:
            file_data = await file.read()
            file_size = len(file_data)
            filename = file.filename or f"untitled_{order}"
            mime_type = file.content_type or "image/jpeg"

            result = await service.process_upload(
                file_data=file_data,
                filename=filename,
                file_size=file_size,
                mime_type=mime_type,
            )

            uploaded_images.append(
                BatchUploadImage(
                    id=result.id,
                    filename=result.filename,
                    url=result.url,
                    size=result.size,
                    order=order,
                )
            )
        except ValueError as e:
            errors.append(f"{file.filename}: {str(e)}")
        except Exception as e:
            logger.error(f"Batch upload failed for {file.filename}: {e}")
            errors.append(f"{file.filename}: Failed to process upload")

    proc.log_processing_step(
        group_id, "batch_upload", "completed",
        metadata={
            "uploaded": len(uploaded_images),
            "failed": len(errors),
            "errors": errors if errors else None,
        },
    )

    if not uploaded_images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No images were uploaded successfully. Errors: {'; '.join(errors)}",
        )

    response = BatchUploadResponse(
        group_id=group_id,
        images=uploaded_images,
        count=len(uploaded_images),
    )

    # Store group_id reference in processing logs for traceability
    for img in uploaded_images:
        logger.bind(category="upload").info(
            f"Batch upload: group_id={group_id} "
            f"image_id={img.id} filename={img.filename} order={img.order}"
        )

    logger.info(
        f"Batch upload complete: {len(uploaded_images)} images, "
        f"{len(errors)} errors, group_id={group_id}"
    )

    return response
