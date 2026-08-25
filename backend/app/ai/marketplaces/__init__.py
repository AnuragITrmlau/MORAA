"""Marketplace Presentation Layer — GemVision.

Marketplace-specific presentation rules that compose with (but never
override) the Master Product Fidelity layer.

Architecture::

    MASTER PRODUCT FIDELITY  (product_fidelity.py — LOCKED)
            +
    MARKETPLACE PRESENTATION  (this package)

Each marketplace module defines presentation-only instructions:
background, composition, framing, lighting, and exclusion lists.

Marketplace rules MUST NOT redefine product identity (stones, metal,
geometry, proportions, decorative elements, or product design).

Usage::

    from app.ai.marketplaces.registry import get_marketplace_presentation

    presentation = get_marketplace_presentation("amazon_india_fashion_earrings")
    if presentation:
        # append presentation.prompt_block to the image-generation prompt
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class MarketPlacePresentation:
    """Lightweight container for a marketplace's presentation rules.

    Attributes:
        marketplace_id: Unique identifier (e.g. ``"amazon_india_fashion_earrings"``).
        prompt_block: The text instruction block appended to image-generation
            prompts when this marketplace is active. Must contain ONLY
            presentation/compliance rules — never product-identity rules.
        default_aspect_ratio: Recommended aspect ratio for this marketplace
            (e.g. ``"1:1"`` for Amazon main images).
        metadata: Arbitrary metadata (marketplace name, category, image type,
            rule counts, etc.).
    """

    marketplace_id: str
    prompt_block: str
    default_aspect_ratio: str = "1:1"
    metadata: Dict[str, Any] = field(default_factory=dict)
