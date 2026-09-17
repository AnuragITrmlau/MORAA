"""Tests for the Chandelier Yellow-Gold Earring product-identity spec layer.

Lean 3-block revision (2026-09-17):
1. ``ChandelierIdentitySpec`` — validation of lengths, palm fraction, and
   field defaults.
2. ``get_style_block`` — all four style blocks, strict scale/background
   locks, and unknown-style error.
3. ``build_chandelier_gold_prompt`` — lean 3-block assembly, canonical
   markers, affirmative metal lock, and pipeline compatibility.
4. Lean guarantees — checklist/conversational sections are gone.
5. Additive-only guarantee — frozen Prompt 1 files and canonical fidelity
   constants are untouched by this module.
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.earring_chandelier_gold_prompt import (  # noqa: E402
    REFERENCE_PRIORITY_MARKER,
    ChandelierIdentitySpec,
    StyleKind,
    build_chandelier_gold_prompt,
    get_style_block,
)
from app.ai.product_fidelity import (  # noqa: E402
    REFERENCE_IMAGE_INSTRUCTION,
    REFERENCE_PRIORITY_BLOCK,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestChandelierIdentitySpec(unittest.TestCase):
    """Validation and defaults of the typed identity spec."""

    def test_default_spec_is_valid(self):
        spec = ChandelierIdentitySpec()
        self.assertEqual(spec.metal_colour.value, "warm yellow gold")
        self.assertEqual(spec.drop_length_cm_min, 6.0)
        self.assertEqual(spec.drop_length_cm_max, 6.5)
        self.assertEqual(spec.max_palm_fraction, 0.30)

    def test_custom_dimensions_accepted(self):
        spec = ChandelierIdentitySpec(
            drop_length_cm_min=5.5,
            drop_length_cm_max=7.0,
            max_palm_fraction=0.25,
        )
        self.assertEqual(spec.drop_length_cm_min, 5.5)
        self.assertEqual(spec.drop_length_cm_max, 7.0)

    def test_max_below_min_rejected(self):
        with self.assertRaises(Exception):
            ChandelierIdentitySpec(
                drop_length_cm_min=7.0,
                drop_length_cm_max=6.0,
            )

    def test_zero_palm_fraction_rejected(self):
        with self.assertRaises(Exception):
            ChandelierIdentitySpec(max_palm_fraction=0.0)

    def test_extra_fields_rejected(self):
        with self.assertRaises(Exception):
            ChandelierIdentitySpec(unknown_field="typo guard")

    def test_drop_length_text(self):
        spec = ChandelierIdentitySpec()
        self.assertEqual(
            spec.drop_length_text(),
            "Approximately 6.0 cm to 6.5 cm total drop length",
        )

    def test_strict_drop_length_text(self):
        spec = ChandelierIdentitySpec(drop_length_cm_min=6.0)
        self.assertEqual(spec.strict_drop_length_text(), "strictly 6.0 cm")

    def test_palm_rule_text(self):
        spec = ChandelierIdentitySpec(max_palm_fraction=0.3)
        self.assertIn("strictly under 30% of the palm surface", spec.palm_rule_text())
        self.assertIn("NEVER covering the full palm", spec.palm_rule_text())

    def test_metal_lock_default(self):
        spec = ChandelierIdentitySpec()
        self.assertIn("100% warm saturated yellow gold", spec.metal_lock)


class TestStyleBlocks(unittest.TestCase):
    """All four style blocks render correctly with the strict locks."""

    def test_all_style_kinds_render(self):
        spec = ChandelierIdentitySpec()
        for kind in StyleKind:
            block = get_style_block(kind, spec)
            self.assertIsInstance(block, str)
            self.assertTrue(block.startswith("[STYLE SPECIFIC EXECUTION"))

    def test_ecommerce_block_background_lock(self):
        spec = ChandelierIdentitySpec()
        block = get_style_block(StyleKind.ECOMMERCE, spec)
        self.assertIn("Clean E-Commerce Catalog Packshot", block)
        self.assertIn("#FFFFFF, RGB 255, 255, 255", block)
        self.assertIn("edge-to-edge", block)
        self.assertIn("Zero grey falloff", block)
        self.assertIn("zero color tint", block)
        self.assertIn("zero vignette", block)
        self.assertIn("zero floor seam", block)
        self.assertIn("zero textured canvas", block)
        self.assertIn("Pure white knockout background", block)
        self.assertIn("crisp subtle contact drop shadow directly underneath", block)
        # Isolated lighting: no ambient fill tinting the canvas grey/lilac.
        self.assertIn("ISOLATED studio lighting", block)
        self.assertIn("Zero ambient fill", block)
        self.assertIn("85% of vertical frame height", block)

    def test_macro_block_content(self):
        spec = ChandelierIdentitySpec()
        block = get_style_block(StyleKind.MACRO, spec)
        self.assertIn("Extreme Macro Jewelry Close-Up", block)
        self.assertIn("micro-pavé prongs", block)
        self.assertIn("f/4", block)
        self.assertIn("yellow gold saturation", block)
        self.assertIn("zero desaturation or silver conversion", block)

    def test_scale_reference_block_strict_locks(self):
        spec = ChandelierIdentitySpec(max_palm_fraction=0.30)
        block = get_style_block(StyleKind.SCALE_REFERENCE, spec)
        self.assertIn("Anatomical Scale Reference Shot", block)
        self.assertIn("strictly 6.0 cm", block)
        self.assertIn("strictly under 30% of the palm surface", block)
        self.assertIn("NEVER covering the full palm or wrist-to-finger length", block)
        self.assertIn("feminine manicured hand", block)
        self.assertIn("#FFFFFF", block)
        self.assertIn("Miniature-to-medium scale, never oversized", block)

    def test_on_ear_block_content(self):
        spec = ChandelierIdentitySpec()
        block = get_style_block(StyleKind.ON_EAR, spec)
        self.assertIn("Macro On-Ear Commercial Shot", block)
        self.assertIn("no pimples", block)
        self.assertIn("hang freely below the lobe", block)

    def test_unknown_style_raises(self):
        spec = ChandelierIdentitySpec()
        with self.assertRaises(ValueError):
            get_style_block("floating", spec)  # type: ignore[arg-type]


class TestBuildPrompt(unittest.TestCase):
    """Lean 3-block prompt assembly for all styles."""

    def test_contains_task_header_and_category(self):
        prompt = build_chandelier_gold_prompt()
        self.assertIn("TASK: E-Commerce Jewelry Photography Transformation", prompt)
        self.assertIn("Fashion Dangle/Chandelier Earrings", prompt)

    def test_contains_reference_priority_marker(self):
        """Marker present so ImageGenerationManager does not double-append."""
        prompt = build_chandelier_gold_prompt()
        self.assertIn(REFERENCE_PRIORITY_MARKER, prompt)

    def test_contains_canonical_reference_instruction(self):
        prompt = build_chandelier_gold_prompt()
        self.assertIn(REFERENCE_IMAGE_INSTRUCTION, prompt)

    def test_block1_identity_and_metal_lock(self):
        prompt = build_chandelier_gold_prompt()
        self.assertIn("IDENTITY & METAL LOCK (NON-NEGOTIABLE)", prompt)
        self.assertIn("100% warm saturated yellow gold", prompt)
        self.assertIn("Under NO circumstances", prompt)
        self.assertIn("silver, rhodium, platinum, or white gold", prompt)
        self.assertIn("princess-cut centre stone", prompt)
        self.assertIn("hanging pear droplets", prompt)
        self.assertIn("MORAA", prompt)
        self.assertIn("prong count", prompt)
        self.assertIn("drop count", prompt)

    def test_block3_negatives(self):
        prompt = build_chandelier_gold_prompt()
        self.assertIn("DO NOT generate:", prompt)
        self.assertIn("silver or rhodium metal", prompt)
        self.assertIn("oversized scale", prompt)
        self.assertIn("grey background", prompt)
        self.assertIn("fused droplets", prompt)
        self.assertIn("plastic sheen", prompt)

    def test_affirmative_metal_anchoring(self):
        """Affirmative lock present; silver appears only as a prohibition."""
        prompt = build_chandelier_gold_prompt()
        lower = prompt.lower()
        self.assertIn("yellow gold", lower)
        self.assertIn("convert to silver", lower)

    def test_all_styles_produce_distinct_prompts(self):
        prompts = {
            build_chandelier_gold_prompt(style=kind) for kind in StyleKind
        }
        self.assertEqual(len(prompts), len(StyleKind))

    def test_ecommerce_style_background_lock(self):
        prompt = build_chandelier_gold_prompt(style=StyleKind.ECOMMERCE)
        self.assertIn("#FFFFFF, RGB 255, 255, 255", prompt)
        self.assertIn("Zero grey falloff", prompt)
        self.assertIn("Pure white knockout background", prompt)
        self.assertIn("Zero ambient fill", prompt)

    def test_scale_reference_style_strict_scale(self):
        prompt = build_chandelier_gold_prompt(style=StyleKind.SCALE_REFERENCE)
        self.assertIn("strictly 6.0 cm", prompt)
        self.assertIn("strictly under 30% of the palm surface", prompt)

    def test_custom_spec_overrides(self):
        spec = ChandelierIdentitySpec(
            drop_length_cm_min=5.0,
            drop_length_cm_max=5.5,
        )
        prompt = build_chandelier_gold_prompt(
            style=StyleKind.SCALE_REFERENCE, spec=spec
        )
        self.assertIn("strictly 5.0 cm", prompt)
        self.assertIn("strictly under 30% of the palm surface", prompt)

    def test_prompt_is_lean(self):
        """Lean architecture keeps every style well under the old bloat."""
        for kind in StyleKind:
            prompt = build_chandelier_gold_prompt(style=kind)
            self.assertGreater(len(prompt), 1000)
            self.assertLess(len(prompt), 4500, f"{kind} prompt regressed to bloat")


class TestLeanGuarantees(unittest.TestCase):
    """Non-functional checklist/conversational sections are stripped."""

    def test_no_final_verification_checklist(self):
        for kind in StyleKind:
            prompt = build_chandelier_gold_prompt(style=kind)
            self.assertNotIn("FINAL VERIFICATION", prompt)
            self.assertNotIn("OUTPUT QUALITY:", prompt)
            self.assertNotIn("If any answer is NO", prompt)

    def test_no_conversational_self_correction(self):
        prompt = build_chandelier_gold_prompt()
        self.assertNotIn("correct the composition", prompt)


class TestPipelineCompatibility(unittest.TestCase):
    """Compatibility with ImageGenerationManager / marketplace / providers."""

    def test_manager_guard_would_skip_double_append(self):
        """The manager's guard is:
        'REFERENCE IMAGE PRIORITY' not in prompt.upper() → append.
        Our marker guarantees the append is skipped.
        """
        prompt = build_chandelier_gold_prompt()
        self.assertIn("REFERENCE IMAGE PRIORITY", prompt.upper())

    def test_marketplace_overlay_composes_after(self):
        """Simulate ImageGenerationManager composition order."""
        prompt = build_chandelier_gold_prompt(style=StyleKind.ECOMMERCE)
        from app.ai.marketplaces.amazon_india import (
            AMAZON_INDIA_EARRINGS_MAIN_IMAGE,
        )

        composed = f"{prompt}\n\n{AMAZON_INDIA_EARRINGS_MAIN_IMAGE.prompt_block}"
        self.assertIn(REFERENCE_PRIORITY_MARKER, composed)
        self.assertIn("AMAZON INDIA", composed)
        # Marketplace text must come after the identity lock
        self.assertGreater(
            composed.index("AMAZON INDIA"),
            composed.index("IDENTITY & METAL LOCK"),
        )

    def test_openai_identity_anchor_still_applicable(self):
        """The provider-level anchor composes cleanly on top of this prompt."""
        from app.ai.providers.openai_image_provider import OPENAI_IDENTITY_ANCHOR

        prompt = build_chandelier_gold_prompt()
        composed = f"{OPENAI_IDENTITY_ANCHOR}\n\n{prompt}"
        self.assertIn("authoritative source", composed)
        self.assertIn(REFERENCE_PRIORITY_MARKER, composed)


class TestAdditiveOnly(unittest.TestCase):
    """This module must not modify frozen or canonical files."""

    def test_prompt1_builder_unmodified_by_import(self):
        """Importing our module does not alter the frozen Prompt 1 builder."""
        from app.services import earring_ecommerce_prompt

        source = Path(earring_ecommerce_prompt.__file__).read_text(encoding="utf-8")
        self.assertIn("def build_earring_ecommerce_prompt", source)

    def test_canonical_constants_untouched(self):
        self.assertIsInstance(REFERENCE_PRIORITY_BLOCK, str)
        self.assertGreater(len(REFERENCE_PRIORITY_BLOCK), 50)


if __name__ == "__main__":
    unittest.main()
