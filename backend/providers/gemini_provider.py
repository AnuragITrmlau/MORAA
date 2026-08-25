"""Gemini AI provider — calls the Google Gemini API for image analysis.

This is the **primary** provider in the MORAA GemVision architecture.
It always runs first; if it fails with a transient error the AI Manager
automatically falls back to OpenAI.

Transient errors (fallback triggered):
- Timeout / DeadlineExceeded
- Rate limit (429)
- Internal server error (500)
- Network / connection failures
- Service unavailable (503)

Permanent errors (no fallback):
- Invalid API key (401 / 403)
- Invalid image / bad request (400)
- Empty / unsupported file

Requirements
------------
- ``GEMINI_API_KEY`` env var set in the backend environment.
- ``google-generativeai`` package installed (``pip install google-generativeai``).
"""

from __future__ import annotations

import io
import json
import time
from typing import Any, Dict, Optional

from app.config import settings
from providers.base_provider import BaseAiProvider
from schemas.ai_response import AiResponse
from app.utils.logger import logger


# ── Gemini-specific transient-error fingerprints ────────────────────────
_GEMINI_TRANSIENT_CODES = {
    429,  # ResourceExhausted / rate limit
    500,  # Internal
    503,  # ServiceUnavailable
    504,  # Gateway timeout
}

# ── Gemini-specific permanent-error fingerprints ────────────────────────
_GEMINI_PERMANENT_CODES = {
    400,  # BadRequest (invalid image, unsafe content)
    401,  # Unauthenticated
    403,  # PermissionDenied
    404,  # NotFound
}


class GeminiProvider(BaseAiProvider):
    """Production Gemini provider for image analysis."""

    def __init__(self) -> None:
        self._client: Optional[Any] = None

    # ── Identity ──────────────────────────────────────────────────────

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")

    @property
    def is_available(self) -> bool:
        return bool(getattr(settings, "GEMINI_API_KEY", ""))

    # ── Core analysis method ──────────────────────────────────────────

    async def analyze_image(
        self,
        image_data: bytes,
        context: Optional[Dict[str, Any]] = None,
    ) -> AiResponse:
        """Analyse a single image using Google Gemini.

        Args:
            image_data: Raw bytes of the image to analyse.
            context: May include ``request_id``, ``mime_type``,
                     ``filename``, ``custom_prompt``.

        Returns:
            AiResponse with structured analysis or error details.
        """
        request_id = (context or {}).get("request_id", "unknown")
        mime_type = (context or {}).get("mime_type", "image/jpeg")
        custom_prompt = (context or {}).get("custom_prompt", "")

        t0 = self._measure()

        # ── Lazy import and configure ─────────────────────────────────
        try:
            import google.generativeai as genai
        except ImportError:
            elapsed = self._measure() - t0
            logger.error(
                "GeminiProvider: google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )
            return AiResponse(
                success=False,
                error="google-generativeai package not installed",
                error_type="permanent",
                provider=self.provider_name,
                processing_time=elapsed,
                request_id=request_id,
            )

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 8192,
                },
            )
        except Exception as exc:
            elapsed = self._measure() - t0
            err = str(exc)
            error_type = self.classify_error(err)
            logger.error(
                f"GeminiProvider: configuration failed: {err} "
                f"request_id={request_id} error_type={error_type}"
            )
            return AiResponse(
                success=False,
                error=err,
                error_type=error_type,
                provider=self.provider_name,
                processing_time=elapsed,
                request_id=request_id,
            )

        # ── Build request contents ────────────────────────────────────
        try:
            import PIL.Image as PILImage

            pil_image = PILImage.open(io.BytesIO(image_data))
        except Exception as exc:
            elapsed = self._measure() - t0
            err = f"Failed to decode image: {exc}"
            logger.error(f"GeminiProvider: {err} request_id={request_id}")
            return AiResponse(
                success=False,
                error=err,
                error_type="permanent",
                provider=self.provider_name,
                processing_time=elapsed,
                request_id=request_id,
            )

        prompt_text = custom_prompt or self._build_default_prompt()
        contents = [prompt_text, pil_image]

        # ── Call Gemini API ───────────────────────────────────────────
        try:
            response = await model.generate_content_async(contents)
            raw_text = response.text

        except Exception as exc:
            elapsed = self._measure() - t0
            err = str(exc)
            error_type = self.classify_error(err)

            # Override classification with Gemini-specific status codes
            if hasattr(exc, "code") and exc.code in _GEMINI_PERMANENT_CODES:
                error_type = "permanent"
            elif hasattr(exc, "code") and exc.code in _GEMINI_TRANSIENT_CODES:
                error_type = "transient"

            logger.warning(
                f"GeminiProvider: API call failed: {err} "
                f"request_id={request_id} error_type={error_type} "
                f"time={elapsed:.2f}s"
            )
            return AiResponse(
                success=False,
                error=err,
                error_type=error_type,
                provider=self.provider_name,
                processing_time=elapsed,
                request_id=request_id,
            )

        # ── Parse response ────────────────────────────────────────────
        elapsed = self._measure() - t0

        parsed = self._safe_parse_json(raw_text)
        if parsed is None:
            logger.warning(
                f"GeminiProvider: failed to parse JSON from response "
                f"request_id={request_id} time={elapsed:.2f}s"
            )
            return AiResponse(
                success=False,
                error="Failed to parse JSON from Gemini response",
                error_type="transient",  # Retriable — maybe next attempt works
                provider=self.provider_name,
                processing_time=elapsed,
                request_id=request_id,
            )

        parsed = self._ensure_required_fields(parsed)

        logger.info(
            f"GeminiProvider: completed {parsed.get('category', 'unknown')} "
            f"request_id={request_id} time={elapsed:.2f}s model={self.model_name}"
        )

        return AiResponse(
            success=True,
            data=parsed,
            provider=self.provider_name,
            processing_time=elapsed,
            model=self.model_name,
            request_id=request_id,
        )

    # ── Override error classification with Gemini-specific codes ──────

    @staticmethod
    def classify_error(error_message: str) -> Optional[str]:
        """Add Gemini-specific status-code heuristics."""
        if not error_message:
            return None

        lower = error_message.lower()

        # Gemini often embeds gRPC-style status codes like "429 Too Many Requests"
        for code in _GEMINI_PERMANENT_CODES:
            if str(code) in lower:
                return "permanent"
        for code in _GEMINI_TRANSIENT_CODES:
            if str(code) in lower:
                return "transient"

        # Check for Gemini-specific error patterns
        if "api_key" in lower or "api key" in lower:
            return "permanent"
        if "unsafe content" in lower or "safety" in lower:
            return "permanent"
        if "blocked" in lower:
            return "permanent"

        # Fall back to base classification
        return BaseAiProvider.classify_error(error_message)
