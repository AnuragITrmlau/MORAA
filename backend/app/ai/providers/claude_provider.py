"""Claude provider — stub for future Anthropic Claude Vision API integration.

Will use ``claude-3-opus`` or later vision-capable models to analyse
jewellery images.  Registered in the provider manager but not yet
fully implemented.
"""

import time
from typing import Any, Dict, List, Optional

from app.ai.providers.base import BaseAIProvider, ProviderResult
from app.config import settings
from app.utils.logger import logger


class ClaudeProvider(BaseAIProvider):
    """AI provider using Anthropic Claude Vision API (stub)."""

    @property
    def provider_name(self) -> str:
        return "claude"

    @property
    def provider_version(self) -> str:
        return "1.0.0-stub"

    @property
    def is_available(self) -> bool:
        return bool(settings.ANTHROPIC_API_KEY)

    async def validate_image(self, image_path: str) -> bool:
        """Stub — always returns True."""
        return True

    async def analyze(
        self,
        image_paths: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderResult:
        """Stub — returns a placeholder result.

        TODO: Implement actual Anthropic Claude Vision API integration.
        """
        request_id = (context or {}).get("request_id", "unknown")
        start_time = time.time()

        logger.warning(
            f"ClaudeProvider called but not yet implemented "
            f"request_id={request_id}"
        )

        return ProviderResult(
            success=False,
            error="Claude provider not yet implemented. Use gemini or local_vision.",
            provider_name=self.provider_name,
            processing_time=time.time() - start_time,
        )
