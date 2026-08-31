"""API routes for Professional Commercial Photography — Prompt 4.

Provides a single endpoint that builds the complete professional commercial
earring photography prompt with a selectable environment archetype.
The frontend calls this endpoint, receives the prompt, and sends it to
/api/generate-image with the reference image.

Flow:
    POST /api/earring-professional-shot/prompt  →  complete prompt string
        ↓
    Frontend sends prompt + reference_image to /api/generate-image
        ↓
    ImageGenerationManager auto-appends REFERENCE_PRIORITY_BLOCK
        + marketplace rules → provider → generated image
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.earring_professional_shot_prompt import (
    build_professional_shot_prompt,
    VALID_ENVIRONMENTS,
    ENVIRONMENT_LABELS,
)
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Earring Professional Shot"])


class ProfessionalShotPromptRequest(BaseModel):
    """Request body for professional commercial earring photography prompt
    generation with dynamic environment archetype selection."""

    earring_type: Optional[str] = Field(
        None,
        description=(
            'Earring type: "Hoop", "Stud", or "Dangle". '
            "When provided, type-specific preservation rules are included. "
            "When None, generic earring preservation rules are used."
        ),
    )
    archetype: str = Field(
        "minimalist",
        description=(
            "Environment archetype for the professional commercial "
            "earring photograph. Must be one of: "
            + ", ".join(VALID_ENVIRONMENTS)
            + ". Defaults to 'minimalist'."
        ),
    )


class ProfessionalShotPromptResponse(BaseModel):
    """Response body for professional commercial earring photography prompt
    generation."""

    success: bool
    prompt: Optional[str] = None
    earring_type: Optional[str] = None
    archetype: Optional[str] = None
    error: Optional[str] = None


@router.post(
    "/earring-professional-shot/prompt",
    response_model=ProfessionalShotPromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate professional commercial earring photography prompt with dynamic environment (Prompt 4)",
    description=(
        "Returns the single authoritative professional commercial earring "
        "photography prompt for Fashion Jewellery → Earrings with a "
        "selectable environment archetype. The frontend sends this prompt "
        "along with the reference image to /api/generate-image."
    ),
)
async def generate_professional_shot_prompt(
    request: ProfessionalShotPromptRequest,
):
    """Generate the professional commercial earring photography prompt.

    This endpoint returns a complete prompt string that includes:
    - Reference image priority marker (prevents backend double-appendition)
    - Product fidelity — highest priority
    - Anti-redesign rules
    - Anti-symmetry / anti-beautification rules (Phase 4D fix)
    - Product identity preservation
    - Earring type-specific preservation (Hoop/Stud/Dangle)
    - Material & colour fidelity (Task 3 validated)
    - Archetype-specific environment instructions
    - Archetype-specific lighting instructions
    - Optical style (macro product photography)
    - Gemstone presentation
    - Environment interaction
    - Grounding and contact shadows
    - Negative constraints
    - Final verification checklist

    The frontend must send this prompt + reference image to
    /api/generate-image.  The ImageGenerationManager will auto-append
    REFERENCE_PRIORITY_BLOCK and marketplace rules as needed.
    """
    try:
        earring_type = request.earring_type
        archetype = request.archetype

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

        # Validate archetype
        if archetype not in VALID_ENVIRONMENTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid archetype: '{archetype}'. "
                    f"Must be one of: {', '.join(VALID_ENVIRONMENTS)}"
                ),
            )

        prompt = build_professional_shot_prompt(
            earring_type=earring_type,
            environment=archetype,
        )

        logger.info(
            f"Professional commercial earring photography prompt generated: "
            f"earring_type={earring_type or 'generic'} "
            f"archetype={archetype} "
            f"prompt_len={len(prompt)}"
        )

        return ProfessionalShotPromptResponse(
            success=True,
            prompt=prompt,
            earring_type=earring_type,
            archetype=archetype,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Professional commercial earring photography prompt generation failed: {e}")
        return ProfessionalShotPromptResponse(
            success=False,
            error=f"Prompt generation failed: {str(e)}",
        )


@router.get(
    "/earring-professional-shot/prompt/health",
    summary="Professional commercial earring photography prompt health check",
    description="Check if the professional commercial earring photography prompt endpoint is ready.",
)
async def professional_shot_health():
    """Health check for the professional commercial earring photography prompt service."""
    import datetime

    return {
        "status": "ready",
        "service": "earring-professional-shot-prompt",
        "earring_types": ["Hoop", "Stud", "Dangle"],
        "environments": VALID_ENVIRONMENTS,
        "environment_labels": ENVIRONMENT_LABELS,
        "prompt_number": 4,
        "timestamp": datetime.datetime.now().isoformat(),
    }
