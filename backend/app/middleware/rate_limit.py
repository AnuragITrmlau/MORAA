"""Simple in-memory rate limiting middleware."""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.utils.logger import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter based on client IP."""

    def __init__(self, app):
        super().__init__(app)
        self._request_counts: Dict[str, list] = defaultdict(list)
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS

    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean old entries
        self._request_counts[client_ip] = [
            ts for ts in self._request_counts[client_ip]
            if now - ts < self.window_seconds
        ]

        # Check limit
        if len(self._request_counts[client_ip]) >= self.max_requests:
            logger.warning(
                f"Rate limit exceeded for {client_ip}",
                extra={"category": "api"},
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": self.window_seconds,
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        # Add current request
        self._request_counts[client_ip].append(now)
        return await call_next(request)


def setup_rate_limit(app: FastAPI) -> None:
    """Add rate limiting middleware."""
    app.add_middleware(RateLimitMiddleware)
