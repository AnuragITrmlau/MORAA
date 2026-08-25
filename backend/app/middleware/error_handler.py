"""Global exception handler for consistent error responses."""

from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.logger import logger


def setup_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions with consistent response format."""
        logger.warning(
            f"HTTP {exc.status_code}: {exc.detail}",
            extra={"category": "api", "path": str(request.url)},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": str(exc.detail),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle request validation errors."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
            message = error.get("msg", "Validation error")
            errors.append({"field": field, "message": message})

        logger.warning(
            f"Validation error: {errors}",
            extra={"category": "api", "path": str(request.url)},
        )

        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation failed",
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unhandled exceptions gracefully."""
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={"category": "api", "path": str(request.url)},
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
