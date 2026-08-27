"""API routes for Earring Scale Reference Shot — Prompt 3.

Provides a single endpoint that builds the complete earring scale-reference
prompt.  The frontend calls this endpoint, receives the prompt, and sends it
to /api/generate-image with the reference image.

Flow:
    POST /api/earring-scale-reference/prompt  →  complete prompt string
        ↓
    Frontend sends prompt + reference_image to /api/generate-image
        ↓
    ImageGenerationManager auto-appends REFERENCE_PRIORITY_BLOCK
        + marketplace rules → provider → generated image
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.earring_scale_reference_prompt import (
    build_scale_reference_prompt,
)
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Earring Scale Reference"])


class ScaleReferencePromptRequest(BaseModel):
    """Request body for earring scale-reference prompt generation."""

    earring_type: Optional[str] = Field(
        None,
        description=(
            'Earring type: "Hoop", "Stud", or "Dangle". '
            "When provided, type-specific preservation rules are included. "
            "When None, generic earring preservation rules are used."
        ),
    )


class ScaleReferencePromptResponse(BaseModel):
    """Response body for earring scale-reference prompt generation."""

    success: bool
    prompt: Optional[str] = None
    earring_type: Optional[str] = None
    error: Optional[str] = None


@router.post(
    "/earring-scale-reference/prompt",
    response_model=ScaleReferencePromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate earring scale-reference prompt (Prompt 3)",
    description=(
        "Returns the single authoritative earring scale-reference prompt "
        "for Fashion Jewellery → Earrings. The frontend sends this prompt "
        "along with the reference image to /api/generate-image."
    ),
)
async def generate_scale_reference_prompt(
    request: ScaleReferencePromptRequest,
):
    """Generate the earring scale-reference prompt.

    This endpoint returns a complete prompt string that includes:
    - Reference image priority marker (prevents backend double-appendition)
    - Anti-redesign rules
    - Anti-symmetry / anti-beautification rules (Phase 4D fix)
    - Product identity preservation
    - Earring type-specific preservation (Hoop/Stud/Dangle)
    - Material & colour fidelity (Task 3 validated)
    - Negative space and bead cluster preservation
    - Scale control (ear adapts to product, not vice versa)
    - Ear-as-scale-reference instructions
    - Occlusion & anti-reconstruction rules
    - Dimension integrity rules
    - Camera, lighting, and e-commerce presentation rules

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

        prompt = build_scale_reference_prompt(
            earring_type=earring_type,
        )

        logger.info(
            f"Scale reference prompt generated: "
            f"earring_type={earring_type or 'generic'} "
            f"prompt_len={len(prompt)}"
        )

        return ScaleReferencePromptResponse(
            success=True,
            prompt=prompt,
            earring_type=earring_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scale reference prompt generation failed: {e}")
        return ScaleReferencePromptResponse(
            success=False,
            error=f"Prompt generation failed: {str(e)}",
        )


@router.get(
    "/earring-scale-reference/prompt/health",
    summary="Earring scale-reference prompt health check",
    description="Check if the earring scale-reference prompt endpoint is ready.",
)
async def scale_reference_health():
    """Health check for the earring scale-reference prompt service."""
    import datetime

    return {
        "status": "ready",
        "service": "earring-scale-reference-prompt",
        "earring_types": ["Hoop", "Stud", "Dangle"],
        "prompt_number": 3,
        "timestamp": datetime.datetime.now().isoformat(),
    }
