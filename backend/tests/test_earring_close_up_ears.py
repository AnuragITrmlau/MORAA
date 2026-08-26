"""Regression tests for the isolated Prompt 2 Close Up Ears workflow."""

import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.api.routes.earring_close_up_ears import (
    CloseUpEarsPromptRequest,
    generate_close_up_ears_prompt,
)
from app.services.earring_close_up_ears_prompt import (
    REFERENCE_PRIORITY_MARKER,
    build_close_up_ears_prompt,
)


class TestCloseUpEarsPrompt(unittest.TestCase):
    """Verify Prompt 2 is fidelity-first and permits the intended ear context."""

    def setUp(self) -> None:
        self.prompt = build_close_up_ears_prompt()
        self.prompt_lower = self.prompt.lower()

    def test_reference_priority_is_present(self) -> None:
        self.assertIn(REFERENCE_PRIORITY_MARKER, self.prompt)
        self.assertIn("sole authoritative source", self.prompt_lower)

    def test_product_fidelity_precedes_presentation(self) -> None:
        fidelity_position = self.prompt.find("PRODUCT FIDELITY")
        wearing_position = self.prompt.find("ON-EAR COMPOSITION")
        self.assertGreaterEqual(fidelity_position, 0)
        self.assertGreater(wearing_position, fidelity_position)

    def test_prompt_requires_natural_unobstructed_ear_wearing(self) -> None:
        self.assertIn("woman's ear", self.prompt_lower)
        self.assertIn("earlobe", self.prompt_lower)
        self.assertIn("macro close-up", self.prompt_lower)
        # Verify ear is required (negative constraints enforce it)
        self.assertIn("visible human ear", self.prompt_lower)

    def test_prompt_does_not_inherit_prompt_one_only_object_rule(self) -> None:
        self.assertNotIn("earring is the only object", self.prompt_lower)
        self.assertNotIn("no human", self.prompt_lower)
        self.assertNotIn("without any human", self.prompt_lower)

    def test_prompt_rejects_product_redesign(self) -> None:
        self.assertIn("do not add, remove, substitute", self.prompt_lower)
        self.assertIn("do not fabricate", self.prompt_lower)
        self.assertIn("additional jewellery", self.prompt_lower)


class TestCloseUpEarsRoute(unittest.TestCase):
    """Verify the dedicated Prompt 2 route contract remains isolated."""

    def test_request_has_fixed_dangle_type(self) -> None:
        request = CloseUpEarsPromptRequest()
        self.assertEqual(request.earring_type, "Dangle")

    def test_route_returns_prompt_two_contract(self) -> None:
        response = asyncio.run(
            generate_close_up_ears_prompt(CloseUpEarsPromptRequest())
        )
        self.assertTrue(response.success)
        self.assertEqual(response.earring_type, "Dangle")
        self.assertIsNotNone(response.prompt)
        self.assertIn("Close Up Ears", response.prompt or "")


if __name__ == "__main__":
    unittest.main()
