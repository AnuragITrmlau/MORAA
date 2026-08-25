"""Marketplace Presentation Registry — GemVision.

Maps marketplace string identifiers to their ``MarketPlacePresentation``
definitions.  The ``ImageGenerationManager`` calls
``get_marketplace_presentation()`` to look up and append marketplace-specific
presentation rules to the image-generation prompt.

Unknown marketplace IDs return ``None`` safely — no exceptions.
"""

from typing import Optional

from app.ai.marketplaces import MarketPlacePresentation
from app.ai.marketplaces.amazon_india import AMAZON_INDIA_EARRINGS_MAIN_IMAGE


# ─── Registry ───────────────────────────────────────────────────────────

_MARKETPLACE_REGISTRY: dict[str, MarketPlacePresentation] = {
    AMAZON_INDIA_EARRINGS_MAIN_IMAGE.marketplace_id: AMAZON_INDIA_EARRINGS_MAIN_IMAGE,
}


def get_marketplace_presentation(
    marketplace_id: Optional[str],
) -> Optional[MarketPlacePresentation]:
    """Look up a marketplace presentation by its identifier.

    Args:
        marketplace_id: The marketplace identifier
            (e.g. ``"amazon_india_fashion_earrings"``).

    Returns:
        The ``MarketPlacePresentation`` if found, or ``None`` if the
        identifier is ``None``, empty, or unknown.
    """
    if not marketplace_id:
        return None

    return _MARKETPLACE_REGISTRY.get(marketplace_id)
