"""LocalVision provider — wraps the existing VisionAIEngine as a provider.

This allows the AIProviderManager to use the PIL-based vision engine
as a fallback when cloud providers are unavailable.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from app.ai.base import AnalysisPipeline
from app.ai.engine_factory import create_engine
from app.ai.providers.base import BaseAIProvider, ProviderResult
from app.utils.logger import logger


class LocalVisionProvider(BaseAIProvider):
    """Wraps the existing PIL-based VisionAIEngine as a provider.

    Uses the same engine factory as the current analysis pipeline,
    so the engine type is controlled by ``AI_ENGINE_TYPE`` in config.
    """

    def __init__(self):
        self._pipeline: Optional[AnalysisPipeline] = None

    @property
    def provider_name(self) -> str:
        return "local_vision"

    @property
    def provider_version(self) -> str:
        return "1.0.0"

    @property
    def is_available(self) -> bool:
        return True  # Always available — no API key needed

    @property
    def capabilities(self) -> List[str]:
        return ["image_analysis", "no_api_key_needed"]

    async def validate_image(self, image_path: str) -> bool:
        """Delegate to the engine's validate_image method."""
        engine = create_engine()
        return await engine.validate_image(image_path)

    async def analyze(
        self,
        image_paths: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderResult:
        """Analyse images using the local PIL-based vision engine.

        For multi-image analysis, each image is analysed independently
        and results are merged.
        """
        request_id = (context or {}).get("request_id", "unknown")
        start_time = time.time()

        logger.info(
            f"LocalVisionProvider analyzing {len(image_paths)} image(s) "
            f"request_id={request_id}"
        )

        engine = create_engine()
        pipeline = AnalysisPipeline(engine)
        all_results: List[Dict[str, Any]] = []
        all_tool_executions: List[Dict[str, Any]] = []

        for idx, img_path in enumerate(image_paths):
            try:
                # Run the pipeline in a thread pool to avoid blocking
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda p=pipeline, ip=img_path, rid=request_id, i=idx: asyncio.run(
                        p.run(ip, context={"request_id": f"{rid}_{i}"})
                    ),
                )
                all_results.append(result)
                tool_execs = result.get("_tool_executions", [])
                for te in tool_execs:
                    te["order"] = len(all_tool_executions) + te.get("order", 0)
                    te["name"] = f"[img_{idx}] {te.get('name', 'unknown')}"
                all_tool_executions.extend(tool_execs)
            except Exception as e:
                logger.error(f"LocalVisionProvider: image {img_path} failed: {e}")
                all_results.append({
                    "category": "Unknown",
                    "material": "Unknown",
                    "error": str(e),
                })

        # Merge results for multi-image
        if len(all_results) == 1:
            merged = all_results[0]
        else:
            merged = self._merge_results(all_results, request_id)

        merged["_tool_executions"] = all_tool_executions
        processing_time = time.time() - start_time

        logger.info(
            f"LocalVisionProvider completed: {merged.get('category', 'unknown')} "
            f"images={len(image_paths)} request_id={request_id} time={processing_time:.2f}s"
        )

        return ProviderResult(
            success=True,
            data=merged,
            provider_name=self.provider_name,
            processing_time=processing_time,
            tool_executions=all_tool_executions,
        )

    def _merge_results(
        self, results: List[Dict[str, Any]], request_id: str
    ) -> Dict[str, Any]:
        """Merge analysis results from multiple images into one unified result."""
        categories = [r.get("category", "Unknown") for r in results]
        materials = [r.get("material", "Unknown") for r in results]
        confidences = [r.get("confidence", 0.0) for r in results if r.get("confidence")]
        prices = [r.get("estimated_price", 0.0) for r in results if r.get("estimated_price")]
        weights = [r.get("weight", 0.0) for r in results if r.get("weight")]

        # Find the most common category/material (mode)
        from collections import Counter
        top_category = Counter(categories).most_common(1)[0][0] if categories else "Unknown"
        top_material = Counter(materials).most_common(1)[0][0] if materials else "Unknown"

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        avg_price = sum(prices) / len(prices) if prices else 0.0
        avg_weight = sum(weights) / len(weights) if weights else 0.0

        all_gems = []
        for r in results:
            gems = r.get("gemstones", [])
            if isinstance(gems, list):
                all_gems.extend(gems)

        # Take the best condition description
        conditions = [r.get("condition", "") for r in results if r.get("condition")]
        best_condition = conditions[0] if conditions else "Unknown"

        # Build a comprehensive summary
        summary_parts = [
            f"Multi-image analysis of {len(results)} image(s). ",
            f"Detected category: {top_category}. ",
            f"Detected material: {top_material}. ",
        ]
        if all_gems:
            summary_parts.append(f"Gemstones detected: {', '.join(set(all_gems))}. ")
        summary_parts.append(f"Average confidence: {avg_confidence:.0%}.")

        return {
            "material": top_material,
            "gold_purity": results[0].get("gold_purity", "Unknown") if results else "Unknown",
            "weight": round(avg_weight, 2),
            "category": top_category,
            "estimated_price": round(avg_price, 2),
            "confidence": round(avg_confidence, 2),
            "gemstones": list(set(all_gems)),
            "style": results[0].get("style", "Contemporary") if results else "Contemporary",
            "era": results[0].get("era", "Contemporary") if results else "Contemporary",
            "condition": best_condition,
            "summary": " ".join(summary_parts),
        }
