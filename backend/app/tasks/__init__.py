"""Celery task definitions for background job processing."""

from app.tasks.analysis_tasks import run_analysis_task

__all__ = ["run_analysis_task"]
