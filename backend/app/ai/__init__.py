"""AI Engine package for jewellery image analysis and generation."""

from app.ai.base import AIEngine, AnalysisPipeline
from app.ai.mock_engine import MockAIEngine
from app.ai.vision_engine import VisionAIEngine
from app.ai.engine_factory import create_engine
from app.ai.provider_manager import AIProviderManager
from app.ai.image_generation_manager import ImageGenerationManager
from app.ai.providers import (
    BaseAIProvider,
    ProviderResult,
    GeminiProvider,
    OpenAIProvider,
    ClaudeProvider,
    LocalVisionProvider,
    BaseImageGenerationProvider,
    ImageGenerationResult,
    GeminiImageProvider,
    OpenAIImageProvider,
)

__all__ = [
    "AIEngine",
    "AnalysisPipeline",
    "MockAIEngine",
    "VisionAIEngine",
    "create_engine",
    "AIProviderManager",
    "ImageGenerationManager",
    "BaseAIProvider",
    "ProviderResult",
    "GeminiProvider",
    "OpenAIProvider",
    "ClaudeProvider",
    "LocalVisionProvider",
    "BaseImageGenerationProvider",
    "ImageGenerationResult",
    "GeminiImageProvider",
    "OpenAIImageProvider",
]
