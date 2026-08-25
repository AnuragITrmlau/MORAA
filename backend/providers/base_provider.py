"""Abstract base class for all AI providers in the production architecture.

Every provider (Gemini, OpenAI, Claude, Groq, etc.) extends this base
and implements a single method: ``analyze_image()``.

Error Classification
--------------------
The base provides a static method ``classify_error()`` so the AI Manager
can decide whether a failure is **transient** (retriable / eligible for
fallback) or **permanent** (not eligible for fallback).

**Transient errors** (fallback allowed):
- Timeout / DeadlineExceeded
- RateLimit / ResourceExhausted (HTTP 429)
- Internal Server Error (HTTP 500)
- Temporary Network Failure / ConnectionReset
- Provider Outage / ServiceUnavailable (HTTP 503)

**Permanent errors** (no fallback):
- Invalid API Key / Authentication (HTTP 401, 403)
- Invalid Image / Bad Request (HTTP 400)
- Empty Upload / Unsupported File
- Request Entity Too Large (HTTP 413)
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from schemas.ai_response import AiResponse


# ── Transient-error keywords (case-insensitive match against error text) ─
_TRANSIENT_KEYWORDS: frozenset = frozenset({
    "timeout",
    "deadline exceeded",
    "deadline_exceeded",
    "rate limit",
    "rate_limit",
    "resource exhausted",
    "resource_exhausted",
    "429",
    "500",
    "503",
    "internal server error",
    "service unavailable",
    "service_unavailable",
    "temporarily unavailable",
    "temporary failure",
    "connection reset",
    "connection refused",
    "connection error",
    "network error",
    "provider outage",
    "upstream service error",
    "overloaded",
    "server error",
    "bad gateway",
    "502",
    "504",
    "gateway timeout",
    "gateway_timeout",
})

# ── Permanent-error keywords ──────────────────────────────────────────
_PERMANENT_KEYWORDS: frozenset = frozenset({
    "invalid api key",
    "api key not found",
    "authentication failed",
    "unauthorized",
    "401",
    "403",
    "invalid image",
    "bad request",
    "400",
    "unsupported file",
    "unsupported image",
    "empty upload",
    "empty image",
    "no image provided",
    "invalid request",
    "request entity too large",
    "413",
    "file too large",
    "permission denied",
    "access denied",
    "quota exceeded",  # different from rate-limited — billing quota
})


class BaseAiProvider(ABC):
    """Abstract base for a production AI provider.

    Subclasses must implement ``analyze_image()``.  They may optionally
    override ``classify_error()`` for provider-specific heuristics.
    """

    # ── Subclass responsibilities ─────────────────────────────────────

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique identifier (e.g. ``"gemini"``, ``"openai"``)."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Current model identifier (e.g. ``"gemini-1.5-flash"``)."""
        ...

    @abstractmethod
    async def analyze_image(
        self,
        image_data: bytes,
        context: Optional[Dict[str, Any]] = None,
    ) -> AiResponse:
        """Analyse a single image and return structured results.

        Args:
            image_data: Raw bytes of the image file to analyse.
            context: Optional dict that MAY contain:
                - ``request_id``: str — correlatable ID for logging.
                - ``mime_type``: str — e.g. ``"image/jpeg"``.
                - ``filename``: str — original filename for metadata.
                - ``custom_prompt``: str — override the default prompt.

        Returns:
            An :class:`AiResponse` with analysis data or error details.
            **Must not raise exceptions** — catch everything internally
            and return an ``AiResponse(success=False)`` so the AI Manager
            can classify and decide on fallback.
        """
        ...

    # ── Error classification (may be overridden) ──────────────────────

    @staticmethod
    def classify_error(error_message: str) -> Optional[str]:
        """Classify an error message as ``"transient"``, ``"permanent"``,
        or ``None`` (unrecognised — treat as transient by default).

        Subclasses can override to add provider-specific error codes.
        """
        if not error_message:
            return None

        lower = error_message.lower()

        for kw in _PERMANENT_KEYWORDS:
            if kw in lower:
                return "permanent"

        for kw in _TRANSIENT_KEYWORDS:
            if kw in lower:
                return "transient"

        # Unrecognised → transient (safe default: fall back)
        return "transient"

    @staticmethod
    def is_transient(error_message: str) -> bool:
        """Convenience: True if the error is transient or unrecognised."""
        return BaseAiProvider.classify_error(error_message) != "permanent"

    @staticmethod
    def is_permanent(error_message: str) -> bool:
        """Convenience: True if the error is definitively permanent."""
        return BaseAiProvider.classify_error(error_message) == "permanent"

    # ── Helpers for subclasses ────────────────────────────────────────

    @staticmethod
    def _build_default_prompt() -> str:
        """Return the standard analysis prompt used by all providers.

        Override in a subclass if you need a different prompt per provider.
        """
        return (
            "You are MORAA GemVision, a precise jewellery and product analysis AI. "
            "Analyse the provided image and return a structured JSON response. "
            "Do NOT include markdown formatting or code fences — return raw JSON only.\n\n"
            "Fields:\n"
            "- material: string (detected material, e.g. 'Yellow Gold', 'Silver', 'Bronze')\n"
            "- gold_purity: string (e.g. '18K', '14K', '925', or 'Unknown')\n"
            "- weight: float (estimated weight in grams)\n"
            "- category: string (e.g. 'Ring', 'Necklace', 'Earrings', 'Electronics')\n"
            "- estimated_price: float (estimated market price in USD)\n"
            "- confidence: float (0.0 to 1.0)\n"
            "- gemstones: array of strings\n"
            "- style: string\n"
            "- era: string\n"
            "- condition: string\n"
            "- summary: string (natural language description)"
        )

    def _safe_parse_json(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Safely parse JSON from a model response, stripping fences."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        import json
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    def _ensure_required_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Guarantee all required fields exist with safe defaults."""
        defaults: Dict[str, Any] = {
            "material": "Unknown",
            "gold_purity": "Unknown",
            "weight": 0.0,
            "category": "Unknown",
            "estimated_price": 0.0,
            "confidence": 0.0,
            "gemstones": [],
            "style": "Contemporary",
            "era": "Contemporary",
            "condition": "Unknown",
            "summary": "Analysis completed.",
        }
        for key, default in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default
        return data

    def _measure(self) -> float:
        """Return a monotonic timestamp — call before and after work."""
        return time.monotonic()
