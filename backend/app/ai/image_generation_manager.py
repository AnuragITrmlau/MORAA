"""Image Generation Manager — orchestrates image generation across multiple AI providers.

The manager provides a single ``generate_image()`` entry point that:
1. Attempts generation with the primary provider (ChatGPT image generation
   / OpenAI gpt-image-1 — reference-aware editing)
2. Falls back to the secondary provider (Gemini) on recoverable failures
3. Only falls back for: HTTP 429, quota exceeded, timeouts, temporary 5xx,
   transient network failures
4. Does NOT fall back for: invalid prompts, bad requests, missing config,
   programming errors

Usage::

    from app.ai.image_generation_manager import ImageGenerationManager

    manager = ImageGenerationManager()
    result = await manager.generate_image(prompt="A gold ring on a marble surface")
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from app.ai.providers.image_base import (
    BaseImageGenerationProvider,
    ImageGenerationResult,
)
from app.ai.providers.gemini_image_provider import GeminiImageProvider
from app.ai.providers.openai_image_provider import OpenAIImageProvider
from app.ai.marketplaces.registry import get_marketplace_presentation
from app.ai.product_fidelity import REFERENCE_PRIORITY_BLOCK
from app.config import settings
from app.utils.logger import logger


# ─── Registry — maps config values to provider classes ─────────────────
_IMAGE_PROVIDER_REGISTRY: Dict[str, type[BaseImageGenerationProvider]] = {
    "gemini": GeminiImageProvider,
    "openai": OpenAIImageProvider,
}


# ─── Reference-image priority block (Product Identity Lock) ─────────────
# Automatically appended to the prompt whenever a reference image is present.
# This is the server-side safety net that guarantees the spec's "REFERENCE
# IMAGE PRIORITY: MAXIMUM" instruction always reaches the image model — even
# when a client skips PFIE fusion, or a provider does not support reference
# images (e.g. DALL-E text-only fallback). It only strengthens instructions;
# it never changes provider call behaviour.
# REFERENCE_PRIORITY_BLOCK imported from app.ai.product_fidelity


# ─── Recoverable failure patterns ──────────────────────────────────────
# These are the ONLY conditions under which we fall back to the next provider.
_RECOVERABLE_PATTERNS = [
    "429",
    "quota",
    "rate_limit",
    "rate limit",
    "timeout",
    "deadline exceeded",
    "deadline_exceeded",
    "unavailable",
    "service unavailable",
    "temporarily",
    "network",
    "connection",
    "reset",
    "internal",
    "server error",
    "resource exhausted",
    "resource_exhausted",
    "502",
    "503",
    "504",
    "5xx",
]


def _is_recoverable_error(error_message: str) -> bool:
    """Check if an error is recoverable and should trigger a fallback."""
    if not error_message:
        return False
    error_lower = error_message.lower()
    return any(pattern in error_lower for pattern in _RECOVERABLE_PATTERNS)


# ─── Non-recoverable patterns (never fallback) ─────────────────────────
# These patterns must be specific to avoid incorrectly classifying
# recoverable errors (e.g. "invalid" alone could match "invalid response").
_NON_RECOVERABLE_PATTERNS = [
    "invalid prompt",
    "invalid payload",
    "invalid api request",
    "bad request",
    "400",
    "403",
    "api key not",
    "api key is invalid",
    "api key missing",
    "not found",
    "404",
    "not supported",
    "unsupported",
    "safety",
    "blocked",
    "harmful",
    "content filtered",
    "content_filtered",
    "prompt blocked",
    "prompt was blocked",
]


def _is_non_recoverable_error(error_message: str) -> bool:
    """Check if an error is definitively non-recoverable."""
    if not error_message:
        return False
    error_lower = error_message.lower()
    return any(pattern in error_lower for pattern in _NON_RECOVERABLE_PATTERNS)


class ImageGenerationManager:
    """Orchestrates image generation with automatic provider failover.

    The manager:
    - Uses the configured primary provider (default: OpenAI gpt-image-1,
      reference-aware ChatGPT image generation)
    - Falls back to the configured fallback provider (default: Gemini) on
      recoverable failures
    - Does NOT fallback for non-recoverable failures (invalid prompt, etc.)
    - Logs every step, retry, and fallback event
    """

    MAX_RETRIES_PER_PROVIDER: int = 1
    RETRY_DELAY_SECONDS: float = 2.0

    def __init__(self):
        self._providers: Dict[str, BaseImageGenerationProvider] = {}
        self._initialised = False

    def _init_providers(self) -> None:
        """Lazy-initialise provider instances."""
        if self._initialised:
            return
        for name, cls in _IMAGE_PROVIDER_REGISTRY.items():
            try:
                self._providers[name] = cls()
            except Exception as e:
                logger.warning(
                    f"Failed to initialise image provider '{name}': {e}"
                )
        self._initialised = True

    def _get_provider(self, name: str) -> Optional[BaseImageGenerationProvider]:
        """Get a provider instance by name."""
        self._init_providers()
        return self._providers.get(name)

    def _get_provider_chain(self) -> List[str]:
        """Build the ordered provider chain for image generation.

        Default: OpenAI gpt-image-1 (primary) -> Gemini (fallback).
        Override via PRIMARY_IMAGE_PROVIDER / FALLBACK_IMAGE_PROVIDER config.
        """
        primary = (settings.PRIMARY_IMAGE_PROVIDER or "openai").strip().lower()
        fallback = (settings.FALLBACK_IMAGE_PROVIDER or "gemini").strip().lower()

        chain: List[str] = []
        if primary in _IMAGE_PROVIDER_REGISTRY:
            chain.append(primary)
        if fallback in _IMAGE_PROVIDER_REGISTRY and fallback != primary:
            chain.append(fallback)

        return chain or ["gemini", "openai"]

    async def generate_image(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        force_provider: Optional[str] = None,
        reference_image: Optional[bytes] = None,
        reference_mime_type: str = "image/jpeg",
        marketplace: Optional[str] = None,
    ) -> ImageGenerationResult:
        """Generate an image with automatic failover across providers.

        Args:
            prompt: The text prompt for image generation.
            context: Optional dict with ``request_id``, ``aspect_ratio``, etc.
            force_provider: If set, uses ONLY this provider (no failover).
            reference_image: Optional bytes of the original product image.
                When provided, providers that support image-conditioned
                generation will use it to preserve product identity.
                Additionally, the ``REFERENCE_PRIORITY_BLOCK`` is auto-
                appended to the prompt (unless already present) so every
                provider path carries the identity-lock instruction.
            reference_mime_type: MIME type of the reference image.
            marketplace: Optional marketplace identifier. When provided,
                marketplace-specific presentation rules are appended to the
                prompt after the reference-priority block. When None, the
                prompt passes through unchanged.

        Returns:
            An ``ImageGenerationResult`` with the generated image or last error.
        """
        # Shallow-copy context so we never mutate the caller's dict
        # (e.g. when overriding aspect_ratio for marketplace defaults).
        context = dict(context) if context else {}
        request_id = context.get("request_id", "unknown")
        has_reference = reference_image is not None

        if force_provider:
            provider_chain = [force_provider]
        else:
            provider_chain = self._get_provider_chain()

        # Spec: "Before sending prompt to image generator, automatically
        # append" the reference-priority block whenever the uploaded image is
        # present. The uploaded image is the single source of truth; the text
        # prompt must always tell the model to preserve it. Appended here so
        # EVERY provider (and every client path) receives the instruction.
        #
        # Guarded against duplication: PFIE-fused prompts already carry their
        # own reference-priority instruction, so we only append when the
        # marker is absent (non-fused / legacy clients). Note: when a provider
        # cannot receive the reference image (e.g. DALL-E text-only fallback),
        # the block still anchors the prompt to the caller-provided product
        # facts; that degraded path is acceptable and documented.
        effective_prompt = prompt
        if has_reference and "REFERENCE IMAGE PRIORITY" not in prompt.upper():
            effective_prompt = f"{prompt}\n\n{REFERENCE_PRIORITY_BLOCK}"
            logger.info(
                f"ImageGenerationManager: appended reference-priority "
                f"block request_id={request_id}"
            )

        # Marketplace presentation overlay: append marketplace-specific
        # presentation rules AFTER fidelity/reference-priority blocks so
        # marketplace rules never override product identity.
        if marketplace:
            marketplace_presentation = get_marketplace_presentation(marketplace)
            if marketplace_presentation:
                effective_prompt = (
                    f"{effective_prompt}\n\n"
                    f"{marketplace_presentation.prompt_block}"
                )
                logger.info(
                    f"ImageGenerationManager: appended marketplace "
                    f"presentation '{marketplace}' request_id={request_id}"
                )

                # Override aspect ratio with marketplace default if available.
                # This ensures marketplace-specific format requirements
                # (e.g. Amazon 1:1 square) are enforced backend-side,
                # regardless of what the frontend sent.
                if marketplace_presentation.default_aspect_ratio:
                    context["aspect_ratio"] = (
                        marketplace_presentation.default_aspect_ratio
                    )
                    logger.info(
                        f"ImageGenerationManager: marketplace '{marketplace}' "
                        f"overrides aspect_ratio to "
                        f"'{marketplace_presentation.default_aspect_ratio}' "
                        f"request_id={request_id}"
                    )

        logger.info(
            f"ImageGenerationManager: generating image "
            f"request_id={request_id} chain={provider_chain} "
            f"has_reference={has_reference}"
        )

        last_error: Optional[str] = None
        fallback_reason: Optional[str] = None
        provider_used: Optional[str] = None
        fallback_used = False

        for idx, provider_name in enumerate(provider_chain):
            provider = self._get_provider(provider_name)
            if provider is None:
                logger.warning(
                    f"Image provider '{provider_name}' not available, skipping"
                )
                continue

            if not provider.is_available:
                logger.info(
                    f"Image provider '{provider_name}' not configured, skipping"
                )
                continue

            is_fallback = idx > 0
            if is_fallback:
                logger.info(
                    f"Falling back to provider '{provider_name}' "
                    f"request_id={request_id} reason={fallback_reason}"
                )

            # Determine if this provider supports reference images
            provider_has_ref = has_reference and provider.supports_reference_image()
            if has_reference and not provider_has_ref:
                logger.info(
                    f"Provider '{provider_name}' does not support reference images, "
                    f"falling back to text-only prompt request_id={request_id}"
                )

            # Retry loop for this provider
            for attempt in range(self.MAX_RETRIES_PER_PROVIDER + 1):
                try:
                    if attempt > 0:
                        logger.info(
                            f"Retry {attempt}/{self.MAX_RETRIES_PER_PROVIDER} "
                            f"for provider '{provider_name}' "
                            f"request_id={request_id}"
                        )
                        await asyncio.sleep(self.RETRY_DELAY_SECONDS)

                    # Pass reference image if provider supports it
                    if provider_has_ref:
                        result = await provider.generate_image(
                            effective_prompt, context,
                            reference_image=reference_image,
                            reference_mime_type=reference_mime_type,
                        )
                    else:
                        result = await provider.generate_image(
                            effective_prompt, context
                        )

                    if result.success:
                        result.provider_name = provider_name
                        result.fallback_used = is_fallback
                        result.fallback_reason = fallback_reason

                        # Tag generation_mode in metadata so the frontend
                        # can distinguish primary, fallback, and manual switch.
                        if force_provider:
                            gen_mode = "manual_switch"
                        elif is_fallback:
                            gen_mode = "fallback"
                        else:
                            gen_mode = "primary"
                        meta = dict(result.metadata) if result.metadata else {}
                        meta["generation_mode"] = gen_mode
                        result.metadata = meta

                        logger.info(
                            f"ImageGenerationManager: success with "
                            f"provider '{provider_name}' "
                            f"mode={gen_mode} "
                            f"time={result.processing_time:.2f}s "
                            f"request_id={request_id}"
                        )
                        return result

                    # Provider returned failure — check if recoverable
                    error_msg = result.error or ""
                    last_error = error_msg

                    # Check if this is a non-recoverable error
                    if _is_non_recoverable_error(error_msg):
                        logger.warning(
                            f"Image provider '{provider_name}' returned "
                            f"non-recoverable error: {error_msg} "
                            f"request_id={request_id} — skipping fallback"
                        )
                        # Return immediately — no point trying other providers
                        return ImageGenerationResult(
                            success=False,
                            error=error_msg,
                            provider_name=provider_name,
                            processing_time=result.processing_time,
                            metadata={"non_recoverable": True},
                        )

                    # Check if recoverable — set fallback reason
                    if _is_recoverable_error(error_msg):
                        fallback_reason = f"{provider_name}_{_classify_error(error_msg)}"
                        logger.info(
                            f"Recoverable error from '{provider_name}': "
                            f"{error_msg} — will fallback if retries exhausted"
                        )
                    elif attempt < self.MAX_RETRIES_PER_PROVIDER:
                        # Unknown error — retry
                        logger.info(
                            f"Unknown error from '{provider_name}': "
                            f"{error_msg} — retrying"
                        )

                except Exception as e:
                    error_msg = str(e)
                    last_error = error_msg
                    logger.warning(
                        f"Image provider '{provider_name}' attempt "
                        f"{attempt + 1} exception: {error_msg} "
                        f"request_id={request_id}"
                    )

            # All retries exhausted for this provider
            if fallback_reason:
                # We have a fallback reason — continue to next provider
                logger.info(
                    f"Provider '{provider_name}' exhausted after "
                    f"{self.MAX_RETRIES_PER_PROVIDER + 1} attempt(s) — "
                    f"falling back. request_id={request_id}"
                )
            else:
                logger.warning(
                    f"Provider '{provider_name}' exhausted after "
                    f"{self.MAX_RETRIES_PER_PROVIDER + 1} attempt(s) "
                    f"request_id={request_id}"
                )

        # All providers failed
        logger.error(
            f"ImageGenerationManager: all providers failed "
            f"request_id={request_id} last_error={last_error}"
        )

        return ImageGenerationResult(
            success=False,
            error=last_error or "All image generation providers failed",
            provider_name=provider_used or "none",
            fallback_used=True,
            fallback_reason=fallback_reason,
        )

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Return a list of available image generation providers with status."""
        self._init_providers()
        result = []
        for name, provider in self._providers.items():
            result.append({
                "name": name,
                "version": provider.provider_version,
                "available": provider.is_available,
                "capabilities": provider.capabilities,
            })
        return result

    def get_provider_chain(self) -> List[str]:
        """Return the current provider chain order."""
        return self._get_provider_chain()


def _classify_error(error_message: str) -> str:
    """Classify an error message into a short reason code."""
    error_lower = error_message.lower()
    if any(t in error_lower for t in ["429", "quota", "rate", "resource exhausted"]):
        return "quota_exceeded"
    if any(t in error_lower for t in ["timeout", "deadline"]):
        return "timeout"
    if any(t in error_lower for t in ["unavailable", "503"]):
        return "service_unavailable"
    if any(t in error_lower for t in ["network", "connection", "reset"]):
        return "network_error"
    if any(t in error_lower for t in ["internal", "500", "502", "504", "5xx"]):
        return "server_error"
    return "transient_error"
