"""API route for the isolated Prompt 2 Close Up Ears workflow."""

from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.earring_close_up_ears_prompt import build_close_up_ears_prompt
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Earring Close Up Ears"])


class CloseUpEarsPromptRequest(BaseModel):
    """Request contract for the fixed Prompt 2 earring workflow."""

    earring_type: Literal["Dangle"] = Field(
        default="Dangle",
        description="Fixed product category for the Prompt 2 reference earring.",
    )


class CloseUpEarsPromptResponse(BaseModel):
    """Response contract containing the isolated Prompt 2 prompt."""

    success: bool
    prompt: Optional[str] = None
    earring_type: Optional[str] = None
    error: Optional[str] = None


@router.post(
    "/earring-close-up-ears/prompt",
    response_model=CloseUpEarsPromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate the Prompt 2 Close Up Ears earring prompt",
    description=(
        "Returns the isolated Close Up Ears prompt. The client must send the "
        "returned prompt and the sole authoritative product reference image to "
        "/api/generate-image."
    ),
)
async def generate_close_up_ears_prompt(
    request: CloseUpEarsPromptRequest,
) -> CloseUpEarsPromptResponse:
    """Return the Prompt 2 close-up ear presentation prompt."""
    try:
        prompt = build_close_up_ears_prompt()
        logger.info(
            "Close Up Ears prompt generated: "
            f"earring_type={request.earring_type} prompt_len={len(prompt)}"
        )
        return CloseUpEarsPromptResponse(
            success=True,
            prompt=prompt,
            earring_type=request.earring_type,
        )
    except Exception as exc:
        logger.error(f"Close Up Ears prompt generation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Close Up Ears prompt generation failed.",
        ) from exc


@router.get(
    "/earring-close-up-ears/prompt/health",
    summary="Check Close Up Ears prompt readiness",
)
async def close_up_ears_prompt_health() -> dict[str, object]:
    """Return readiness information for the isolated Prompt 2 route."""
    return {
        "status": "ready",
        "service": "earring-close-up-ears-prompt",
        "earring_type": "Dangle",
    }
