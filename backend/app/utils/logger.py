"""Logging configuration using loguru for structured logs."""

import sys
from pathlib import Path

from loguru import logger

from app.config import settings


def setup_logging() -> None:
    """Configure application-wide logging."""

    # Remove default handler
    logger.remove()

    # Console handler
    logger.add(
        sys.stdout,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=settings.DEBUG,
    )

    # File handler - error logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        format=settings.LOG_FORMAT,
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=True,
    )

    # File handler - all logs
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="INFO",
        rotation="1 day",
        retention="7 days",
        compression="gz",
    )

    # File handler - upload logs (separate file)
    logger.add(
        log_dir / "uploads_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        level="INFO",
        rotation="1 day",
        retention="30 days",
        filter=lambda record: record["extra"].get("category") == "upload",
    )

    # File handler - API logs
    logger.add(
        log_dir / "api_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        level="INFO",
        rotation="1 day",
        retention="7 days",
        filter=lambda record: record["extra"].get("category") == "api",
    )

    logger.info("Logging configured successfully", extra={"category": "system"})
