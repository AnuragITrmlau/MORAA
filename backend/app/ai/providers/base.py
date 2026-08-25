"""Abstract base class for all AI providers in the Provider Manager.

Every provider extends ``BaseAIProvider`` and implements ``analyze()``
and ``validate_image()``.  The ``AIProviderManager`` orchestrates
failover across registered providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ProviderResult:
    """Standardised result returned by every provider."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    provider_name: str = ""
    processing_time: float = 0.0
    fallback_used: bool = False
    tool_executions: List[Dict[str, Any]] = field(default_factory=list)


class BaseAIProvider(ABC):
    """Abstract base for an AI analysis provider.

    Each provider wraps a specific AI service (Gemini, OpenAI, Claude,
    local vision) and normalises its output into the standard
    ``ProviderResult`` format.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name (e.g. ``gemini``, ``openai``)."""
        ...

    @property
    @abstractmethod
    def provider_version(self) -> str:
        """Provider implementation version."""
        ...

    @abstractmethod
    async def analyze(
        self,
        image_paths: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderResult:
        """Analyse one or more images and return structured results.

        Args:
            image_paths: Absolute paths to the uploaded image files.
                         Single-image analysis passes a list of 1 element.
            context: Optional contextual data (request_id, preferences, etc.).

        Returns:
            A ``ProviderResult`` with analysis data or error details.
        """
        ...

    @abstractmethod
    async def validate_image(self, image_path: str) -> bool:
        """Validate that an image is suitable for analysis."""
        ...

    @property
    def capabilities(self) -> List[str]:
        """List of capabilities this provider supports."""
        return ["image_analysis"]

    @property
    def is_available(self) -> bool:
        """Whether this provider is configured and ready."""
        return True
