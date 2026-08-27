"""API routes for Complementary Shot — Prompt 5.

Provides a single endpoint that builds the complete complementary shot
prompt.  The frontend calls this endpoint, receives the prompt, and sends
it to /api/generate-image with the reference image.

Flow:
    POST /api/earring-complementary-shot/prompt  →  complete prompt string
        ↓
    Frontend sends prompt + reference_image to /api/generate-image
        ↓
    ImageGenerationManager auto-appends REFERENCE_PRIORITY_BLOCK
        + marketplace rules → provider → generated image
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.earring_complementary_shot_prompt import (
    build_complementary_shot_prompt,
)
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Earring Complementary Shot"])


class ComplementaryShotPromptRequest(BaseModel):
    """Request body for complementary shot prompt generation."""

    earring_type: Optional[str] = Field(
        None,
        description=(
            'Earring type: "Hoop", "Stud", or "Dangle". '
            "When provided, type-specific preservation rules are included. "
            "When None, generic earring preservation rules are used."
        ),
    )


class ComplementaryShotPromptResponse(BaseModel):
    """Response body for complementary shot prompt generation."""

    success: bool
    prompt: Optional[str] = None
    earring_type: Optional[str] = None
    error: Optional[str] = None


@router.post(
    "/earring-complementary-shot/prompt",
    response_model=ComplementaryShotPromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate complementary shot prompt (Prompt 5)",
    description=(
        "Returns the single authoritative complementary shot prompt "
        "for Fashion Jewellery → Earrings. The frontend sends this prompt "
        "along with the reference image to /api/generate-image."
    ),
)
async def generate_complementary_shot_prompt(
    request: ComplementaryShotPromptRequest,
):
    """Generate the complementary shot prompt.

    This endpoint returns a complete prompt string that includes:
    - Reference image priority marker (prevents backend double-appendition)
    - Product fidelity — absolute priority
    - Anti-redesign rules
    - Anti-symmetry / anti-beautification rules (Phase 4D fix)
    - Product identity preservation
    - Earring type-specific preservation (Hoop/Stud/Dangle)
    - Material & colour fidelity (Task 3 validated)
    - Staging requirements (editorial surface)
    - Asymmetric jewellery arrangement
    - Physical contact & grounding
    - Camera, lighting, background
    - Visual hierarchy (90/10 jewellery focus)
    - Negative space & bead cluster preservation
    - Strictly forbidden elements
    - Quality control checklist

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

        prompt = build_complementary_shot_prompt(
            earring_type=earring_type,
        )

        logger.info(
            f"Complementary shot prompt generated: "
            f"earring_type={earring_type or 'generic'} "
            f"prompt_len={len(prompt)}"
        )

        return ComplementaryShotPromptResponse(
            success=True,
            prompt=prompt,
            earring_type=earring_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complementary shot prompt generation failed: {e}")
        return ComplementaryShotPromptResponse(
            success=False,
            error=f"Prompt generation failed: {str(e)}",
        )


@router.get(
    "/earring-complementary-shot/prompt/health",
    summary="Complementary shot prompt health check",
    description="Check if the complementary shot prompt endpoint is ready.",
)
async def complementary_shot_health():
    """Health check for the complementary shot prompt service."""
    import datetime

    return {
        "status": "ready",
        "service": "earring-complementary-shot-prompt",
        "earring_types": ["Hoop", "Stud", "Dangle"],
        "prompt_number": 5,
        "timestamp": datetime.datetime.now().isoformat(),
    }
