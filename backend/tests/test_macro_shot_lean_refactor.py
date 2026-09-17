"""Regression tests for the lean macro shot prompt refactor (2026-09-17).

Guards against reintroduction of the silver-hallucination root cause:
listing `silver/white-gold appearance` as a preserve target in
``earring_macro_shot_prompt.py`` primed diffusion models to render gold
earrings as silver at macro scale.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.earring_macro_shot_prompt import (  # noqa: E402
    METAL_AFFIRMATION_INSTRUCTION,
    REFERENCE_PRIORITY_MARKER,
    build_macro_shot_prompt,
)


class TestMacroLeanRefactor(unittest.TestCase):
    """The macro prompt must affirmatively lock yellow gold."""

    def test_silver_preserve_line_removed(self):
        """ROOT CAUSE: '- silver/white-gold appearance' must never return."""
        prompt = build_macro_shot_prompt()
        self.assertNotIn("silver/white-gold appearance", prompt)
        self.assertNotIn("silver/white-gold", prompt)

    def test_affirmative_yellow_gold_lock_present(self):
        prompt = build_macro_shot_prompt()
        self.assertIn("METAL AFFIRMATION", prompt)
        self.assertIn("100% WARM YELLOW GOLD", prompt)
        self.assertIn("rich saturated yellow gold", prompt)

    def test_silver_appears_only_as_prohibition(self):
        prompt = build_macro_shot_prompt().lower()
        self.assertIn("make yellow gold appear silver", prompt)
        self.assertIn("silver or rhodium metal", prompt)

    def test_marker_present_unchanged(self):
        prompt = build_macro_shot_prompt()
        self.assertIn(REFERENCE_PRIORITY_MARKER, prompt)

    def test_signature_and_return_type_unchanged(self):
        """No-arg call must work (WhatsApp pipeline calls it bare)."""
        result = build_macro_shot_prompt()
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 500)

    def test_earring_type_contract_preserved(self):
        for kind in ("Hoop", "Stud", "Dangle"):
            result = build_macro_shot_prompt(earring_type=kind)
            self.assertIsInstance(result, str)
            self.assertIn(kind.upper(), result)

    def test_checklist_stripped(self):
        prompt = build_macro_shot_prompt()
        self.assertNotIn("FINAL VERIFICATION", prompt)
        self.assertNotIn("correct the composition", prompt)

    def test_validated_constants_retained(self):
        """Proven preservation constants still compose into the prompt."""
        prompt = build_macro_shot_prompt()
        self.assertIn("ANTI-SYMMETRY", prompt)
        self.assertIn("COLOUR LOCK", prompt)
        self.assertIn("MATERIAL & COLOUR FIDELITY", prompt)

    def test_prompt_is_lean(self):
        prompt = build_macro_shot_prompt()
        self.assertLess(len(prompt), 8000, "macro prompt regressed to bloat")

    def test_metal_affirmation_constant_content(self):
        self.assertIn("100% WARM YELLOW GOLD", METAL_AFFIRMATION_INSTRUCTION)
        self.assertIn("zero desaturation", METAL_AFFIRMATION_INSTRUCTION)
        self.assertIn("specular highlight blowouts", METAL_AFFIRMATION_INSTRUCTION)

    # ── Extreme-macro crop fix (catalog still-life failure, 2026-09-17) ──

    def test_tight_macro_crop_framing_present(self):
        """The prompt must demand a single tight focal section, optics included."""
        prompt = build_macro_shot_prompt()
        self.assertIn("TIGHT MACRO CROP", prompt)
        self.assertIn("extreme close-up of a single emerald-cut stone", prompt)
        self.assertIn("adjacent marquise leaf facets filling 85% of the frame", prompt)
        self.assertIn("100mm macro lens at f/2.8", prompt)
        self.assertIn("extreme shallow depth of field", prompt)

    def test_full_earring_framing_declared_direct_failure(self):
        prompt = build_macro_shot_prompt()
        self.assertIn("Do NOT show the full earring", prompt)
        self.assertIn("Do NOT show both earrings", prompt)
        self.assertIn("Full earrings in frame is a direct task failure", prompt)

    def test_catalog_still_life_negatives_present(self):
        prompt = build_macro_shot_prompt()
        self.assertIn("full earring pair in frame", prompt)
        self.assertIn("entire earring visible", prompt)
        self.assertIn("catalog still-life framing", prompt)
        self.assertIn("earring photographed on cloth", prompt)

    def test_zoom_out_clause_removed(self):
        """ROOT CAUSE: the 'inspect everything' clause forced the zoom-out."""
        prompt = build_macro_shot_prompt()
        self.assertNotIn("all jewellery components stay sharp and inspectable", prompt)
        self.assertNotIn("TASK: Macro Shot.", prompt)
        self.assertIn("TASK: Extreme Macro Jewelry Close-Up Photography.", prompt)


if __name__ == "__main__":
    unittest.main()
