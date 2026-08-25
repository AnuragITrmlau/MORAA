"""API routes for the Prompt Fusion Intelligence Engine (PFIE).

GemVision V3 — additive endpoint. Does NOT modify any existing route.

    POST /api/fuse-prompt  →  fuse product intelligence + creative
                             direction + preservation rules + enhancement
                             into a single final image-generation prompt.

    GET  /api/fuse-prompt/health  →  fusion engine status.
"""

from typing import Optional

from fastapi import APIRouter, status

from app.schemas.prompt_fusion import (
    PromptFusionRequest,
    PromptFusionResponse,
)
from app.services.prompt_fusion_engine import PromptFusionEngine, fusion_health
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Prompt Fusion"])


@router.post(
    "/fuse-prompt",
    response_model=PromptFusionResponse,
    status_code=status.HTTP_200_OK,
    summary="Fuse a final image-generation prompt (GemVision V3 PFIE)",
    description=(
        "Fuses four layers into one final prompt: Layer 1 — Gemini product "
        "facts; Layer 2 — ChatGPT Luxury Jewellery Creative Direction "
        "(template fallback when unconfigured/unavailable); Layer 3 — "
        "product preservation rules; Layer 4 — photography enhancement "
        "instructions. Lifestyle/wearing mode appends wearing-specific "
        "instructions. Always pair the returned prompt with the uploaded "
        "image as the reference image when generating."
    ),
)
async def fuse_prompt(request: PromptFusionRequest):
    """Run the prompt fusion engine for a single category + mode."""
    request_id = request.imageId or "unknown"
    logger.bind(category="prompt-fusion").info(
        f"Fusion requested: category={request.category} "
        f"mode={request.mode} image={request_id}"
    )

    engine = PromptFusionEngine()
    result = await engine.fuse(
        product_intelligence=request.productIntelligence,
        category=request.category,
        mode=request.mode,
        aspect_ratio=request.aspectRatio,
        request_id=request_id,
    )

    if not result.get("success"):
        logger.bind(category="prompt-fusion").error(
            f"Fusion failed: {result.get('error')} image={request_id}"
        )
        return PromptFusionResponse(
            success=False,
            prompt=None,
            layers=None,
            source=None,
            tokens_consumed=0,
            generation_time_ms=result.get("generation_time_ms", 0),
            error=result.get("error", "Prompt fusion failed"),
        )

    return PromptFusionResponse(
        success=True,
        prompt=result.get("prompt"),
        layers=result.get("layers"),
        source=result.get("source"),
        tokens_consumed=result.get("tokens_consumed", 0),
        generation_time_ms=result.get("generation_time_ms", 0),
        error=None,
    )


@router.get(
    "/fuse-prompt/health",
    summary="Prompt fusion engine health check",
    description="Check if the prompt fusion engine is ready.",
)
async def fuse_prompt_health():
    """Health check for the prompt fusion engine."""
    import datetime

    health = fusion_health()
    health["timestamp"] = datetime.datetime.now().isoformat()
    return health
