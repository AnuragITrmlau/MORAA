"""Group analysis service — orchestrates multi-image analysis.

Multiple images are processed together by the AI Provider Manager,
which can use any registered provider with automatic failover.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.ai.provider_manager import AIProviderManager
from app.config import settings
from app.models.analysis import Analysis
from app.models.image import Image
from app.repositories.base import BaseRepository
from app.schemas.analysis_group import (
    GroupAnalysisResponse,
    GroupAnalysisStatus,
)
from app.services.preprocessing_service import PreprocessingService
from app.services.processing_service import ProcessingService
from app.tasks.analysis_tasks import run_analysis_task
from app.utils.logger import logger


class GroupAnalysisService:
    """Service for analysing multiple images as a single analysis group."""

    def __init__(self, db: Session):
        self.db = db
        self.analysis_repo = BaseRepository(Analysis, db)
        self.image_repo = BaseRepository(Image, db)
        self.provider_manager = AIProviderManager()

    async def start_group_analysis(
        self,
        group_id: str,
        image_ids: List[str],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> GroupAnalysisResponse:
        """Start analysis for a group of images.

        All images are analysed together through the AI Provider Manager,
        which handles provider selection, retry, and failover automatically.

        Args:
            group_id: UUID identifying this analysis group.
            image_ids: List of image IDs to analyse.
            user_id: Optional authenticated user ID.
            session_id: Optional browser session ID.

        Returns:
            ``GroupAnalysisResponse`` with processing status.
        """
        proc = ProcessingService(self.db)

        # Verify all images exist
        images: List[Image] = []
        for img_id in image_ids:
            img = self.image_repo.get(img_id)
            if not img:
                raise ValueError(f"Image not found: {img_id}")
            images.append(img)

        if not images:
            raise ValueError("No valid images found for analysis")

        # Log: analysis started
        proc.log_processing_step(
            group_id, "group_analysis", "started",
            metadata={
                "image_count": len(images),
                "image_ids": image_ids,
                "provider_chain": self.provider_manager.get_provider_chain(),
            },
        )

        # Create the analysis record
        analysis_id = str(uuid.uuid4())
        analysis = self.analysis_repo.create(
            id=analysis_id,
            request_id=group_id,
            image_id=images[0].id,  # Primary image for FK
            user_id=user_id,
            status="processing",
            version_number=1,
        )

        # Update all images' status
        for img in images:
            img.processing_status = "queued"
        self.db.flush()

        # Log: queue completed
        proc.log_processing_step(group_id, "queue", "completed")

        # Dispatch to Celery for background processing
        image_paths = [img.file_path for img in images]
        from app.tasks.group_analysis_tasks import run_multi_image_analysis_task
        run_multi_image_analysis_task.delay(
            analysis_id=analysis_id,
            image_paths=image_paths,
            group_id=group_id,
        )

        # Audit event
        proc.log_audit(
            action="analyze_group",
            status="processing",
            user_id=user_id,
            session_id=session_id,
            request_id=group_id,
            resource_type="analysis_group",
            resource_id=analysis_id,
            details=f"Group analysis started: {len(images)} images",
        )

        logger.info(
            f"Group analysis started: {analysis_id} "
            f"group_id={group_id} images={len(images)}"
        )

        return GroupAnalysisResponse(
            status="processing",
            group_id=group_id,
            analysis_id=analysis_id,
        )

    def get_group_status(self, group_id: str) -> Optional[GroupAnalysisStatus]:
        """Get the current status of a group analysis.

        Queries the processing logs to determine progress.
        """
        proc = ProcessingService(self.db)
        logs = proc.get_processing_logs(group_id)

        if not logs:
            return None

        # Determine overall status from logs
        status = "processing"
        has_completed = any(
            l.status == "completed" and l.processing_step == "group_analysis"
            for l in logs
        )
        has_failed = any(
            l.status == "failed" and l.processing_step == "group_analysis"
            for l in logs
        )

        if has_completed:
            status = "completed"
        elif has_failed:
            status = "failed"

        # Count images from metadata
        total_images = 0
        for log in logs:
            if log.metadata_json:
                try:
                    meta = json.loads(log.metadata_json)
                    total_images = meta.get("image_count", total_images)
                except (json.JSONDecodeError, TypeError):
                    pass

        # Find the analysis record for provider info
        analysis = (
            self.db.query(Analysis)
            .filter(Analysis.request_id == group_id)
            .first()
        )

        return GroupAnalysisStatus(
            group_id=group_id,
            status=status,
            total_images=total_images,
            processed_images=total_images if status == "completed" else 0,
            failed_images=0 if status == "completed" else (total_images if status == "failed" else 0),
            provider_used=None,  # Populated by task on completion
            fallback_used=False,
            error=None,
        )

    def get_group_images(self, group_id: str) -> List[Image]:
        """Get all images belonging to an analysis group.

        Uses the request_id (which is the group_id) to find images.
        """
        return (
            self.db.query(Image)
            .filter(Image.request_id == group_id)
            .all()
        )

    async def analyze_with_provider_manager(
        self,
        image_paths: List[str],
        group_id: str,
    ) -> Dict[str, Any]:
        """Analyse multiple images using the AI Provider Manager.

        This is the core analysis method called by the Celery task.
        It:
        1. Preprocesses all images
        2. Sends them to the AI Provider Manager
        3. Returns the merged result

        Args:
            image_paths: Absolute paths to image files.
            group_id: The analysis group ID (used as request_id).

        Returns:
            Dict with analysis results and metadata.
        """
        proc = ProcessingService(self.db)
        prep_service = PreprocessingService()

        # Log: preprocessing started
        proc.log_processing_step(group_id, "preprocessing", "started")

        # Preprocess all images
        preprocess_results = await prep_service.preprocess_batch(image_paths)

        valid_paths = []
        failed_count = 0
        for pr in preprocess_results:
            if pr.success and pr.processed_path:
                valid_paths.append(pr.processed_path)
            else:
                failed_count += 1

        if not valid_paths:
            error_msg = "All images failed preprocessing"
            proc.fail_processing_step(group_id, "preprocessing", error_msg)
            raise ValueError(error_msg)

        proc.log_processing_step(
            group_id, "preprocessing", "completed",
            metadata={
                "valid": len(valid_paths),
                "failed": failed_count,
                "total": len(image_paths),
            },
        )

        # Log: ai_provider_analysis started
        proc.log_processing_step(group_id, "ai_provider_analysis", "started")

        # Run through AI Provider Manager (with failover)
        context = {"request_id": group_id}
        provider_result = await self.provider_manager.analyze(
            image_paths=valid_paths,
            context=context,
        )

        if not provider_result.success:
            error_msg = provider_result.error or "AI analysis failed"
            proc.fail_processing_step(group_id, "ai_provider_analysis", error_msg)
            raise ValueError(error_msg)

        proc.log_processing_step(
            group_id, "ai_provider_analysis", "completed",
            metadata={
                "provider": provider_result.provider_name,
                "fallback": provider_result.fallback_used,
                "time": round(provider_result.processing_time, 3),
            },
        )

        # Add metadata to result
        result_data = provider_result.data or {}
        result_data["_provider_name"] = provider_result.provider_name
        result_data["_fallback_used"] = provider_result.fallback_used
        result_data["_processing_time"] = provider_result.processing_time
        result_data["_tool_executions"] = provider_result.tool_executions

        return result_data
