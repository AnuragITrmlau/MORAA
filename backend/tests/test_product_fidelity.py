"""Tests for the Master Product Fidelity module.

Verifies:
1. ProductFidelity model creation and validation
2. Fidelity instruction generation (generic and specific)
3. Fidelity QA evaluation
4. Reference priority instruction inclusion
5. Backward compatibility of re-exported constants
"""

import os
import sys
import unittest

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ai.product_fidelity import (
    GENERIC_FIDELITY_INSTRUCTION,
    PRODUCT_PRESERVATION_CONSTRAINTS,
    PRODUCT_PRESERVATION_BLOCK,
    REFERENCE_IMAGE_ANCHOR,
    REFERENCE_IMAGE_INSTRUCTION,
    REFERENCE_PRIORITY_BLOCK,
    REFERENCE_PRIORITY_INSTRUCTION,
    SCALE_CONTROL_BLOCK,
    FidelityAttachment,
    FidelityDecorative,
    FidelityMetal,
    FidelityProportions,
    FidelityQAResult,
    FidelityStone,
    ProductFidelity,
    build_fidelity_instruction,
    evaluate_fidelity,
)


# ─── Test: ProductFidelity Model ────────────────────────────────────────


class TestProductFidelityModel(unittest.TestCase):
    """Verify the ProductFidelity Pydantic model."""

    def test_empty_model(self):
        """An empty fidelity model is valid — all fields optional."""
        f = ProductFidelity()
        self.assertIsNone(f.product_type)
        self.assertIsNone(f.stones)
        self.assertIsNone(f.metal)

    def test_full_model(self):
        """A fully populated model stores all fidelity attributes."""
        f = ProductFidelity(
            product_type="Earring",
            quantity="pair",
            design_summary="Gold jhumka with red stones",
            total_stone_count=12,
            stones=[
                FidelityStone(count=12, shape="round", colour="red", placement="body"),
            ],
            metal=FidelityMetal(colour="yellow gold", appearance="polished"),
            proportions=FidelityProportions(overall_geometry="bell-shaped"),
            attachment=FidelityAttachment(type="hook", visible=True),
            decorative=FidelityDecorative(
                elements=["filigree", "granulation"],
                surface_texture="textured",
                symmetry="symmetric",
            ),
            unknown_details=["back clasp type unclear"],
            avoid_errors=["do not add gemstones to the dome"],
        )
        self.assertEqual(f.product_type, "Earring")
        self.assertEqual(f.quantity, "pair")
        self.assertEqual(f.total_stone_count, 12)
        self.assertEqual(len(f.stones), 1)
        self.assertEqual(f.metal.colour, "yellow gold")
        self.assertEqual(len(f.decorative.elements), 2)

    def test_partial_model(self):
        """A model with only some fields populated is valid."""
        f = ProductFidelity(
            product_type="Ring",
            metal=FidelityMetal(colour="rose gold"),
        )
        self.assertEqual(f.product_type, "Ring")
        self.assertEqual(f.metal.colour, "rose gold")
        self.assertIsNone(f.stones)
        self.assertIsNone(f.proportions)


# ─── Test: Fidelity Instruction Generation ──────────────────────────────


class TestBuildFidelityInstruction(unittest.TestCase):
    """Verify the fidelity instruction builder."""

    def test_none_returns_generic(self):
        """When fidelity is None, returns the generic instruction."""
        result = build_fidelity_instruction(None)
        self.assertEqual(result, GENERIC_FIDELITY_INSTRUCTION)
        self.assertIn("NON-NEGOTIABLE", result)
        self.assertIn("reference image", result.lower())

    def test_empty_model_returns_fidelity_header(self):
        """When fidelity has no fields populated, returns fidelity header + reference priority."""
        result = build_fidelity_instruction(ProductFidelity())
        self.assertIn("PRODUCT FIDELITY", result)
        self.assertIn("REFERENCE IMAGE PRIORITY", result)

    def test_includes_product_type(self):
        """Instruction includes the product type when known."""
        f = ProductFidelity(product_type="Earring", quantity="pair")
        result = build_fidelity_instruction(f)
        self.assertIn("Earring", result)
        self.assertIn("pair", result)

    def test_includes_stone_count(self):
        """Instruction includes total stone count."""
        f = ProductFidelity(total_stone_count=7)
        result = build_fidelity_instruction(f)
        self.assertIn("Total stone count: 7", result)

    def test_includes_stone_details(self):
        """Instruction includes stone shape, colour, and placement."""
        f = ProductFidelity(
            stones=[
                FidelityStone(
                    count=6,
                    shape="round",
                    colour="red",
                    placement="around the dome",
                    setting="prong",
                ),
            ]
        )
        result = build_fidelity_instruction(f)
        self.assertIn("round", result)
        self.assertIn("red", result)
        self.assertIn("around the dome", result)
        self.assertIn("prong", result)

    def test_includes_metal_colour(self):
        """Instruction includes metal colour."""
        f = ProductFidelity(metal=FidelityMetal(colour="rose gold"))
        result = build_fidelity_instruction(f)
        self.assertIn("rose gold", result)

    def test_includes_proportions(self):
        """Instruction includes geometry and proportions."""
        f = ProductFidelity(
            proportions=FidelityProportions(
                overall_geometry="teardrop",
                length_width_relationship="elongated",
            )
        )
        result = build_fidelity_instruction(f)
        self.assertIn("teardrop", result)
        self.assertIn("elongated", result)

    def test_includes_attachment(self):
        """Instruction includes attachment type."""
        f = ProductFidelity(
            attachment=FidelityAttachment(type="lever-back", details="visible")
        )
        result = build_fidelity_instruction(f)
        self.assertIn("lever-back", result)

    def test_includes_decorative(self):
        """Instruction includes decorative elements."""
        f = ProductFidelity(
            decorative=FidelityDecorative(
                elements=["cut-outs", "filigree"],
                surface_texture="hammered",
                symmetry="asymmetric",
            )
        )
        result = build_fidelity_instruction(f)
        self.assertIn("cut-outs", result)
        self.assertIn("hammered", result)
        self.assertIn("asymmetric", result)

    def test_includes_unknown_details(self):
        """Instruction includes unknown details as do-not-invent warnings."""
        f = ProductFidelity(unknown_details=["back clasp unclear"])
        result = build_fidelity_instruction(f)
        self.assertIn("back clasp unclear", result)
        self.assertIn("do NOT invent", result)

    def test_includes_avoid_errors(self):
        """Instruction includes avoid-errors list."""
        f = ProductFidelity(avoid_errors=["do not add stones to dome"])
        result = build_fidelity_instruction(f)
        self.assertIn("do not add stones to dome", result)

    def test_includes_reference_priority(self):
        """Every instruction includes the reference priority instruction."""
        f = ProductFidelity(product_type="Ring")
        result = build_fidelity_instruction(f)
        self.assertIn("REFERENCE IMAGE PRIORITY", result)
        self.assertIn("authoritative", result.lower())

    def test_full_model_instruction(self):
        """A fully populated model generates a comprehensive instruction."""
        f = ProductFidelity(
            product_type="Earring",
            quantity="pair",
            design_summary="Gold jhumka with red stones",
            total_stone_count=12,
            stones=[
                FidelityStone(count=6, shape="round", colour="red", placement="dome"),
                FidelityStone(count=6, shape="pear", colour="white", placement="drop"),
            ],
            metal=FidelityMetal(colour="yellow gold", appearance="polished"),
            proportions=FidelityProportions(overall_geometry="bell-shaped"),
            attachment=FidelityAttachment(type="hook"),
            decorative=FidelityDecorative(
                elements=["granulation"], surface_texture="textured"
            ),
            unknown_details=["earring back type unclear"],
            avoid_errors=["do not add stones to dome"],
        )
        result = build_fidelity_instruction(f)
        # All key elements should be present
        self.assertIn("Earring", result)
        self.assertIn("pair", result)
        self.assertIn("12", result)
        self.assertIn("yellow gold", result)
        self.assertIn("bell-shaped", result)
        self.assertIn("hook", result)
        self.assertIn("granulation", result)
        self.assertIn("earring back type unclear", result)
        self.assertIn("do not add stones to dome", result)
        self.assertIn("REFERENCE IMAGE PRIORITY", result)


# ─── Test: Fidelity QA Evaluation ───────────────────────────────────────


class TestFidelityQA(unittest.TestCase):
    """Verify the fidelity QA evaluation."""

    def test_no_fidelity_returns_manual_qa(self):
        """When fidelity is None, returns manual QA note."""
        result = evaluate_fidelity(None)
        self.assertIsNotNone(result.notes)
        self.assertIn("manual QA", result.notes)

    def test_no_comparison_returns_manual_qa(self):
        """When generated_attributes is None, returns manual QA note."""
        f = ProductFidelity(total_stone_count=7)
        result = evaluate_fidelity(f)
        self.assertIsNotNone(result.notes)
        self.assertIn("manual QA", result.notes)

    def test_stone_count_match(self):
        """Correct stone count is detected."""
        f = ProductFidelity(total_stone_count=7)
        result = evaluate_fidelity(f, {"total_stone_count": 7})
        self.assertTrue(result.stone_count_match)

    def test_stone_count_mismatch(self):
        """Incorrect stone count is detected."""
        f = ProductFidelity(total_stone_count=7)
        result = evaluate_fidelity(f, {"total_stone_count": 5})
        self.assertFalse(result.stone_count_match)

    def test_metal_colour_match(self):
        """Correct metal colour is detected (case-insensitive substring)."""
        f = ProductFidelity(metal=FidelityMetal(colour="rose gold"))
        result = evaluate_fidelity(f, {"metal_colour": "18K Rose Gold Plated"})
        self.assertTrue(result.metal_colour_match)

    def test_metal_colour_mismatch(self):
        """Incorrect metal colour is detected."""
        f = ProductFidelity(metal=FidelityMetal(colour="rose gold"))
        result = evaluate_fidelity(f, {"metal_colour": "Yellow Gold"})
        self.assertFalse(result.metal_colour_match)

    def test_quantity_match(self):
        """Correct quantity (pair) is detected."""
        f = ProductFidelity(quantity="pair")
        result = evaluate_fidelity(f, {"quantity": "pair of earrings"})
        self.assertTrue(result.single_or_pair_match)

    def test_overall_score_calculation(self):
        """Overall score is calculated from individual checks."""
        f = ProductFidelity(
            total_stone_count=7,
            metal=FidelityMetal(colour="gold"),
            quantity="pair",
        )
        result = evaluate_fidelity(
            f,
            {
                "total_stone_count": 7,  # match
                "metal_colour": "Gold",  # match
                "quantity": "single",  # mismatch
            },
        )
        self.assertIsNotNone(result.overall_score)
        self.assertAlmostEqual(result.overall_score, 2 / 3, places=2)


# ─── Test: Constants Exist and Are Strings ──────────────────────────────


class TestConstants(unittest.TestCase):
    """Verify all canonical constants exist and are non-empty strings."""

    def test_generic_fidelity_instruction(self):
        self.assertIsInstance(GENERIC_FIDELITY_INSTRUCTION, str)
        self.assertGreater(len(GENERIC_FIDELITY_INSTRUCTION), 100)

    def test_reference_priority_instruction(self):
        self.assertIsInstance(REFERENCE_PRIORITY_INSTRUCTION, str)
        self.assertGreater(len(REFERENCE_PRIORITY_INSTRUCTION), 100)

    def test_product_preservation_constraints(self):
        self.assertIsInstance(PRODUCT_PRESERVATION_CONSTRAINTS, str)
        self.assertGreater(len(PRODUCT_PRESERVATION_CONSTRAINTS), 100)

    def test_reference_image_anchor(self):
        self.assertIsInstance(REFERENCE_IMAGE_ANCHOR, str)
        self.assertGreater(len(REFERENCE_IMAGE_ANCHOR), 50)

    def test_reference_priority_block(self):
        self.assertIsInstance(REFERENCE_PRIORITY_BLOCK, str)
        self.assertGreater(len(REFERENCE_PRIORITY_BLOCK), 50)

    def test_scale_control_block(self):
        self.assertIsInstance(SCALE_CONTROL_BLOCK, str)
        self.assertGreater(len(SCALE_CONTROL_BLOCK), 50)

    def test_product_preservation_block(self):
        self.assertIsInstance(PRODUCT_PRESERVATION_BLOCK, str)
        self.assertGreater(len(PRODUCT_PRESERVATION_BLOCK), 50)

    def test_reference_image_instruction(self):
        self.assertIsInstance(REFERENCE_IMAGE_INSTRUCTION, str)
        self.assertGreater(len(REFERENCE_IMAGE_INSTRUCTION), 50)


# ─── Test: Priority Order ───────────────────────────────────────────────


class TestPriorityOrder(unittest.TestCase):
    """Verify the fidelity instruction respects the priority hierarchy."""

    def test_fidelity_comes_before_presentation(self):
        """Fidelity rules appear before any presentation/lighting instructions."""
        f = ProductFidelity(
            product_type="Earring",
            total_stone_count=7,
            metal=FidelityMetal(colour="gold"),
        )
        result = build_fidelity_instruction(f)

        fidelity_pos = result.find("PRODUCT FIDELITY")
        reference_pos = result.find("REFERENCE IMAGE PRIORITY")

        self.assertGreater(fidelity_pos, -1)
        self.assertGreater(reference_pos, -1)
        self.assertLess(fidelity_pos, reference_pos)


# ─── Test: Backward Compatibility ───────────────────────────────────────


class TestBackwardCompatibility(unittest.TestCase):
    """Verify that constants imported from product_fidelity are usable
    by existing code that imports them from their original locations."""

    def test_import_from_product_fidelity(self):
        """All constants can be imported directly from product_fidelity."""
        from app.ai.product_fidelity import (
            PRODUCT_PRESERVATION_CONSTRAINTS as PPC,
            REFERENCE_PRIORITY_BLOCK as RPB,
        )
        self.assertIsInstance(PPC, str)
        self.assertIsInstance(RPB, str)

    def test_import_from_image_generation_manager(self):
        """REFERENCE_PRIORITY_BLOCK can still be imported from image_generation_manager."""
        from app.ai.image_generation_manager import REFERENCE_PRIORITY_BLOCK as RPB
        self.assertIsInstance(RPB, str)
        self.assertGreater(len(RPB), 50)

    def test_import_from_prompt_fusion_engine(self):
        """PRODUCT_PRESERVATION_BLOCK can still be imported from prompt_fusion_engine."""
        from app.services.prompt_fusion_engine import (
            PRODUCT_PRESERVATION_BLOCK as PPB,
        )
        self.assertIsInstance(PPB, str)
        self.assertGreater(len(PPB), 50)

    def test_import_from_gemini_provider(self):
        """REFERENCE_IMAGE_ANCHOR can still be imported from gemini_image_provider."""
        from app.ai.providers.gemini_image_provider import (
            REFERENCE_IMAGE_ANCHOR as RIA,
        )
        self.assertIsInstance(RIA, str)
        self.assertGreater(len(RIA), 50)


if __name__ == "__main__":
    unittest.main()
