"""Application configuration management using Pydantic v2 Settings."""

import os
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables/.env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "MORAA GemVision"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Jewellery Image Analysis Platform"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database
    DATABASE_URL: str = "sqlite:///./data/moraa_gemvision.db"

    # JWT Authentication
    SECRET_KEY: str = "moraa-gemvision-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # File Uploads
    UPLOAD_DIR: str = "app/uploads"
    REPORT_DIR: str = "app/reports"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,webp"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # --- AI Engine ---
    # Options: "mock" (random), "vision" (PIL-based real analysis).
    # Add new engines in app/ai/engine_factory.py
    AI_ENGINE_TYPE: str = "vision"

    # --- AI Provider Manager ---
    # Primary provider for image analysis.
    # Options: "gemini", "openai", "claude", "local_vision"
    PRIMARY_AI_PROVIDER: str = "gemini"

    # Backup provider if primary fails.
    BACKUP_AI_PROVIDER: str = "openai"

    # Fallback provider if backup also fails.
    FALLBACK_AI_PROVIDER: str = "local_vision"

    # --- API Keys for AI Providers ---
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # --- Model Settings ---
    # Model name for Gemini API (e.g. "gemini-1.5-flash", "gemini-1.5-pro")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    # Model name for OpenAI Vision API (e.g. "gpt-4o", "gpt-4o-mini")
    OPENAI_MODEL: str = "gpt-4o-mini"

    # --- Image Generation ---
    # Primary provider for image generation.
    # Options: "gemini", "openai"
    # ChatGPT image generation (OpenAI gpt-image-1) is PRIMARY; it accepts
    # the uploaded reference image via /v1/images/edits for product
    # preservation. Gemini is the automatic fallback on recoverable failures.
    PRIMARY_IMAGE_PROVIDER: str = "openai"

    # Fallback provider for image generation if primary fails.
    # Options: "gemini", "openai"
    FALLBACK_IMAGE_PROVIDER: str = "gemini"

    # Model name for Gemini image generation. Default is the current
    # generation image model ("gemini-3.1-flash-image" / Nano Banana 2),
    # which delivers significantly better reference-image fidelity than the
    # deprecated "gemini-2.5-flash-image" (Nano Banana v1). Must support
    # image output via generate_content with response_modalities=["IMAGE"].
    GEMINI_IMAGE_MODEL: str = "gemini-3.1-flash-image"

    # Model name for OpenAI image generation. Default "gpt-image-1" is the
    # ChatGPT image model — it supports reference-image editing
    # (/v1/images/edits) which is required for the PRIMARY path to preserve
    # the uploaded product. "dall-e-3" remains available via env override
    # (text-to-image only, reference image ignored).
    OPENAI_IMAGE_MODEL: str = "gpt-image-1"

    # --- Prompt Fusion Intelligence Engine (PFIE) — DISABLED ---
    # Prompt Fusion is no longer used: the final image-generation prompt
    # comes ONLY from the Gemini-driven structured prompt generation
    # (analysis → category prompt), never from a merged/hybrid prompt.
    # The /api/fuse-prompt endpoint remains registered for backward
    # compatibility, but it no longer calls the ChatGPT creative director
    # and the frontend never invokes it.
    PFIE_ENABLED: bool = False

    # ChatGPT model used as the Luxury Jewellery Creative Director.
    PFIE_CREATIVE_MODEL: str = "gpt-4o-mini"

    # Sampling temperature for the creative director (0-1; higher = more varied).
    PFIE_CREATIVE_TEMPERATURE: float = 0.8

    # Jewellery Preservation & Scale Control (JSR enhancement).
    # When enabled, EVERY fused prompt includes the jewellery scale-control
    # block (preserve size/proportions, fit human anatomy) and category-based
    # fitting rules (ear-to-earring ratio, finger proportions, wrist proportion,
    # collarbone placement). This toggle only controls the scale-control block
    # and category fitting rules; the strengthened lifestyle removals (no cards,
    # labels, text, packaging, hands holding product) are applied independently.
    PFIE_SCALE_CONTROL_ENABLED: bool = True

    # --- Meta WhatsApp Cloud API ---
    # Webhook verification token (set in Meta developer dashboard)
    META_VERIFY_TOKEN: str = ""
    # Permanent access token for the WhatsApp Business account
    META_WHATSAPP_TOKEN: str = ""
    # Phone number ID from the Meta Business account
    META_PHONE_NUMBER_ID: str = ""
    # App secret for webhook signature validation (X-Hub-Signature-256)
    META_APP_SECRET: str = ""
    # Maximum WhatsApp image download size (bytes) — 5 MB safety limit
    META_MAX_MEDIA_BYTES: int = 5 * 1024 * 1024

    # --- Image Preprocessing ---
    # Max dimension (pixels) for image resizing before AI analysis
    PREPROCESS_MAX_DIMENSION: int = 2048
    # JPEG compression quality (0-100) for image compression
    PREPROCESS_COMPRESSION_QUALITY: int = 85

    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # --- Celery / Task Queue ---
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # When True, tasks run synchronously (no broker needed) — ideal for dev.
    # Set to False in production when a real Redis/RabbitMQ broker is available.
    CELERY_TASK_ALWAYS_EAGER: bool = True

    # Name of the Celery task queue for analysis jobs
    CELERY_ANALYSIS_QUEUE: str = "analysis"

    # Number of Celery worker processes (only used when not eager)
    CELERY_WORKER_CONCURRENCY: int = 2

    @property
    def ALLOWED_EXTENSIONS_LIST(self) -> List[str]:
        """Return allowed extensions as a list."""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        """Return max upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def IS_SQLITE(self) -> bool:
        """Check if using SQLite database."""
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def UPLOAD_PATH(self) -> Path:
        """Return upload directory as Path."""
        return Path(self.UPLOAD_DIR)

    @property
    def REPORT_PATH(self) -> Path:
        """Return report directory as Path."""
        return Path(self.REPORT_DIR)


settings = Settings()
