"""OpenAI provider — calls the OpenAI Vision API for image analysis.

This is the **fallback** provider in the MORAA GemVision architecture.
It is only called when the primary Gemini provider fails with a transient
error (timeout, rate limit, server error, network failure, or outage).

Requirements
------------
- ``OPENAI_API_KEY`` env var set in the backend environment.
- ``openai`` package installed (``pip install openai``).
"""

from __future__ import annotations

import base64
import io
import json
import time
from typing import Any, Dict, Optional

from app.config import settings
from providers.base_provider import BaseAiProvider
from schemas.ai_response import AiResponse
from app.utils.logger import logger


class OpenAIProvider(BaseAiProvider):
    """Production OpenAI Vision provider for image analysis (fallback)."""

    def __init__(self) -> None:
        self._client: Optional[Any] = None

    # ── Identity ──────────────────────────────────────────────────────

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    @property
    def is_available(self) -> bool:
        return bool(getattr(settings, "OPENAI_API_KEY", ""))

    # ── Core analysis method ──────────────────────────────────────────

    async def analyze_image(
        self,
        image_data: bytes,
        context: Optional[Dict[str, Any]] = None,
    ) -> AiResponse:
        """Analyse a single image using OpenAI Vision API.

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
            from openai import AsyncOpenAI
        except ImportError:
            elapsed = self._measure() - t0
            logger.error(
                "OpenAIProvider: openai package not installed. "
                "Run: pip install openai"
            )
            return AiResponse(
                success=False,
                error="openai package not installed",
                error_type="permanent",
                provider=self.provider_name,
                processing_time=elapsed,
                request_id=request_id,
            )

        try:
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as exc:
            elapsed = self._measure() - t0
            err = str(exc)
            logger.error(
                f"OpenAIProvider: client init failed: {err} "
                f"request_id={request_id}"
            )
            return AiResponse(
                success=False,
                error=err,
                error_type=self.classify_error(err),
                provider=self.provider_name,
                processing_time=elapsed,
                request_id=request_id,
            )

        # ── Validate image size ──────────────────────────────────────
        try:
            import PIL.Image as PILImage

            pil_image = PILImage.open(io.BytesIO(image_data))
            # OpenAI has a 20MB limit; we check early to avoid billing
            if len(image_data) > 20 * 1024 * 1024:
                elapsed = self._measure() - t0
                return AiResponse(
                    success=False,
                    error="Image exceeds 20MB limit for OpenAI Vision API",
                    error_type="permanent",
                    provider=self.provider_name,
                    processing_time=elapsed,
                    request_id=request_id,
                )
        except Exception as exc:
            elapsed = self._measure() - t0
            err = f"Failed to decode image: {exc}"
            logger.error(f"OpenAIProvider: {err} request_id={request_id}")
            return AiResponse(
                success=False,
                error=err,
                error_type="permanent",
                provider=self.provider_name,
                processing_time=elapsed,
                request_id=request_id,
            )

        # ── Build the API request ─────────────────────────────────────
        base64_image = base64.b64encode(image_data).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{base64_image}"

        prompt_text = custom_prompt or self._build_default_prompt()

        try:
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_uri,
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=8192,
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            raw_text = response.choices[0].message.content or ""

        except Exception as exc:
            elapsed = self._measure() - t0
            err = str(exc)

            # OpenAPI-specific error classification
            error_type = self.classify_error(err)

            # OpenAI raises specific exception types
            if "InsufficientQuota" in err or "insufficient_quota" in err:
                error_type = "permanent"
            elif "invalid_api_key" in err or "Incorrect API key" in err:
                error_type = "permanent"
            elif "model_not_found" in err or "Model not found" in err:
                error_type = "permanent"

            logger.warning(
                f"OpenAIProvider: API call failed: {err} "
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

        # ── Parse JSON response ───────────────────────────────────────
        elapsed = self._measure() - t0

        parsed = self._safe_parse_json(raw_text)
        if parsed is None:
            logger.warning(
                f"OpenAIProvider: failed to parse JSON from response "
                f"request_id={request_id} time={elapsed:.2f}s"
            )
            return AiResponse(
                success=False,
                error="Failed to parse JSON from OpenAI response",
                error_type="transient",
                provider=self.provider_name,
                processing_time=elapsed,
                request_id=request_id,
            )

        parsed = self._ensure_required_fields(parsed)

        logger.info(
            f"OpenAIProvider: completed {parsed.get('category', 'unknown')} "
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

    # ── OpenAI-specific error overrides ───────────────────────────────

    @staticmethod
    def classify_error(error_message: str) -> Optional[str]:
        """Classify OpenAI API errors using their specific codes."""
        if not error_message:
            return None

        lower = error_message.lower()

        # OpenAI-specific permanent errors
        if any(kw in lower for kw in [
            "invalid_api_key",
            "incorrect api key",
            "insufficient_quota",
            "insufficient quota",
            "model not found",
            "model_not_found",
            "content_policy_violation",
            "content policy violation",
            "invalid_request_error:",
        ]):
            return "permanent"

        # OpenAI-specific transient errors
        if any(kw in lower for kw in [
            "rate_limit",
            "rate limit",
            "server_error",
            "server error",
            "service_unavailable",
            "service unavailable",
            "timeout",
            "temporary",
        ]):
            return "transient"

        return BaseAiProvider.classify_error(error_message)
