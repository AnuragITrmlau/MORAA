"""Request logging middleware for API calls."""

import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests and their response times."""

    async def dispatch(self, request: Request, call_next):
        """Process request, log it, and return response."""
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Capture start time
        start_time = time.time()

        # Log request
        logger.info(
            f"→ [{request_id}] {request.method} {request.url.path}",
            extra={"category": "api"},
        )

        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.info(
                f"← [{request_id}] {request.method} {request.url.path} "
                f"→ {response.status_code} ({duration_ms:.1f}ms)",
                extra={"category": "api"},
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"✗ [{request_id}] {request.method} {request.url.path} "
                f"→ ERROR ({duration_ms:.1f}ms): {str(e)}",
                extra={"category": "api"},
            )
            raise


def setup_logging_middleware(app: FastAPI) -> None:
    """Add request logging middleware."""
    app.add_middleware(RequestLoggingMiddleware)
