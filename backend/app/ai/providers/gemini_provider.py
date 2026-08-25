"""Gemini AI provider — connects to Google Gemini API from the backend.

This provider calls the Gemini API directly using google-generativeai SDK,
independently of the frontend Next.js API route.  It is managed by the
``AIProviderManager`` and supports failover.

Requires ``GEMINI_API_KEY`` environment variable in the backend .env.
"""

import json
import time
from typing import Any, Dict, List, Optional

from app.ai.providers.base import BaseAIProvider, ProviderResult
from app.config import settings
from app.utils.logger import logger


class GeminiProvider(BaseAIProvider):
    """AI provider that uses Google's Gemini API for image analysis."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def provider_version(self) -> str:
        return "1.0.0"

    @property
    def is_available(self) -> bool:
        return bool(settings.GEMINI_API_KEY)

    async def validate_image(self, image_path: str) -> bool:
        """Validate image using Gemini's own content filtering.

        Returns True by default since Gemini handles invalid images
        gracefully during analysis.
        """
        try:
            from PIL import Image as PILImage
            img = PILImage.open(image_path)
            img.verify()
            return True
        except Exception:
            return False

    async def analyze(
        self,
        image_paths: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderResult:
        """Analyse one or more images using Gemini.

        For multi-image analysis, all images are sent together in one
        API call so Gemini can cross-reference them.

        Args:
            image_paths: Path(s) to uploaded image files.
            context: Optional dict with ``request_id``, ``custom_prompt``, etc.

        Returns:
            ProviderResult with structured analysis data.
        """
        request_id = (context or {}).get("request_id", "unknown")
        custom_prompt = (context or {}).get("custom_prompt", "")
        start_time = time.time()

        logger.info(
            f"GeminiProvider analyzing {len(image_paths)} image(s) "
            f"request_id={request_id}"
        )

        # Lazy import — google-generativeai is only required for this provider
        try:
            import google.generativeai as genai
        except ImportError:
            return ProviderResult(
                success=False,
                error="google-generativeai package not installed. Run: pip install google-generativeai",
                provider_name=self.provider_name,
                processing_time=time.time() - start_time,
            )

        # Configure the Gemini client
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Build the analysis prompt
        analysis_prompt = custom_prompt or (
            "You are MORAA GemVision, a precise jewellery and product analysis AI. "
            "Analyse the provided image(s) and return a structured JSON response. "
            "Do NOT include markdown formatting or code fences — return raw JSON only.\n\n"
            "Fields:\n"
            "- material: string (detected material, e.g. 'Yellow Gold', 'Silver', 'Bronze')\n"
            "- gold_purity: string (e.g. '18K', '14K', '925', or 'Unknown')\n"
            "- weight: float (estimated weight in grams)\n"
            "- category: string (e.g. 'Ring', 'Necklace', 'Earrings', 'Electronics')\n"
            "- estimated_price: float (estimated market price in USD)\n"
            "- confidence: float (0.0 to 1.0)\n"
            "- gemstones: array of strings\n"
            "- style: string\n"
            "- era: string\n"
            "- condition: string\n"
            "- summary: string (natural language description)\n"
            # Jewellery Scale & Reference Accuracy (JSR) — additive fields.
            # Note: these flow to callers of /api/analyze/sync via raw JSON.
            # They are NOT persisted to the Analysis DB model (fixed columns),
            # so the backend prompt_generation_service path won't carry them;
            # the primary UI generation path (frontend image-analysis.service.ts
            # -> buildProductIntelligence) carries them end-to-end.
            "Jewellery scale & reference accuracy fields (for jewellery images):\n"
            "- size_category: string ('small' | 'medium' | 'large' — jewellery size relative to human anatomy)\n"
            "- relative_scale: string (description of jewellery size compared to human anatomy, e.g. small stud, delicate chain)\n"
            "- wear_position: string (natural wearing location: earlobe, finger, neckline, collarbone, wrist)\n"
            "- proportion_notes: string (realistic fitting information)\n"
            "- avoid_generation_errors: array of strings (e.g. 'oversized jewellery', 'tiny jewellery', 'unrealistic placement', 'exaggerated gemstones')"
        )

        # Build contents with all images
        import PIL.Image as PILImageModule

        contents_parts = [analysis_prompt]
        for img_path in image_paths:
            try:
                pil_img = PILImageModule.open(img_path)
                contents_parts.append(pil_img)
            except Exception as e:
                logger.error(f"GeminiProvider: failed to load image {img_path}: {e}")
                return ProviderResult(
                    success=False,
                    error=f"Failed to load image: {e}",
                    provider_name=self.provider_name,
                    processing_time=time.time() - start_time,
                )

        if len(image_paths) > 1:
            contents_parts.append(
                "The above images are different views/angles of the same item. "
                "Analyse them collectively and provide a single unified analysis."
            )

        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL or "gemini-1.5-flash",
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 8192,
            },
        )

        try:
            response = await model.generate_content_async(contents_parts)
            raw_text = response.text

            # Parse JSON from response
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            result_data = json.loads(cleaned)

            processing_time = time.time() - start_time
            logger.info(
                f"GeminiProvider completed: {result_data.get('category', 'unknown')} "
                f"request_id={request_id} time={processing_time:.2f}s"
            )

            return ProviderResult(
                success=True,
                data=result_data,
                provider_name=self.provider_name,
                processing_time=processing_time,
                tool_executions=[
                    {
                        "name": "gemini_analysis",
                        "order": 0,
                        "status": "completed",
                        "duration": round(processing_time, 3),
                        "output": f"Analysed {len(image_paths)} image(s) via Gemini API",
                    }
                ],
            )

        except Exception as e:
            error_msg = str(e)
            processing_time = time.time() - start_time
            logger.error(
                f"GeminiProvider failed: {error_msg} "
                f"request_id={request_id} time={processing_time:.2f}s"
            )
            return ProviderResult(
                success=False,
                error=error_msg,
                provider_name=self.provider_name,
                processing_time=processing_time,
            )
