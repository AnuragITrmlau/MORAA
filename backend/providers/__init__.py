"""Production-ready AI Provider layer for MORAA GemVision.

Every provider in this package extends :class:`BaseAiProvider` and
implements ``analyze_image()`` which returns a normalised
:class:`~backend.schemas.ai_response.AiResponse`.

Providers are designed to be swappable — the :class:`AiManager` in
``backend.services.ai_manager`` selects the active provider and handles
fallback logic based on error classification (transient vs. permanent).
"""

from providers.base_provider import BaseAiProvider
from providers.gemini_provider import GeminiProvider
from providers.openai_provider import OpenAIProvider

__all__ = [
    "BaseAiProvider",
    "GeminiProvider",
    "OpenAIProvider",
]
