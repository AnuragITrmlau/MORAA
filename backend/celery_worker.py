"""
Celery worker entry point for MORAA GemVision.

Run in production (requires a live Redis instance):

    celery -A celery_worker worker -l info -Q analysis

Or with auto-reload during development:

    celery -A celery_worker worker -l info -Q analysis --autoreload

The worker must be started separately from the FastAPI server.
"""

from app.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()
