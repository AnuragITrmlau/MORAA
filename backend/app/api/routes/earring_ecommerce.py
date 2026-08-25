"""API routes for Earring E-Commerce Main Image Prompt Generation.

Provides a single endpoint that builds the complete earring e-commerce
main-image prompt.  The frontend calls this endpoint, receives the
prompt, and sends it to /api/generate-image with the reference image.

Flow:
    POST /api/earring-ecommerce/prompt  →  complete prompt string
        ↓
    Frontend sends prompt + reference_image to /api/generate-image
        ↓
    ImageGenerationManager auto-appends REFERENCE_PRIORITY_BLOCK
        + marketplace rules → provider → generated image
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.earring_ecommerce_prompt import (
    build_earring_ecommerce_prompt,
)
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Earring E-Commerce"])


class EarringEcommercePromptRequest(BaseModel):
    """Request body for earring e-commerce prompt generation."""

    earring_type: Optional[str] = Field(
        None,
        description=(
            'Earring type: "Hoop", "Stud", or "Dangle". '
            "When provided, type-specific preservation rules are included. "
            "When None, generic earring preservation rules are used."
        ),
    )


class EarringEcommercePromptResponse(BaseModel):
    """Response body for earring e-commerce prompt generation."""

    success: bool
    prompt: Optional[str] = None
    earring_type: Optional[str] = None
    error: Optional[str] = None


@router.post(
    "/earring-ecommerce/prompt",
    response_model=EarringEcommercePromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate earring e-commerce main-image prompt",
    description=(
        "Returns the single authoritative earring e-commerce main-image "
        "prompt for Fashion Jewellery → Earrings.  The frontend sends "
        "this prompt along with the reference image to /api/generate-image."
    ),
)
async def generate_earring_ecommerce_prompt(
    request: EarringEcommercePromptRequest,
):
    """Generate the earring e-commerce main-image prompt.

    This endpoint returns a complete prompt string that includes:
    - Reference image priority marker (prevents backend double-appendition)
    - Anti-redesign rules
    - Anti-symmetry / anti-beautification rules (Phase 4D fix)
    - Product identity preservation
    - Earring type-specific preservation (Hoop/Stud/Dangle)
    - Material & colour fidelity
    - Input cleanup rules
    - Angle preservation
    - E-commerce presentation rules
    - Output rule (no card/backing)

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

        prompt = build_earring_ecommerce_prompt(
            earring_type=earring_type,
        )

        logger.info(
            f"Earring e-commerce prompt generated: "
            f"earring_type={earring_type or 'generic'} "
            f"prompt_len={len(prompt)}"
        )

        return EarringEcommercePromptResponse(
            success=True,
            prompt=prompt,
            earring_type=earring_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Earring e-commerce prompt generation failed: {e}")
        return EarringEcommercePromptResponse(
            success=False,
            error=f"Prompt generation failed: {str(e)}",
        )


@router.get(
    "/earring-ecommerce/prompt/health",
    summary="Earring e-commerce prompt health check",
    description="Check if the earring e-commerce prompt endpoint is ready.",
)
async def earring_ecommerce_health():
    """Health check for the earring e-commerce prompt service."""
    import datetime

    return {
        "status": "ready",
        "service": "earring-ecommerce-prompt",
        "earring_types": ["Hoop", "Stud", "Dangle"],
        "timestamp": datetime.datetime.now().isoformat(),
    }
