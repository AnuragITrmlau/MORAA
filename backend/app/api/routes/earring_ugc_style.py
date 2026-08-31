"""API routes for UGC Style — Prompt 6.

Provides a single endpoint that builds the complete UGC style prompt.
The frontend calls this endpoint, receives the prompt, and sends
it to /api/generate-image with the reference image.

Flow:
    POST /api/earring-ugc-style/prompt  →  complete prompt string
        ↓
    Frontend sends prompt + reference_image to /api/generate-image
        ↓
    ImageGenerationManager auto-appends REFERENCE_PRIORITY_BLOCK
        + marketplace rules → provider → generated image
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.earring_ugc_style_prompt import (
    build_ugc_style_prompt,
)
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Earring UGC Style"])


class UGCStylePromptRequest(BaseModel):
    """Request body for UGC style prompt generation."""

    earring_type: Optional[str] = Field(
        None,
        description=(
            'Earring type: "Hoop", "Stud", or "Dangle". '
            "When provided, type-specific preservation rules are included. "
            "When None, generic earring preservation rules are used."
        ),
    )


class UGCStylePromptResponse(BaseModel):
    """Response body for UGC style prompt generation."""

    success: bool
    prompt: Optional[str] = None
    earring_type: Optional[str] = None
    error: Optional[str] = None


@router.post(
    "/earring-ugc-style/prompt",
    response_model=UGCStylePromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate UGC style prompt (Prompt 6)",
    description=(
        "Returns the single authoritative UGC style prompt "
        "for Fashion Jewellery → Earrings. The frontend sends this prompt "
        "along with the reference image to /api/generate-image."
    ),
)
async def generate_ugc_style_prompt(
    request: UGCStylePromptRequest,
):
    """Generate the UGC style prompt.

    This endpoint returns a complete prompt string that includes:
    - Reference image priority marker (prevents backend double-appendition)
    - Product fidelity — absolute priority
    - Anti-redesign rules
    - Anti-symmetry / anti-beautification rules (Phase 4D fix)
    - Product identity preservation
    - Earring type-specific preservation (Hoop/Stud/Dangle)
    - Material & colour fidelity (Task 3 validated)
    - Negative space and bead cluster preservation
    - Size & proportion integrity
    - UGC environment (vanity, unboxing, wooden desk, linen)
    - Natural window daylight lighting
    - Smartphone photography aesthetic
    - Strictly forbidden elements

    The frontend must send this prompt + reference image to
    /api/generate-image.  The ImageGenerationManager will auto-append
    REFERENCE_PRIORITY_BLOCK and marketplace rules as needed.
    """
    try:
        earring_type = request.earring_type

        # Validate earring type if provided
        valid_types = {"Hoop", "Stud", "Dangle"}
        if earring_type and earring_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid earring_type: '{earring_type}'. "
                    f"Must be one of: {', '.join(sorted(valid_types))}"
                ),
            )

        prompt = build_ugc_style_prompt(
            earring_type=earring_type,
        )

        logger.info(
            f"UGC style prompt generated: "
            f"earring_type={earring_type or 'generic'} "
            f"prompt_len={len(prompt)}"
        )

        return UGCStylePromptResponse(
            success=True,
            prompt=prompt,
            earring_type=earring_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UGC style prompt generation failed: {e}")
        return UGCStylePromptResponse(
            success=False,
            error=f"Prompt generation failed: {str(e)}",
        )


@router.get(
    "/earring-ugc-style/prompt/health",
    summary="UGC style prompt health check",
    description="Check if the UGC style prompt endpoint is ready.",
)
async def ugc_style_health():
    """Health check for the UGC style prompt service."""
    import datetime

    return {
        "status": "ready",
        "service": "earring-ugc-style-prompt",
        "earring_types": ["Hoop", "Stud", "Dangle"],
        "prompt_number": 6,
        "timestamp": datetime.datetime.now().isoformat(),
    }
