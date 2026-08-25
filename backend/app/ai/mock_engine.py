"""Mock AI engine for development and testing.

Returns realistic structured analysis data without calling any AI model.
This makes it easy to develop and test the frontend integration
while the real AI models are being trained.
"""

import asyncio
import random
from typing import Any, Dict, Optional

from app.ai.base import AIEngine
from app.utils.logger import logger


class MockAIEngine(AIEngine):
    """Mock AI engine for development and testing."""

    @property
    def engine_name(self) -> str:
        return "mock-gemvision-engine"

    @property
    def engine_version(self) -> str:
        return "1.0.0"

    async def validate_image(self, image_path: str) -> bool:
        """Simulate image validation."""
        await asyncio.sleep(0.5)
        # In mock mode, all images are valid
        return True

    async def analyze(
        self, image_path: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulate AI analysis with realistic mock data.

        The engine ALWAYS reads the image from the explicit ``image_path``
        argument — never from a global variable, shared filename, or latest
        uploaded reference.  This guarantees request isolation under
        concurrent uploads.
        """
        request_id = (context or {}).get("request_id", "unknown")
        logger.info(f"MockAIEngine analyzing: request_id={request_id} path={image_path}")

        # Simulate processing delay (2-4 seconds)
        delay = 2.0 + random.random() * 2.0
        await asyncio.sleep(delay)

        # Pick random analysis variant for variety
        variants = [
            {
                "material": "Yellow Gold",
                "gold_purity": "18K (75% purity)",
                "weight": round(12.45 + random.uniform(-2, 2), 2),
                "category": "Necklace",
                "estimated_price": round(2800 + random.uniform(-300, 500), 2),
                "confidence": round(0.85 + random.uniform(-0.1, 0.1), 2),
                "gemstones": ["Small diamond accents", "Blue sapphire details"],
                "style": "Victorian Revival",
                "era": "Contemporary",
                "condition": "Well-maintained with minimal visible wear",
                "summary": (
                    "The uploaded image appears to contain a floral style gold necklace with decorative stones. "
                    "The design features intricate metalwork with symmetrical patterns, suggesting skilled craftsmanship. "
                    "Small sparkling stones are visible along the pendant, and the warm yellow tone of the metal is characteristic of gold. "
                    "The piece has a classic, elegant look that would suit formal occasions."
                ),
            },
            {
                "material": "White Gold",
                "gold_purity": "14K (58.5% purity)",
                "weight": round(8.2 + random.uniform(-1, 1), 2),
                "category": "Ring",
                "estimated_price": round(4500 + random.uniform(-500, 800), 2),
                "confidence": round(0.92 + random.uniform(-0.05, 0.05), 2),
                "gemstones": ["Single diamond center stone"],
                "style": "Classic Solitaire",
                "era": "Contemporary",
                "condition": "Excellent condition, well-polished surface",
                "summary": (
                    "This image appears to show a white metal ring with a single clear stone at the center. "
                    "The metal has a bright silver-white appearance typical of white gold or platinum. "
                    "The center stone is prominent and faceted, with visible sparkle. "
                    "The band is smooth and simple, putting the focus on the main stone."
                ),
            },
            {
                "material": "Rose Gold",
                "gold_purity": "18K (75% purity)",
                "weight": round(5.78 + random.uniform(-0.5, 0.5), 2),
                "category": "Earrings",
                "estimated_price": round(980 + random.uniform(-100, 200), 2),
                "confidence": round(0.78 + random.uniform(-0.1, 0.1), 2),
                "gemstones": ["No visible stones"],
                "style": "Modern Minimalist",
                "era": "Contemporary",
                "condition": "Good condition with some surface scratches",
                "summary": (
                    "The image shows a pair of earrings with a warm pinkish metal tone, consistent with rose gold. "
                    "The design is simple and modern, with smooth curved shapes. "
                    "No decorative stones are visible in the pieces. "
                    "The earrings appear lightweight and suitable for everyday wear."
                ),
            },
        ]

        return random.choice(variants)
