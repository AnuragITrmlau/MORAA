"""Abstract base class for AI analysis engines.

This defines the interface that all AI engines must implement.
New AI models (gemstone classifier, diamond analyzer, LLM, etc.)
can be plugged in by creating a new class that extends AIEngine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AIEngine(ABC):
    """Abstract base for AI analysis engines."""

    @abstractmethod
    async def analyze(self, image_path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a jewellery image and return structured results.

        The engine MUST read the image from ``image_path`` only — never from
        a global variable, shared filename, or ``latest uploaded file``.
        This guarantees request isolation even under concurrent execution.

        Args:
            image_path: Absolute path to the uploaded image file.
            context: Optional contextual data (e.g., ``request_id``,
                     user preferences, image metadata).

        Returns:
            Dict containing analysis results. Must include at minimum:
                - material: str
                - gold_purity: str
                - weight: float
                - category: str
                - estimated_price: float
                - confidence: float
                - gemstones: List[str]
                - style: str
                - era: str
                - condition: str
                - summary: str
        """
        ...

    @abstractmethod
    async def validate_image(self, image_path: str) -> bool:
        """
        Validate that the image is suitable for analysis.

        Args:
            image_path: Path to the image file.

        Returns:
            True if image is valid, False otherwise.
        """
        ...

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Return the name/identifier of this AI engine."""
        ...

    @property
    @abstractmethod
    def engine_version(self) -> str:
        """Return the version of this AI engine."""
        ...


class AnalysisPipeline:
    """
    Orchestrates the analysis pipeline: preprocess -> AI engine -> postprocess.

    This pipeline interface ensures that future AI models can be plugged in
    without changing the API contracts.
    """

    def __init__(self, engine: AIEngine):
        self.engine = engine

    async def run(
        self, image_path: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the full analysis pipeline.

        The pipeline always operates on the explicit ``image_path`` — it NEVER
        reads from a global or shared image reference.  This ensures that even
        when multiple images are processed concurrently, each result belongs
        to its own image.
        """
        # Pre-processing can be added here (image enhancement, resizing, etc.)
        result = await self.engine.analyze(image_path, context)
        # Post-processing can be added here (data enrichment, formatting, etc.)
        return self._postprocess(result)

    def _postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process the AI result to ensure consistent output format."""
        required_fields = [
            "material", "gold_purity", "weight", "category",
            "estimated_price", "confidence", "gemstones",
            "style", "era", "condition", "summary",
        ]
        for field in required_fields:
            if field not in result:
                result[field] = "" if field in [
                    "material", "gold_purity", "category", "style", "era", "condition", "summary"
                ] else 0.0 if field in ["weight", "estimated_price", "confidence"] else []
        return result
