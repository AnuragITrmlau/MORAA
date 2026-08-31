"""API routes for Macro Shot — Prompt 7.

Provides a single endpoint that builds the complete macro shot prompt.
The frontend calls this endpoint, receives the prompt, and sends
it to /api/generate-image with the reference image.

Flow:
    POST /api/earring-macro-shot/prompt  →  complete prompt string
        ↓
    Frontend sends prompt + reference_image to /api/generate-image
        ↓
    ImageGenerationManager auto-appends REFERENCE_PRIORITY_BLOCK
        + marketplace rules → provider → generated image
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.earring_macro_shot_prompt import (
    build_macro_shot_prompt,
)
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Earring Macro Shot"])


class MacroShotPromptRequest(BaseModel):
    """Request body for macro shot prompt generation."""

    earring_type: Optional[str] = Field(
        None,
        description=(
            'Earring type: "Hoop", "Stud", or "Dangle". '
            "When provided, type-specific preservation rules are included. "
            "When None, generic earring preservation rules are used."
        ),
    )


class MacroShotPromptResponse(BaseModel):
    """Response body for macro shot prompt generation."""

    success: bool
    prompt: Optional[str] = None
    earring_type: Optional[str] = None
    error: Optional[str] = None


@router.post(
    "/earring-macro-shot/prompt",
    response_model=MacroShotPromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate macro shot prompt (Prompt 7)",
    description=(
        "Returns the single authoritative macro shot prompt "
        "for Fashion Jewellery → Earrings. The frontend sends this prompt "
        "along with the reference image to /api/generate-image."
    ),
)
async def generate_macro_shot_prompt(
    request: MacroShotPromptRequest,
):
    """Generate the macro shot prompt.

    This endpoint returns a complete prompt string that includes:
    - Reference image priority marker (prevents backend double-appendition)
    - Product fidelity — absolute priority
    - Anti-redesign rules
    - Anti-symmetry / anti-beautification rules (Phase 4D fix)
    - Product identity preservation
    - Earring type-specific preservation (Hoop/Stud/Dangle)
    - Material & colour fidelity (Task 3 validated)
    - Macro photography requirement
    - Detail visibility rules
    - Framing, focus, and lighting rules
    - Anti-beautification / anti-reconstruction rules
    - Reference priority hierarchy
    - Clean background requirement

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

        prompt = build_macro_shot_prompt(
            earring_type=earring_type,
        )

        logger.info(
            f"Macro shot prompt generated: "
            f"earring_type={earring_type or 'generic'} "
            f"prompt_len={len(prompt)}"
        )

        return MacroShotPromptResponse(
            success=True,
            prompt=prompt,
            earring_type=earring_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Macro shot prompt generation failed: {e}")
        return MacroShotPromptResponse(
            success=False,
            error=f"Prompt generation failed: {str(e)}",
        )


@router.get(
    "/earring-macro-shot/prompt/health",
    summary="Macro shot prompt health check",
    description="Check if the macro shot prompt endpoint is ready.",
)
async def macro_shot_health():
    """Health check for the macro shot prompt service."""
    import datetime

    return {
        "status": "ready",
        "service": "earring-macro-shot-prompt",
        "earring_types": ["Hoop", "Stud", "Dangle"],
        "prompt_number": 7,
        "timestamp": datetime.datetime.now().isoformat(),
    }
