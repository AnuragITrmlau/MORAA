"""Pydantic schemas for the Prompt Fusion Intelligence Engine (PFIE).

GemVision V3 — fuses Gemini product intelligence, ChatGPT creative
direction, product preservation rules, and photography enhancement
instructions into a single final image-generation prompt.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductIntelligence(BaseModel):
    """Structured product facts extracted by Gemini Vision analysis.

    These are the ONLY facts the creative director and fusion engine are
    allowed to use. Fields are optional — missing facts are omitted from
    the fused prompt rather than invented.

    Accepts both camelCase (frontend analysis result) and snake_case keys,
    plus any additional keys (``extra='allow'``) for forward compatibility.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    category: Optional[str] = Field(None, description="Product category (e.g. Jewellery)")
    subcategory: Optional[str] = Field(None, description="Product subcategory")
    jewelleryType: Optional[str] = Field(
        None, alias="jewellery_type",
        description="Jewellery type (Ring, Necklace, Earring, Bracelet, ...)",
    )
    metal: Optional[str] = Field(None, description="Detected metal(s)")
    stones: Optional[str] = Field(None, description="Detected stones/gemstones")
    stonePlacement: Optional[str] = Field(
        None, alias="stone_placement",
        description="Gemstone placement/setting description",
    )
    shape: Optional[str] = Field(None, description="Product shape")
    texture: Optional[str] = Field(None, description="Surface texture")
    finish: Optional[str] = Field(None, description="Surface finish")
    craftsmanship: Optional[str] = Field(None, description="Craftsmanship quality")
    designDetails: Optional[str] = Field(
        None, alias="design_details",
        description="Design details / visual observations",
    )
    wearableType: Optional[str] = Field(
        None, alias="wearable_type",
        description="How the product is worn (finger ring, neck, ear, wrist, ...)",
    )
    # Jewellery Scale & Reference Accuracy fields (additive — JSR).
    # Help the image model understand real-world jewellery proportions so it
    # never generates oversized, tiny, or unrealistically placed jewellery.
    sizeCategory: Optional[str] = Field(
        None, alias="size_category",
        description="Jewellery size category relative to human anatomy (small | medium | large)",
    )
    relativeScale: Optional[str] = Field(
        None, alias="relative_scale",
        description="Jewellery size compared to human anatomy (e.g. small stud, delicate chain)",
    )
    wearPosition: Optional[str] = Field(
        None, alias="wear_position",
        description="Natural wearing location (earlobe, finger, neckline, collarbone, wrist)",
    )
    proportionNotes: Optional[str] = Field(
        None, alias="proportion_notes",
        description="Realistic fitting information for the jewellery on the human body",
    )
    avoidGenerationErrors: Optional[List[str]] = Field(
        None, alias="avoid_generation_errors",
        description="Generation errors to avoid (oversized jewellery, tiny jewellery, unrealistic placement)",
    )


FusionMode = Literal["studio", "lifestyle"]


class PromptFusionRequest(BaseModel):
    """Request to fuse a final image-generation prompt."""

    productIntelligence: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Structured product facts from Gemini vision analysis "
            "(see ProductIntelligence). The fused prompt treats these "
            "as authoritative and never invents additional details."
        ),
    )
    category: str = Field(
        default="professionalShot",
        description="Prompt category (professionalShot, useCaseShot, festive, ...)",
    )
    mode: FusionMode = Field(
        default="studio",
        description="studio = hero product shot; lifestyle = jewellery worn by a model",
    )
    aspectRatio: str = Field(
        default="4:5",
        alias="aspect_ratio",
        description="Aspect ratio of the final generated image",
    )
    imageId: Optional[str] = Field(
        None, alias="image_id",
        description="Optional image/analysis ID for tracking",
    )

    model_config = ConfigDict(populate_by_name=True)


class PromptFusionLayer(BaseModel):
    """One layer of the fused prompt (for transparency/debugging)."""

    name: str = Field(description="Layer name (product_facts, creative_direction, ...)")
    content: str = Field(description="Layer text content")


class PromptFusionResponse(BaseModel):
    """Response from the prompt fusion endpoint."""

    success: bool = Field(..., description="Whether fusion succeeded")
    prompt: Optional[str] = Field(None, description="The final fused image-generation prompt")
    layers: Optional[List[PromptFusionLayer]] = Field(
        None, description="The individual prompt layers that were fused"
    )
    source: Optional[str] = Field(
        None, description="Creative-direction source: 'chatgpt' or 'template'"
    )
    tokensConsumed: int = Field(
        default=0, alias="tokens_consumed",
        description="Tokens consumed by the creative director (0 when template fallback used)",
    )
    generationTimeMs: float = Field(
        default=0.0, alias="generation_time_ms",
        description="Fusion engine wall time in milliseconds",
    )
    error: Optional[str] = Field(None, description="Error message if fusion failed")

    model_config = ConfigDict(populate_by_name=True)
