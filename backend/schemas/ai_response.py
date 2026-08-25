"""Standardised Pydantic response schema for all AI providers.

Every provider (Gemini, OpenAI, Claude, Groq, etc.) MUST return exactly
this schema so the AI Manager and all downstream consumers receive a
uniform response regardless of which provider processed the request.

The schema is intentionally flat — no nested provider-specific fields —
so that adding a new provider never requires changing the response format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AiResponse:
    """Standardised response returned by every AI provider.

    Fields
    ------
    success : bool
        True when the provider produced a valid analysis result.
    data : dict or None
        The structured analysis result (material, category, price, etc.)
        when ``success`` is True.  Always None on failure.
    error : str or None
        Human-readable error message when ``success`` is False.
    error_type : str or None
        One of ``"transient"``, ``"permanent"``, or None (on success).
        The AI Manager uses this to decide whether to fall back.
    provider : str
        Name of the provider that produced this response
        (e.g. ``"gemini"``, ``"openai"``).
    processing_time : float
        Wall-clock time in seconds spent inside the provider.
    fallback_used : bool
        Whether this response was produced as a fallback from a previously
        failed provider.  Always False for the primary provider.
    model : str or None
        Specific model name used (e.g. ``"gemini-1.5-flash"``,
        ``"gpt-4o-mini"``).  Useful for observability.
    request_id : str or None
        Correlatable ID passed through from the caller (if provided).
    """

    success: bool = False
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None  # "transient" | "permanent" | None
    provider: str = ""
    processing_time: float = 0.0
    fallback_used: bool = False
    model: Optional[str] = None
    request_id: Optional[str] = None
