"""Master Product Fidelity Layer — GemVision.

Single source of truth for product identity preservation across all
image-generation prompts.  This module is:

- **Provider-independent**: works with Gemini, OpenAI, or any future provider.
- **Marketplace-independent**: contains NO Amazon/Myntra/eBay-specific rules.
- **Reusable**: consumed by prompt_generation_service, prompt_fusion_engine,
  image_generation_manager, and gemini_image_provider.

Architecture::

    REFERENCE IMAGE
          ↓
    PRODUCT ANALYSIS
          ↓
    MASTER PRODUCT FIDELITY   ← this module
          ↓
    MARKETPLACE PRESENTATION  (future Task 2+)
          ↓
    IMAGE GENERATION
          ↓
    FINAL IMAGE

Priority order (never reverse):
    1. PRODUCT FIDELITY
    2. PRODUCT GEOMETRY
    3. MATERIAL + COLOUR ACCURACY
    4. MARKETPLACE COMPLIANCE  (future layer)
    5. LIGHTING / PRESENTATION
    6. AESTHETIC POLISH
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ─── Structured Product Fidelity Model ──────────────────────────────────
# Captures the physical identity of a jewellery SKU.  Fields are optional —
# missing data is OMITTED from generated instructions (never invented).


class FidelityStone(BaseModel):
    """A single stone/gemstone on the product."""

    model_config = ConfigDict(extra="allow")

    count: Optional[int] = Field(None, description="Number of stones of this type")
    shape: Optional[str] = Field(None, description="Stone shape (round, oval, marquise, ...)")
    colour: Optional[str] = Field(None, description="Stone colour")
    placement: Optional[str] = Field(
        None,
        description="Where on the product this stone type is placed",
    )
    size_relationship: Optional[str] = Field(
        None,
        description="Relative size compared to other stones (e.g. 'central stone is larger')",
    )
    setting: Optional[str] = Field(
        None,
        description="Setting type (prong, bezel, pave, channel, ...)",
    )


class FidelityMetal(BaseModel):
    """Metal appearance and finish."""

    model_config = ConfigDict(extra="allow")

    colour: Optional[str] = Field(
        None,
        description="Metal colour (yellow gold, rose gold, silver, platinum, ...)",
    )
    appearance: Optional[str] = Field(
        None,
        description="Overall metal appearance (polished, brushed, matte, ...)",
    )
    plating: Optional[str] = Field(
        None,
        description="Plating description if applicable",
    )


class FidelityProportions(BaseModel):
    """Physical proportions of the product."""

    model_config = ConfigDict(extra="allow")

    length_width_relationship: Optional[str] = Field(
        None,
        description="How length relates to width (e.g. 'elongated drop earring')",
    )
    overall_geometry: Optional[str] = Field(
        None,
        description="Overall shape geometry (circular, teardrop, geometric, organic, ...)",
    )
    notes: Optional[str] = Field(
        None,
        description="Any notable proportion characteristics",
    )


class FidelityAttachment(BaseModel):
    """How the jewellery attaches (hook, post, clasp, etc.)."""

    model_config = ConfigDict(extra="allow")

    type: Optional[str] = Field(
        None,
        description="Attachment type (hook, post, lever-back, clip, clasp, ...)",
    )
    visible: Optional[bool] = Field(
        None,
        description="Whether the attachment is visible in the reference image",
    )
    details: Optional[str] = Field(
        None,
        description="Additional attachment details visible in the reference",
    )


class FidelityDecorative(BaseModel):
    """Decorative elements beyond stones and metal."""

    model_config = ConfigDict(extra="allow")

    elements: Optional[List[str]] = Field(
        None,
        description="List of decorative elements (cut-outs, engravings, filigree, ...)",
    )
    surface_texture: Optional[str] = Field(
        None,
        description="Surface texture (smooth, hammered, engraved, ...)",
    )
    symmetry: Optional[str] = Field(
        None,
        description="Symmetry description (symmetric, asymmetric, ...)",
    )


class ProductFidelity(BaseModel):
    """Master product identity — the single source of truth.

    Every field is optional.  Only information that can be derived from
    the reference image is populated.  Missing fields are OMITTED from
    generated instructions — never invented.
    """

    model_config = ConfigDict(extra="allow")

    # ── Identity ────────────────────────────────────────────────────
    product_type: Optional[str] = Field(
        None,
        description="Product type (Earring, Ring, Necklace, ...)",
    )
    quantity: Optional[str] = Field(
        None,
        description="Single piece or pair",
    )
    design_summary: Optional[str] = Field(
        None,
        description="One-line description of the overall design",
    )

    # ── Stones ──────────────────────────────────────────────────────
    total_stone_count: Optional[int] = Field(
        None,
        description="Total number of stones on the product",
    )
    stones: Optional[List[FidelityStone]] = Field(
        None,
        description="Detailed stone information grouped by type",
    )

    # ── Metal ───────────────────────────────────────────────────────
    metal: Optional[FidelityMetal] = Field(
        None,
        description="Metal appearance and finish",
    )

    # ── Proportions ─────────────────────────────────────────────────
    proportions: Optional[FidelityProportions] = Field(
        None,
        description="Physical proportions and geometry",
    )

    # ── Attachment ──────────────────────────────────────────────────
    attachment: Optional[FidelityAttachment] = Field(
        None,
        description="How the jewellery attaches (hook, post, clasp, ...)",
    )

    # ── Decorative Details ──────────────────────────────────────────
    decorative: Optional[FidelityDecorative] = Field(
        None,
        description="Decorative elements, texture, and symmetry",
    )

    # ── Unknown / Occluded ──────────────────────────────────────────
    unknown_details: Optional[List[str]] = Field(
        None,
        description="Details that could not be determined from the reference image",
    )

    # ── Generation Errors to Avoid ──────────────────────────────────
    avoid_errors: Optional[List[str]] = Field(
        None,
        description="Known generation errors specific to this product",
    )


# ─── Instruction Builders ───────────────────────────────────────────────
# These generate the text instructions that get injected into image-
# generation prompts.  Every builder follows the same principle:
#   - Only include information that IS known
#   - Never invent information for unknown fields
#   - Keep instructions concise and actionable


def _fmt_list(items: Optional[List[str]]) -> str:
    """Format a list of strings as a comma-separated string."""
    if not items:
        return ""
    return ", ".join(str(i) for i in items)


def _fmt_stones(stones: Optional[List[FidelityStone]]) -> str:
    """Format stone details into instruction text."""
    if not stones:
        return ""
    parts: List[str] = []
    for s in stones:
        segs: List[str] = []
        if s.count is not None:
            segs.append(f"{s.count}x")
        if s.shape:
            segs.append(s.shape)
        if s.colour:
            segs.append(s.colour)
        if s.placement:
            segs.append(f"placed at {s.placement}")
        if s.setting:
            segs.append(f"({s.setting} setting)")
        if segs:
            parts.append(" ".join(segs))
    return "; ".join(parts)


def build_fidelity_instruction(fidelity: Optional[ProductFidelity]) -> str:
    """Build the canonical product fidelity instruction for image-generation prompts.

    This is the **single source of truth** text that gets injected into
    every image-generation prompt.  It replaces the previously scattered
    PRODUCT_PRESERVATION_CONSTRAINTS, PRODUCT_PRESERVATION_BLOCK,
    REFERENCE_PRIORITY_BLOCK, and REFERENCE_IMAGE_ANCHOR constants.

    When ``fidelity`` is None or empty, a generic instruction is returned
    that still enforces the reference-image-wins principle.
    """
    if not fidelity:
        return GENERIC_FIDELITY_INSTRUCTION

    parts: List[str] = ["PRODUCT FIDELITY — NON-NEGOTIABLE:"]

    # ── Identity ────────────────────────────────────────────────
    identity_parts: List[str] = []
    if fidelity.product_type:
        identity_parts.append(fidelity.product_type)
    if fidelity.quantity:
        identity_parts.append(fidelity.quantity)
    if fidelity.design_summary:
        identity_parts.append(f"— {fidelity.design_summary}")
    if identity_parts:
        parts.append(f"Product: {' '.join(identity_parts)}.")

    # ── Stones ──────────────────────────────────────────────────
    if fidelity.total_stone_count is not None:
        parts.append(f"Total stone count: {fidelity.total_stone_count}.")
    stone_text = _fmt_stones(fidelity.stones)
    if stone_text:
        parts.append(f"Stones: {stone_text}.")

    # ── Metal ───────────────────────────────────────────────────
    if fidelity.metal:
        metal_segs: List[str] = []
        if fidelity.metal.colour:
            metal_segs.append(fidelity.metal.colour)
        if fidelity.metal.appearance:
            metal_segs.append(fidelity.metal.appearance)
        if fidelity.metal.plating:
            metal_segs.append(f"({fidelity.metal.plating})")
        if metal_segs:
            parts.append(f"Metal: {' '.join(metal_segs)}.")

    # ── Proportions ─────────────────────────────────────────────
    if fidelity.proportions:
        prop_segs: List[str] = []
        if fidelity.proportions.overall_geometry:
            prop_segs.append(f"Geometry: {fidelity.proportions.overall_geometry}")
        if fidelity.proportions.length_width_relationship:
            prop_segs.append(
                f"Proportions: {fidelity.proportions.length_width_relationship}"
            )
        if prop_segs:
            parts.append("; ".join(prop_segs) + ".")

    # ── Attachment ──────────────────────────────────────────────
    if fidelity.attachment:
        att_segs: List[str] = []
        if fidelity.attachment.type:
            att_segs.append(f"Attachment: {fidelity.attachment.type}")
        if fidelity.attachment.details:
            att_segs.append(fidelity.attachment.details)
        if att_segs:
            parts.append("; ".join(att_segs) + ".")

    # ── Decorative Details ──────────────────────────────────────
    if fidelity.decorative:
        dec_segs: List[str] = []
        if fidelity.decorative.elements:
            dec_segs.append(
                f"Decorative elements: {_fmt_list(fidelity.decorative.elements)}"
            )
        if fidelity.decorative.surface_texture:
            dec_segs.append(f"Surface: {fidelity.decorative.surface_texture}")
        if fidelity.decorative.symmetry:
            dec_segs.append(f"Symmetry: {fidelity.decorative.symmetry}")
        if dec_segs:
            parts.append("; ".join(dec_segs) + ".")

    # ── Unknown Details ─────────────────────────────────────────
    if fidelity.unknown_details:
        parts.append(
            f"Uncertain details (do NOT invent): "
            f"{_fmt_list(fidelity.unknown_details)}."
        )

    # ── Avoid Errors ────────────────────────────────────────────
    if fidelity.avoid_errors:
        parts.append(f"AVOID: {_fmt_list(fidelity.avoid_errors)}.")

    # ── Reference Priority ──────────────────────────────────────
    parts.append(REFERENCE_PRIORITY_INSTRUCTION)

    return "\n".join(parts)


# ─── Fidelity QA Evaluation ─────────────────────────────────────────────


class FidelityQAResult(BaseModel):
    """Result of a fidelity evaluation comparing reference to generated."""

    model_config = ConfigDict(extra="allow")

    design_match: Optional[bool] = Field(
        None, description="Does the overall design match?"
    )
    stone_count_match: Optional[bool] = Field(
        None, description="Is the stone count correct?"
    )
    stone_configuration_match: Optional[bool] = Field(
        None, description="Is the stone arrangement correct?"
    )
    metal_colour_match: Optional[bool] = Field(
        None, description="Is the metal colour correct?"
    )
    geometry_match: Optional[bool] = Field(
        None, description="Is the product geometry correct?"
    )
    proportion_match: Optional[bool] = Field(
        None, description="Are the proportions correct?"
    )
    attachment_match: Optional[bool] = Field(
        None, description="Is the attachment type correct?"
    )
    decorative_detail_match: Optional[bool] = Field(
        None, description="Are decorative details preserved?"
    )
    single_or_pair_match: Optional[bool] = Field(
        None, description="Is the single/pair configuration correct?"
    )
    overall_score: Optional[float] = Field(
        None,
        description="Overall fidelity score 0.0–1.0",
        ge=0.0,
        le=1.0,
    )
    notes: Optional[str] = Field(
        None, description="Additional notes or failure details"
    )


def evaluate_fidelity(
    fidelity: Optional[ProductFidelity],
    generated_attributes: Optional[Dict[str, Any]] = None,
) -> FidelityQAResult:
    """Evaluate how well a generated image matches the product fidelity spec.

    This is the **data/interface foundation** for future validation.
    When ``generated_attributes`` is None (no comparison data available),
    returns a result with all ``None`` fields — suitable for manual QA.

    When ``generated_attributes`` IS provided, performs a lightweight
    attribute-by-attribute comparison.  This is NOT a computer-vision
    system — it compares structured metadata.

    Future enhancement: plug in a vision model to populate
    ``generated_attributes`` from the generated image.
    """
    if not fidelity or not generated_attributes:
        return FidelityQAResult(
            notes="No comparison data available — manual QA required"
        )

    result = FidelityQAResult()

    # ── Stone count ─────────────────────────────────────────────
    if fidelity.total_stone_count is not None:
        gen_count = generated_attributes.get("total_stone_count")
        result.stone_count_match = (
            int(gen_count) == fidelity.total_stone_count
            if gen_count is not None
            else None
        )

    # ── Metal colour ────────────────────────────────────────────
    if fidelity.metal and fidelity.metal.colour:
        gen_metal = generated_attributes.get("metal_colour", "")
        result.metal_colour_match = (
            fidelity.metal.colour.lower() in gen_metal.lower()
            if gen_metal
            else None
        )

    # ── Product type / single-or-pair ───────────────────────────
    if fidelity.quantity:
        gen_qty = generated_attributes.get("quantity", "")
        result.single_or_pair_match = (
            fidelity.quantity.lower() in gen_qty.lower()
            if gen_qty
            else None
        )

    # ── Geometry ────────────────────────────────────────────────
    if fidelity.proportions and fidelity.proportions.overall_geometry:
        gen_geom = generated_attributes.get("geometry", "")
        result.geometry_match = (
            gen_geom.lower() in fidelity.proportions.overall_geometry.lower()
            or fidelity.proportions.overall_geometry.lower() in gen_geom.lower()
            if gen_geom
            else None
        )

    # ── Attachment ──────────────────────────────────────────────
    if fidelity.attachment and fidelity.attachment.type:
        gen_att = generated_attributes.get("attachment_type", "")
        result.attachment_match = (
            fidelity.attachment.type.lower() in gen_att.lower()
            if gen_att
            else None
        )

    # ── Overall score ───────────────────────────────────────────
    checks = [
        result.design_match,
        result.stone_count_match,
        result.stone_configuration_match,
        result.metal_colour_match,
        result.geometry_match,
        result.proportion_match,
        result.attachment_match,
        result.decorative_detail_match,
        result.single_or_pair_match,
    ]
    evaluated = [c for c in checks if c is not None]
    if evaluated:
        result.overall_score = sum(1.0 for c in evaluated if c) / len(evaluated)

    return result


# ─── Canonical Constants ────────────────────────────────────────────────
# These replace the previously scattered constants across multiple files.
# Every consumer imports from HERE as the single source of truth.


GENERIC_FIDELITY_INSTRUCTION = (
    "PRODUCT FIDELITY — NON-NEGOTIABLE:\n"
    "The uploaded reference image is the authoritative source of truth.\n"
    "Preserve the EXACT jewellery design: same shape, same stones, same "
    "metal colour, same proportions, same craftsmanship.\n"
    "Do NOT redesign the product.\n"
    "Do NOT add or remove stones.\n"
    "Do NOT change stone count, shape, colour, or placement.\n"
    "Do NOT change metal colour or finish.\n"
    "Do NOT change proportions or geometry.\n"
    "Do NOT invent decorative elements.\n"
    "Do NOT remove visible hooks, clasps, or attachment mechanisms.\n"
    "Do NOT turn a single earring into a pair or vice versa.\n"
    "If a detail is unclear from the reference, do NOT confidently invent it.\n"
    "Only modify: lighting, background, camera angle, composition, "
    "sharpness, resolution, and commercial presentation quality."
)

REFERENCE_PRIORITY_INSTRUCTION = (
    "REFERENCE IMAGE PRIORITY: MAXIMUM\n"
    "The uploaded image is the single authoritative visual source.\n"
    "Reproduce the product EXACTLY as shown in it — same design, same "
    "geometry, same stone placement and count, same shape, proportions, "
    "metal appearance, texture, and craftsmanship.\n"
    "Do not create a similar piece. Do not replace stones. "
    "Do not change patterns. Do not add decoration. "
    "Do not remove existing elements.\n"
    "Act as a luxury jewellery photographer capturing the exact uploaded "
    "product — NOT a designer creating a new concept.\n"
    "Use the text prompt only for scene, lighting, camera, and presentation."
)

PRODUCT_PRESERVATION_CONSTRAINTS = (
    "CRITICAL PRODUCT PRESERVATION CONSTRAINTS (NON-NEGOTIABLE):\n"
    "1. EXACT PRODUCT GEOMETRY: Preserve the EXACT overall shape, exact "
    "dimensions, exact proportions, and exact silhouette of this product. "
    "Do not stretch, compress, enlarge, or reduce any element.\n"
    "2. STONE PLACEMENT: Preserve every gemstone position, gemstone count, "
    "gemstone colors, and gemstone arrangement exactly as they appear. "
    "Do not add new gemstones. Do not remove existing gemstones. "
    "Do not change gemstone colors or shapes.\n"
    "3. METAL DETAILS: Preserve all carvings, texture, finish, engravings, "
    "and craftsmanship details exactly. Do not smooth over intricate work. "
    "Do not simplify complex patterns.\n"
    "4. HANGING ELEMENTS: Preserve all dangling beads, bead count, bead "
    "positions, and chain positions exactly. Do not add or remove any "
    "hanging elements.\n"
    "5. PRODUCT IDENTITY: The generated image MUST represent the EXACT "
    "same product, not a redesigned or inspired variation. This is a "
    "photography task, not a design task.\n"
    "6. WHAT YOU MAY CHANGE (ONLY): Studio lighting quality, camera lens "
    "quality, background, shadows, reflections, sharpness, resolution, "
    "commercial presentation quality.\n"
    "7. WHAT YOU MUST NOT CHANGE: The jewellery piece itself — its shape, "
    "stones, metalwork, engravings, proportions, colors, textures, or any "
    "visible decorative elements.\n"
    "8. ANTI-REDESIGN RULE: This is NOT a design task. Do NOT redesign "
    "the product. Do NOT invent new elements. Do NOT create a new "
    "interpretation. Reproduce the EXACT product in a professional "
    "studio setting."
)

REFERENCE_IMAGE_ANCHOR = (
    "PRODUCT IDENTITY LOCK: The attached image is the EXACT product to "
    "photograph. Preserve the jewellery EXACTLY as shown in it — same "
    "design, shape, gemstone placement and count, metal colour, texture, "
    "and proportions. Do not redesign, replace, or invent any part of the "
    "jewellery. Only change the background, environment, camera angle, "
    "composition, lighting, and styling. Treat this as professional product "
    "photography of the attached piece — never a creative reimagining."
)

REFERENCE_PRIORITY_BLOCK = (
    "REFERENCE IMAGE PRIORITY: MAXIMUM\n"
    "\n"
    "PRIORITY RULE: REFERENCE PRODUCT IDENTITY > SCENE / CREATIVE "
    "INSTRUCTION.\n"
    "The uploaded image is the single authoritative source of "
    "product truth.  The text prompt may describe the desired scene, "
    "presentation, or styling — but it must never override, reinterpret, "
    "or replace the physical identity of the product shown in the "
    "reference image.\n"
    "\n"
    "PRODUCT IDENTITY — PRESERVE EXACTLY:\n"
    "• Overall silhouette and outline shape.\n"
    "• Geometry: the exact form (circular, teardrop, geometric, organic, "
    "or any other visible shape).\n"
    "• Proportions: the exact length-to-width ratio, the relationship "
    "between elements, and the relative size of every visible component.\n"
    "• Stone arrangement: preserve every visible stone's position, "
    "spacing, grouping, and spatial relationship to other stones and "
    "to the metal structure.\n"
    "• Stone placement: do not move stones from their visible locations.\n"
    "• Stone characteristics: preserve the visible count, shapes, sizes, "
    "colours, and relative prominence of every stone as shown.\n"
    "• Metal appearance: preserve the exact metal colour, finish, "
    "texture, and surface quality as shown in the reference.\n"
    "• Attachment structure: preserve any visible hooks, posts, "
    "clasps, lever-backs, chains, or other attachment mechanisms "
    "exactly as shown.\n"
    "• Decorative details: preserve all visible filigree, engravings, "
    "cut-outs, milgrain, surface patterns, and ornamental elements.\n"
    "• Surface details: preserve visible texture, polish, brushing, "
    "hammering, or any other surface treatment as shown.\n"
    "• Symmetry or asymmetry: preserve the exact visible symmetry — "
    "do not symmetrise an asymmetric design or vice versa.\n"
    "\n"
    "WHAT YOU MUST NOT CHANGE:\n"
    "• Do not redesign or reinterpret the product.\n"
    "• Do not simplify or abstract the design.\n"
    "• Do not add stones, decorative elements, or features not shown.\n"
    "• Do not remove stones, decorative elements, or features that are "
    "shown.\n"
    "• Do not change stone arrangement, spacing, or placement.\n"
    "• Do not change proportions or geometry.\n"
    "• Do not change metal colour, finish, or texture.\n"
    "• Do not change attachment structure or type.\n"
    "• Do not change the product's visible size relative to the "
    "reference — do not enlarge or shrink it.\n"
    "• Do not turn a single piece into a pair or a pair into a single "
    "piece.\n"
    "• Do not create a 'similar' or 'inspired' variation.\n"
    "\n"
    "WHAT YOU MAY CHANGE (PRESENTATION ONLY):\n"
    "• Background and environment.\n"
    "• Lighting quality, direction, and colour temperature.\n"
    "• Camera angle, focal length, and depth of field.\n"
    "• Composition and framing.\n"
    "• Sharpness, resolution, and commercial presentation quality.\n"
    "\n"
    "This is professional product photography of the exact uploaded "
    "product — not creative generation, not a redesign, and not a "
    "new interpretation."
)

SCALE_CONTROL_BLOCK = (
    "JEWELLERY PRESERVATION & SCALE CONTROL (NON-NEGOTIABLE):\n"
    "The uploaded jewellery image is the primary reference.\n"
    "Maintain the exact original jewellery design.\n"
    "Preserve original size and proportions.\n"
    "Do not enlarge the jewellery.\n"
    "Do not shrink the jewellery.\n"
    "Do not exaggerate gemstones.\n"
    "Do not modify stone placement.\n"
    "Do not redesign the jewellery.\n"
    "The jewellery must fit naturally according to human anatomy.\n"
    "The final result should look like a real professional jewellery photograph."
)

# ── Preserved from prompt_fusion_engine.py (Layer 3) ────────────────────
# These constants were previously defined inline in prompt_fusion_engine.py.
# They are now centralized here as the single source of truth.

PRODUCT_PRESERVATION_BLOCK = (
    "PRODUCT PRESERVATION (NON-NEGOTIABLE):\n"
    "The uploaded image is the authoritative reference.\n"
    "Preserve the exact jewellery design.\n"
    "Do not redesign the product.\n"
    "Do not change gemstone placement.\n"
    "Do not add new stones.\n"
    "Do not remove existing elements.\n"
    "Do not change shape.\n"
    "Do not change proportions.\n"
    "Do not modify craftsmanship.\n"
    "Do not replace decorative details.\n"
    "Maintain original metal texture and finish.\n"
    "Only improve: lighting, background, camera quality, sharpness, "
    "reflection, commercial presentation."
)

REFERENCE_IMAGE_INSTRUCTION = (
    "REFERENCE IMAGE PRIORITY: MAXIMUM. A reference image of the exact "
    "product is attached. Treat it as the single authoritative visual source "
    "and reproduce the product EXACTLY as shown in it — the same jewellery, "
    "same design, same geometry, same stone placement and count, same shape, "
    "proportions, metal appearance, texture and craftsmanship. Do not create "
    "a similar piece, do not replace stones, do not change patterns, do not "
    "add decoration, do not remove existing elements. Act as a luxury "
    "jewellery photographer capturing the exact uploaded product — NOT a "
    "designer creating a new concept. Use the text prompt only for scene, "
    "lighting, camera, and presentation."
)
