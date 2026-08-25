"""AI Provider implementations — each wraps a specific AI service.

Every provider extends ``BaseAIProvider`` and normalises its output
into ``ProviderResult`` for the ``AIProviderManager``.

Image generation providers extend ``BaseImageGenerationProvider`` and
are managed by ``ImageGenerationManager``.
"""

from app.ai.providers.base import BaseAIProvider, ProviderResult
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.claude_provider import ClaudeProvider
from app.ai.providers.local_vision_provider import LocalVisionProvider

# Image generation providers
from app.ai.providers.image_base import BaseImageGenerationProvider, ImageGenerationResult
from app.ai.providers.gemini_image_provider import GeminiImageProvider
from app.ai.providers.openai_image_provider import OpenAIImageProvider

__all__ = [
    "BaseAIProvider",
    "ProviderResult",
    "GeminiProvider",
    "OpenAIProvider",
    "ClaudeProvider",
    "LocalVisionProvider",
    # Image generation
    "BaseImageGenerationProvider",
    "ImageGenerationResult",
    "GeminiImageProvider",
    "OpenAIImageProvider",
]
