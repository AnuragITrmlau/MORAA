"""Celery task for multi-image group analysis.

Analyses multiple images together through the AI Provider Manager,
produces a single merged report, and persists the result.

This task runs in a background worker (or synchronously in eager mode).
"""

import asyncio
import concurrent.futures
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from celery import Task
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.analysis import Analysis
from app.models.image import Image
from app.services.group_analysis_service import GroupAnalysisService
from app.services.processing_service import ProcessingService
from app.utils.logger import logger


class GroupAnalysisTask(Task):
    """Base task class for group analysis with error handling."""

    autoretry_for = (Exception,)
    max_retries = 2
    default_retry_delay = 10
    acks_late = True
    reject_on_worker_lost = True
    track_started = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        group_id = kwargs.get("group_id", args[2] if len(args) > 2 else "unknown")
        logger.bind(category="analysis").error(
            f"Group analysis task failed for group {group_id}: {exc}"
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(
    bind=True,
    base=GroupAnalysisTask,
    name="run_multi_image_analysis_task",
    queue="analysis",
)
def run_multi_image_analysis_task(
    self: GroupAnalysisTask,
    analysis_id: str,
    image_paths: List[str],
    group_id: str,
) -> Dict[str, Any]:
    """Analyse multiple images and produce a single merged report.

    Args:
        analysis_id: UUID of the Analysis record.
        image_paths: Absolute paths to uploaded image files.
        group_id: The analysis group UUID.

    Returns:
        Dict with merged analysis results.
    """
    db: Session = SessionLocal()
    processing_start = datetime.now(timezone.utc)

    try:
        logger.info(
            f"Multi-image analysis task started: analysis={analysis_id} "
            f"group={group_id} images={len(image_paths)}"
        )

        # Load the analysis record
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis record {analysis_id} not found")

        proc = ProcessingService(db)
        group_service = GroupAnalysisService(db)

        # Log: processing started
        proc.log_processing_step(
            group_id, "group_analysis_pipeline", "started",
            metadata={"image_count": len(image_paths)},
        )

        # Run the actual analysis via AI Provider Manager
        # This uses async internally — need to handle event loop
        try:
            asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                result = pool.submit(
                    asyncio.run,
                    group_service.analyze_with_provider_manager(
                        image_paths, group_id,
                    ),
                ).result()
        except RuntimeError:
            result = asyncio.run(
                group_service.analyze_with_provider_manager(
                    image_paths, group_id,
                )
            )

        processing_end = datetime.now(timezone.utc)
        processing_time = (processing_end - processing_start).total_seconds()

        # Extract provider info
        provider_name = result.pop("_provider_name", "unknown")
        fallback_used = result.pop("_fallback_used", False)
        proc_time = result.pop("_processing_time", processing_time)
        tool_executions = result.pop("_tool_executions", [])

        # Log tool executions
        for tool in tool_executions:
            proc.log_tool_execution(
                request_id=group_id,
                analysis_id=analysis_id,
                tool_name=tool.get("name", "unknown"),
                execution_order=tool.get("order", 0),
                status=tool.get("status", "completed"),
                output_summary=tool.get("output", ""),
                execution_time=tool.get("duration", 0.0),
            )

        # Serialise gemstones
        gemstones_json = result.get("gemstones", [])
        if isinstance(gemstones_json, list):
            gemstones_json = json.dumps(gemstones_json)

        # Update the analysis record
        analysis.status = "completed"
        analysis.processing_time = processing_time
        analysis.material = result.get("material")
        analysis.gold_purity = result.get("gold_purity")
        analysis.weight = result.get("weight")
        analysis.category = result.get("category")
        analysis.estimated_price = result.get("estimated_price")
        analysis.confidence = result.get("confidence")
        analysis.gemstones = gemstones_json
        analysis.style = result.get("style")
        analysis.era = result.get("era")
        analysis.condition = result.get("condition")
        analysis.summary = result.get("summary")
        analysis.analyzed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(analysis)

        # Record version history
        proc.record_version(
            request_id=group_id,
            analysis_id=analysis_id,
            version_number=analysis.version_number,
            result_json=json.dumps(result, default=str),
            summary=result.get("summary", "")[:500],
        )

        # Update all images' processing status
        for img in db.query(Image).filter(Image.request_id == group_id).all():
            img.processing_status = "completed"
        db.commit()

        # Log pipeline completed
        proc.log_processing_step(
            group_id, "group_analysis_pipeline", "completed",
            metadata={
                "provider": provider_name,
                "fallback": fallback_used,
                "processing_time": round(processing_time, 3),
                "result_category": result.get("category", "unknown"),
            },
        )

        # Audit event
        proc.log_audit(
            action="analyze_group_completed",
            status="success",
            request_id=group_id,
            resource_type="analysis_group",
            resource_id=analysis_id,
            details=(
                f"Group analysis completed: {len(image_paths)} images, "
                f"provider={provider_name}, fallback={fallback_used}, "
                f"time={processing_time:.2f}s"
            ),
        )

        logger.info(
            f"Multi-image analysis completed: {analysis_id} "
            f"group={group_id} provider={provider_name} "
            f"fallback={fallback_used} time={processing_time:.2f}s"
        )

        return result

    except Exception as e:
        # Mark analysis as failed
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = "failed"
                db.commit()

            # Update image statuses
            for img in db.query(Image).filter(Image.request_id == group_id).all():
                img.processing_status = "failed"
            db.commit()

            proc = ProcessingService(db)
            proc.fail_processing_step(group_id, "group_analysis_pipeline", str(e))
            proc.log_audit(
                action="analyze_group_failed",
                status="failure",
                request_id=group_id,
                resource_type="analysis_group",
                resource_id=analysis_id,
                details=f"Group analysis failed: {str(e)[:500]}",
            )
        except Exception:
            pass

        logger.error(
            f"Multi-image analysis failed: {analysis_id} group={group_id}: {e}"
        )
        raise

    finally:
        db.close()
