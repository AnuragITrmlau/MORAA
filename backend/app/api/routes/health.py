"""Health check API route."""

from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the health status of the API service.",
)
async def health_check():
    """Return service health status."""
    return HealthResponse(status="healthy")
