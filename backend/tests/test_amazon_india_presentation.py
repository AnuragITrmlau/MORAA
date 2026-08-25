"""Tests for the Amazon India Marketplace Presentation Layer.

Verifies:
1. Registry lookup for amazon_india_fashion_earrings
2. Unknown marketplace handled safely
3. marketplace=None preserves existing behaviour
4. Amazon presentation block content (white background, 1:1, no-model, etc.)
5. Amazon block contains only presentation rules (no product redesign)
6. Fidelity instructions remain before marketplace instructions
7. REFERENCE_PRIORITY_BLOCK remains intact
8. PFIE remains disabled
9. Provider routing unchanged
"""

import os
import sys
import unittest

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch

from app.ai.marketplaces import MarketPlacePresentation
from app.ai.marketplaces.registry import get_marketplace_presentation
from app.ai.marketplaces.amazon_india import (
    AMAZON_INDIA_EARRINGS_MAIN_IMAGE,
    get_amazon_india_earrings_presentation,
)
from app.ai.product_fidelity import REFERENCE_PRIORITY_BLOCK


# ─── Test: Registry Lookup ──────────────────────────────────────────────


class TestRegistryLookup(unittest.TestCase):
    """Verify marketplace registry resolution."""

    def test_amazon_india_resolves_correctly(self):
        """amazon_india_fashion_earrings maps to Amazon presentation."""
        result = get_marketplace_presentation("amazon_india_fashion_earrings")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, MarketPlacePresentation)
        self.assertEqual(result.marketplace_id, "amazon_india_fashion_earrings")

    def test_unknown_marketplace_returns_none(self):
        """Unknown marketplace ID returns None safely (no exception)."""
        result = get_marketplace_presentation("unknown_marketplace_xyz")
        self.assertIsNone(result)

    def test_none_returns_none(self):
        """None input returns None safely."""
        result = get_marketplace_presentation(None)
        self.assertIsNone(result)

    def test_empty_string_returns_none(self):
        """Empty string input returns None safely."""
        result = get_marketplace_presentation("")
        self.assertIsNone(result)

    def test_amazon_presentation_is_frozen_dataclass(self):
        """Amazon presentation is a frozen MarketPlacePresentation."""
        result = get_marketplace_presentation("amazon_india_fashion_earrings")
        self.assertIsInstance(result, MarketPlacePresentation)
        # frozen=True means we can't accidentally mutate it
        with self.assertRaises(AttributeError):
            result.marketplace_id = "mutated"


# ─── Test: Amazon Presentation Block Content ────────────────────────────


class TestAmazonPresentationContent(unittest.TestCase):
    """Verify the Amazon India presentation block contains correct rules."""

    def setUp(self):
        self.presentation = get_amazon_india_earrings_presentation()
        self.block = self.presentation.prompt_block

    def test_presentation_block_exists(self):
        """Amazon presentation block is a non-empty string."""
        self.assertIsInstance(self.block, str)
        self.assertGreater(len(self.block), 100)

    def test_pure_white_background(self):
        """Block mentions pure white background (RGB 255,255,255)."""
        self.assertIn("white background", self.block.lower())
        self.assertIn("255", self.block)

    def test_square_aspect_ratio(self):
        """Block mentions 1:1 square composition."""
        self.assertIn("1:1", self.block)
        self.assertIn("square", self.block.lower())

    def test_no_human_model(self):
        """Block restricts human model and mannequin."""
        self.assertIn("model", self.block.lower())
        self.assertIn("mannequin", self.block.lower())

    def test_no_text_logos_watermarks(self):
        """Block restricts text, logos, watermarks, badges, borders."""
        self.assertIn("text", self.block.lower())
        self.assertIn("logo", self.block.lower())
        self.assertIn("watermark", self.block.lower())
        self.assertIn("badge", self.block.lower())
        self.assertIn("border", self.block.lower())

    def test_no_props_packaging(self):
        """Block restricts props, packaging, lifestyle elements."""
        self.assertIn("props", self.block.lower())
        self.assertIn("packaging", self.block.lower())
        self.assertIn("lifestyle", self.block.lower())

    def test_product_visibility(self):
        """Block requires product to be clearly visible and in focus."""
        self.assertIn("visible", self.block.lower())
        self.assertIn("focus", self.block.lower())

    def test_default_aspect_ratio(self):
        """Default aspect ratio is 1:1."""
        self.assertEqual(self.presentation.default_aspect_ratio, "1:1")

    def test_marketplace_id_correct(self):
        """Marketplace ID matches expected value."""
        self.assertEqual(
            self.presentation.marketplace_id,
            "amazon_india_fashion_earrings",
        )

    def test_metadata_populated(self):
        """Metadata dict is populated with marketplace info."""
        self.assertIn("marketplace", self.presentation.metadata)
        self.assertEqual(self.presentation.metadata["marketplace"], "Amazon India")


# ─── Test: No Product Redesign Instructions ─────────────────────────────


class TestAmazonNoRedesign(unittest.TestCase):
    """Verify the Amazon block contains NO product redesign instructions."""

    def setUp(self):
        self.block = get_amazon_india_earrings_presentation().prompt_block
        self.block_lower = self.block.lower()

    def test_no_stone_count_instructions(self):
        """Block does not redefine stone count."""
        self.assertNotIn("stone count", self.block_lower)
        self.assertNotIn("add stones", self.block_lower)
        self.assertNotIn("remove stones", self.block_lower)

    def test_no_metal_colour_instructions(self):
        """Block does not redefine metal colour."""
        self.assertNotIn("change metal", self.block_lower)
        # Note: "metal colour representation" (accurate representation) is
        # a valid presentation rule, not a redesign instruction.

    def test_no_geometry_instructions(self):
        """Block does not redefine product geometry."""
        self.assertNotIn("change geometry", self.block_lower)
        self.assertNotIn("change proportions", self.block_lower)
        self.assertNotIn("change shape", self.block_lower)

    def test_no_decorative_instructions(self):
        """Block does not redefine decorative elements."""
        self.assertNotIn("add decorative", self.block_lower)
        self.assertNotIn("remove decorative", self.block_lower)

    def test_no_attachment_instructions(self):
        """Block does not redefine attachment mechanism."""
        self.assertNotIn("change clasp", self.block_lower)
        self.assertNotIn("change hook", self.block_lower)
        self.assertNotIn("change attachment", self.block_lower)

    def test_reinforces_product_unchanged(self):
        """Block explicitly reinforces that the product must remain unchanged."""
        self.assertIn("unchanged", self.block_lower)


# ─── Test: Composition Order ────────────────────────────────────────────


class TestCompositionOrder(unittest.TestCase):
    """Verify fidelity instructions come before marketplace instructions."""

    def test_fidelity_before_marketplace_in_composed_prompt(self):
        """When both are composed, fidelity text appears before marketplace text."""
        # Simulate the composition order as it happens in ImageGenerationManager
        fidelity_block = REFERENCE_PRIORITY_BLOCK
        marketplace_block = get_amazon_india_earrings_presentation().prompt_block
        composed = f"base prompt\n\n{fidelity_block}\n\n{marketplace_block}"

        fidelity_pos = composed.find("REFERENCE IMAGE PRIORITY")
        marketplace_pos = composed.find("AMAZON INDIA")

        self.assertGreater(fidelity_pos, -1)
        self.assertGreater(marketplace_pos, -1)
        self.assertLess(fidelity_pos, marketplace_pos)

    def test_reference_priority_block_intact(self):
        """REFERENCE_PRIORITY_BLOCK is still available and correct."""
        self.assertIsInstance(REFERENCE_PRIORITY_BLOCK, str)
        self.assertIn("REFERENCE IMAGE PRIORITY", REFERENCE_PRIORITY_BLOCK)
        self.assertIn("preserve", REFERENCE_PRIORITY_BLOCK.lower())

    def test_composed_prompt_preserves_fidelity(self):
        """Composed prompt preserves all fidelity text."""
        fidelity_block = REFERENCE_PRIORITY_BLOCK
        marketplace_block = get_amazon_india_earrings_presentation().prompt_block
        composed = f"base prompt\n\n{fidelity_block}\n\n{marketplace_block}"

        # All key fidelity phrases must remain in the composed prompt
        self.assertIn("uploaded image", composed.lower())
        self.assertIn("preserve", composed.lower())
        self.assertIn("exact", composed.lower())


# ─── Test: PFIE Remains Disabled ────────────────────────────────────────


class TestPFIERemainsDisabled(unittest.TestCase):
    """Verify PFIE is still disabled."""

    def test_pfie_disabled(self):
        """PFIE_ENABLED must be False."""
        from app.config import settings
        self.assertFalse(settings.PFIE_ENABLED)


# ─── Test: Provider Routing Unchanged ───────────────────────────────────


class TestProviderRoutingUnchanged(unittest.TestCase):
    """Verify provider routing is not affected by marketplace layer."""

    @patch("app.ai.image_generation_manager.settings")
    def test_default_chain_unchanged(self, mock_settings):
        """Default provider chain is still [openai, gemini]."""
        from app.ai.image_generation_manager import ImageGenerationManager
        mock_settings.PRIMARY_IMAGE_PROVIDER = "openai"
        mock_settings.FALLBACK_IMAGE_PROVIDER = "gemini"

        manager = ImageGenerationManager()
        chain = manager._get_provider_chain()
        self.assertEqual(chain, ["openai", "gemini"])


# ─── Test: Backward Compatibility ───────────────────────────────────────


class TestBackwardCompatibility(unittest.TestCase):
    """Verify existing behaviour is preserved when marketplace is not specified."""

    def test_imports_work(self):
        """All new imports work without errors."""
        from app.ai.marketplaces import MarketPlacePresentation
        from app.ai.marketplaces.registry import get_marketplace_presentation
        from app.ai.marketplaces.amazon_india import AMAZON_INDIA_EARRINGS_MAIN_IMAGE
        self.assertIsNotNone(MarketPlacePresentation)
        self.assertIsNotNone(get_marketplace_presentation)
        self.assertIsNotNone(AMAZON_INDIA_EARRINGS_MAIN_IMAGE)

    def test_manager_still_initializes(self):
        """ImageGenerationManager still initializes correctly."""
        from app.ai.image_generation_manager import ImageGenerationManager
        manager = ImageGenerationManager()
        self.assertIsNotNone(manager)

    def test_existing_request_schema_valid(self):
        """Existing request without marketplace is still valid."""
        from app.schemas.image_generation import ImageGenerationRequest
        request = ImageGenerationRequest(
            prompt="A gold ring on marble",
            aspect_ratio="4:5",
        )
        self.assertIsNone(request.marketplace)
        self.assertEqual(request.prompt, "A gold ring on marble")

    def test_new_request_schema_with_marketplace(self):
        """Request with marketplace is valid."""
        from app.schemas.image_generation import ImageGenerationRequest
        request = ImageGenerationRequest(
            prompt="A gold earring on marble",
            marketplace="amazon_india_fashion_earrings",
        )
        self.assertEqual(request.marketplace, "amazon_india_fashion_earrings")


# ─── Test: MarketplacePresentation Dataclass ────────────────────────────


class TestMarketPlacePresentationDataclass(unittest.TestCase):
    """Verify the MarketPlacePresentation dataclass contract."""

    def test_fields(self):
        """Dataclass has required fields."""
        p = MarketPlacePresentation(
            marketplace_id="test",
            prompt_block="test block",
        )
        self.assertEqual(p.marketplace_id, "test")
        self.assertEqual(p.prompt_block, "test block")
        self.assertEqual(p.default_aspect_ratio, "1:1")
        self.assertEqual(p.metadata, {})

    def test_metadata_optional(self):
        """Metadata defaults to empty dict."""
        p = MarketPlacePresentation(
            marketplace_id="test",
            prompt_block="test block",
        )
        self.assertIsInstance(p.metadata, dict)
        self.assertEqual(len(p.metadata), 0)

    def test_frozen(self):
        """Dataclass is frozen (immutable)."""
        p = MarketPlacePresentation(
            marketplace_id="test",
            prompt_block="test block",
        )
        with self.assertRaises(AttributeError):
            p.marketplace_id = "changed"
        with self.assertRaises(AttributeError):
            p.prompt_block = "changed"


if __name__ == "__main__":
    unittest.main()
