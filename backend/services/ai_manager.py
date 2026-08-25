"""AI Manager — single entry point for all AI-powered image analysis.

This is the **only** class the rest of the application interacts with for
AI analysis.  It encapsulates all provider-selection and fallback logic
so that callers never need to know which provider processed a request.

Architecture
------------
1. ``analyze_image()`` is the sole public method.
2. The manager always calls **Gemini first** (primary provider).
3. If Gemini fails with a **transient** error (timeout, rate limit,
   server error, network failure, provider outage), it automatically
   falls back to **OpenAI**.
4. If Gemini fails with a **permanent** error (invalid API key, invalid
   image, bad request, unsupported file), it **immediately** returns
   the error — no fallback.
5. If both providers fail, the last error is returned.

Design tenets
-------------
- **Frontend never knows which provider processed the request.**
  The ``AiResponse`` contains the provider name (only used for internal
  observability), but the response schema returned to the caller strips it.
- **API keys never appear in the frontend.**
  All keys are read from backend environment variables only.
- **Adding a new provider (Claude, Groq, etc.) requires zero changes**
  to business logic — just add a new provider class and register it here.

Logging
-------
Every call logs:
- ``provider_selected`` — which provider was chosen (primary vs fallback)
- ``fallback_triggered`` — whether fallback was needed (and why)
- ``reason`` — the error message that caused the fallback
- ``processing_time`` — total end-to-end time
- ``request_id`` — correlatable ID
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from providers.base_provider import BaseAiProvider
from providers.gemini_provider import GeminiProvider
from providers.openai_provider import OpenAIProvider
from schemas.ai_response import AiResponse
from app.utils.logger import logger


class AiManager:
    """Single entry point for AI image analysis with automatic failover.

    Usage::

        from backend.services.ai_manager import AiManager

        manager = AiManager()
        result = await manager.analyze_image(image_bytes, context={
            "request_id": "uuid-here",
        })

    The caller receives an ``AiResponse`` — a uniform dataclass regardless
    of which provider served the request.
    """

    def __init__(self) -> None:
        self._primary: Optional[BaseAiProvider] = None
        self._fallback: Optional[BaseAiProvider] = None
        self._initialised = False

    # ── Initialisation (lazy) ─────────────────────────────────────────

    def _init(self) -> None:
        """Lazy-initialise provider instances."""
        if self._initialised:
            return

        self._primary = GeminiProvider()
        self._fallback = OpenAIProvider()
        self._initialised = True

        logger.debug(
            "AiManager initialised: "
            f"primary='{self._primary.provider_name}' (available={self._primary.is_available}), "
            f"fallback='{self._fallback.provider_name}' (available={self._fallback.is_available})"
        )

    # ── Public API ────────────────────────────────────────────────────

    async def analyze_image(
        self,
        image_data: bytes,
        context: Optional[Dict[str, Any]] = None,
    ) -> AiResponse:
        """Analyse a single image using the best available AI provider.

        Args:
            image_data: Raw bytes of the image file to analyse.
            context: Optional dict that may include:
                - ``request_id``: str — correlatable ID for logging.
                - ``mime_type``: str — e.g. ``"image/jpeg"``.
                - ``filename``: str — original filename.
                - ``custom_prompt``: str — override prompt.

        Returns:
            An ``AiResponse`` with structured analysis data.
            The ``provider`` field is set for internal observability
            but **must not** be forwarded to the frontend.

        Raises:
            No exceptions — all errors are captured in ``AiResponse``.
        """
        self._init()
        request_id = (context or {}).get("request_id", "unknown")
        total_t0 = time.monotonic()

        # ── Phase 1: Try primary (Gemini) ─────────────────────────────
        result = await self._try_provider(
            provider=self._primary,
            image_data=image_data,
            context=context,
            is_fallback=False,
        )

        if result.success:
            total_time = time.monotonic() - total_t0
            self._log_success(result, total_time, request_id)
            return result

        # If the primary failed with a **permanent** error → stop immediately
        if result.error_type == "permanent":
            total_time = time.monotonic() - total_t0
            self._log_permanent_failure(result, total_time, request_id)
            return result

        # ── Phase 2: Fallback to OpenAI ──────────────────────────────
        fallback_reason = result.error or "Unknown transient error"
        logger.warning(
            f"AiManager: triggering fallback (primary='{self._primary.provider_name}' "
            f"failed with '{fallback_reason}') "
            f"request_id={request_id}"
        )

        fallback_result = await self._try_provider(
            provider=self._fallback,
            image_data=image_data,
            context=context,
            is_fallback=True,
        )

        total_time = time.monotonic() - total_t0

        if fallback_result.success:
            fallback_result.fallback_used = True
            self._log_fallback_success(fallback_result, total_time, request_id, fallback_reason)
            return fallback_result

        # ── Both providers failed ─────────────────────────────────────
        logger.error(
            f"AiManager: all providers failed "
            f"request_id={request_id} total_time={total_time:.2f}s "
            f"primary_error='{result.error}' "
            f"fallback_error='{fallback_result.error}'"
        )

        # Return the last error (from fallback)
        fallback_result.fallback_used = True
        fallback_result.processing_time = total_time
        return fallback_result

    # ── Internal helpers ──────────────────────────────────────────────

    async def _try_provider(
        self,
        provider: Optional[BaseAiProvider],
        image_data: bytes,
        context: Optional[Dict[str, Any]],
        is_fallback: bool,
    ) -> AiResponse:
        """Call a single provider safely, catching any unexpected errors."""
        if provider is None or not provider.is_available:
            name = provider.provider_name if provider else "none"
            logger.warning(
                f"AiManager: provider '{name}' not available, skipping"
            )
            return AiResponse(
                success=False,
                error=f"Provider '{name}' is not configured or not available",
                error_type="permanent",
                provider=name,
                request_id=(context or {}).get("request_id"),
            )

        try:
            result = await provider.analyze_image(image_data, context)
            return result
        except Exception as exc:
            # Guard against unhandled exceptions in provider code
            err = str(exc)
            logger.error(
                f"AiManager: unexpected exception in provider "
                f"'{provider.provider_name}': {err}"
            )
            return AiResponse(
                success=False,
                error=err,
                error_type="transient",
                provider=provider.provider_name,
                request_id=(context or {}).get("request_id"),
            )

    # ── Structured logging ────────────────────────────────────────────

    def _log_success(
        self, result: AiResponse, total_time: float, request_id: str
    ) -> None:
        """Log a successful primary-provider response."""
        logger.info(
            f"AiManager: success provider='{result.provider}' "
            f"model='{result.model}' "
            f"provider_time={result.processing_time:.2f}s "
            f"total_time={total_time:.2f}s "
            f"fallback=False "
            f"request_id={request_id}"
        )

    def _log_permanent_failure(
        self, result: AiResponse, total_time: float, request_id: str
    ) -> None:
        """Log a permanent failure — no fallback attempted."""
        logger.warning(
            f"AiManager: permanent failure provider='{result.provider}' "
            f"error='{result.error}' "
            f"total_time={total_time:.2f}s "
            f"fallback_skipped=True "
            f"request_id={request_id}"
        )

    def _log_fallback_success(
        self,
        result: AiResponse,
        total_time: float,
        request_id: str,
        fallback_reason: str,
    ) -> None:
        """Log a successful fallback-provider response."""
        logger.info(
            f"AiManager: success (fallback) provider='{result.provider}' "
            f"model='{result.model}' "
            f"primary_failed_with='{fallback_reason}' "
            f"provider_time={result.processing_time:.2f}s "
            f"total_time={total_time:.2f}s "
            f"fallback=True "
            f"request_id={request_id}"
        )
