"""Complementary Shot Prompt — Prompt 5 — MORAA GemVision.

Single authoritative prompt foundation for generating lifestyle editorial
complementary images for Fashion Jewellery → Earrings.

The uploaded product image is the sole source of truth for the jewellery.
This prompt produces a premium lifestyle editorial image with asymmetric
staging, premium contextual surfaces, and storytelling composition.

Distinct from Prompt 4 (Professional Shot):
- Prompt 4 = controlled studio, minimal environment, technical precision
- Prompt 5 = lifestyle editorial, asymmetric arrangement, visual storytelling

Architecture::

    REFERENCE IMAGE (Prompt 1 output preferred, raw upload fallback)
          ↓
    COMPLEMENTARY SHOT FOUNDATION  ← this module
          ↓
    REFERENCE PRIORITY (auto-appended by ImageGenerationManager)
          ↓
    MARKETPLACE PRESENTATION (auto-appended by ImageGenerationManager)
          ↓
    PROVIDER (OPENAI_IDENTITY_ANCHOR prepended by provider)
          ↓
    IMAGE GENERATION

This prompt is designed to:
1. Preserve exact product identity (source of truth = reference image)
2. Prevent anti-symmetry normalisation (Phase 4D failure mode)
3. Prevent colour/material shift (Task 3 validated)
4. Produce a lifestyle editorial complementary image with premium context
5. Use asymmetric editorial arrangement (NOT a plain hero/catalog shot)
6. Emphasize visual storytelling and environmental context
7. Enforce no-human-model / no-props / no-decorative-elements rules
8. Support Hoop, Stud, Dangle earring types
9. Coexist with existing marketplace layers (Amazon India)
"""

from typing import Optional

# ─── Reuse proven constants from Prompt 1 ───────────────────────────────
# These are the battle-tested safety mechanisms validated through
# Phase 4D (anti-symmetry) and Task 3 (colour lock) experiments.
# Importing from Prompt 1 module avoids duplication.

from app.services.earring_ecommerce_prompt import (
    REFERENCE_PRIORITY_MARKER,
    ANTI_SYMMETRY_INSTRUCTION,
    COLOUR_LOCK_INSTRUCTION,
    MATERIAL_FIDELITY_INSTRUCTION,
    EARRING_TYPE_PRESERVATION,
    GENERIC_EARRING_PRESERVATION,
)


# ─── Product Fidelity — Absolute Priority ──────────────────────────────

PRODUCT_FIDELITY_ABSOLUTE = (
    "PRODUCT FIDELITY — ABSOLUTE PRIORITY:\n"
    "The reference image is the single source of truth for the jewellery.\n"
    "Preserve the jewellery exactly as shown in the reference.\n"
    "\n"
    "DO NOT:\n"
    "• redesign the jewellery\n"
    "• reinterpret the jewellery\n"
    "• beautify by changing its structure\n"
    "• add stones\n"
    "• remove stones\n"
    "• change stone count\n"
    "• change stone shape\n"
    "• change stone placement\n"
    "• change bead count\n"
    "• change bead arrangement\n"
    "• change prongs\n"
    "• change facets\n"
    "• change clasp/lock\n"
    "• change hooks\n"
    "• change links\n"
    "• change chains\n"
    "• change metal structure\n"
    "• change metal color\n"
    "• change finish\n"
    "• change proportions\n"
    "• change thickness\n"
    "• change geometry\n"
    "\n"
    "Every visible jewellery component must correspond to the reference.\n"
    "If a detail is unclear in the reference, DO NOT invent it.\n"
    "The jewellery must remain the SAME physical product."
)


# ─── Staging Requirements ─────────────────────────────────────────────

STAGING_INSTRUCTION = (
    "STAGING (NON-NEGOTIABLE):\n"
    "Use a minimal premium editorial surface.\n"
    "\n"
    "Allowed examples:\n"
    "• neutral beige travertine\n"
    "• matte stone\n"
    "• plaster slab\n"
    "• neutral geometric podium\n"
    "• subtle ribbed architectural surface\n"
    "• muted warm-grey or cream textured surface\n"
    "\n"
    "The surface must remain secondary to the jewellery.\n"
    "\n"
    "DO NOT use:\n"
    "• plants\n"
    "• flowers\n"
    "• colored fabric\n"
    "• decorative accessories\n"
    "• jewellery boxes\n"
    "• branded objects\n"
    "• excessive ornaments\n"
    "• busy backgrounds\n"
    "• lifestyle scenes\n"
    "• human models\n"
    "• hands\n"
    "• body parts"
)


# ─── Jewellery Arrangement ─────────────────────────────────────────────

ARRANGEMENT_INSTRUCTION = (
    "JEWELLERY ARRANGEMENT (NON-NEGOTIABLE):\n"
    "Create an asymmetric editorial arrangement.\n"
    "\n"
    "For a pair of earrings:\n"
    "• One earring should rest naturally flat or at a slight angle on the\n"
    "  elevated/riser surface.\n"
    "• The second earring should be positioned slightly offset or leaning\n"
    "  on the lower surface.\n"
    "• The two pieces should not form a perfectly symmetrical hero\n"
    "  arrangement.\n"
    "• The arrangement must reveal depth, thickness, structure, and\n"
    "  dimensionality.\n"
    "• Both earrings must remain clearly visible.\n"
    "\n"
    "The positioning must obey realistic physical gravity.\n"
    "NO floating jewellery.\n"
    "NO impossible intersections.\n"
    "NO jewellery passing through the surface.\n"
    "NO physically impossible orientation."
)


# ─── Physical Contact ──────────────────────────────────────────────────

PHYSICAL_CONTACT_INSTRUCTION = (
    "PHYSICAL CONTACT (NON-NEGOTIABLE):\n"
    "Jewellery must appear physically present in the scene.\n"
    "\n"
    "Use realistic:\n"
    "• contact shadows\n"
    "• grounding shadows\n"
    "• occlusion\n"
    "• weight\n"
    "• surface contact\n"
    "• reflections\n"
    "\n"
    "Do not make the jewellery look pasted, cut out, or digitally floating."
)


# ─── Camera ────────────────────────────────────────────────────────────

CAMERA_INSTRUCTION = (
    "CAMERA (NON-NEGOTIABLE):\n"
    "Use an elevated three-quarter editorial perspective.\n"
    "Preferred viewpoint: approximately 45-degree elevated angle or a\n"
    "subtle diagonal top-down perspective.\n"
    "\n"
    "The camera angle should reveal:\n"
    "• jewellery depth\n"
    "• thickness\n"
    "• metal structure\n"
    "• gemstone brilliance\n"
    "• dimensional form\n"
    "\n"
    "Avoid an extreme perspective that distorts the jewellery."
)


# ─── Lighting ──────────────────────────────────────────────────────────

LIGHTING_INSTRUCTION = (
    "LIGHTING (NON-NEGOTIABLE):\n"
    "Use soft directional studio lighting.\n"
    "\n"
    "Lighting should produce:\n"
    "• controlled metal highlights\n"
    "• natural gemstone brilliance\n"
    "• clean dimensional modelling\n"
    "• delicate but defined shadows\n"
    "• realistic surface reflections\n"
    "\n"
    "Do not create exaggerated glow, artificial sparkle, or fantasy lighting."
)


# ─── Background / Color ────────────────────────────────────────────────

BACKGROUND_COLOR_INSTRUCTION = (
    "BACKGROUND / COLOR (NON-NEGOTIABLE):\n"
    "Use muted neutral tones only.\n"
    "\n"
    "Preferred palette:\n"
    "• soft beige\n"
    "• warm grey\n"
    "• cream\n"
    "• muted stone\n"
    "• neutral plaster\n"
    "\n"
    "The background/surface must complement the jewellery without competing\n"
    "with it.\n"
    "\n"
    "If the jewellery contains colorful gemstones such as emeralds or\n"
    "sapphires, the environment should remain sufficiently neutral for those\n"
    "gemstones to remain visually prominent.\n"
    "\n"
    "DO NOT use highly saturated backgrounds."
)


# ─── Visual Hierarchy ──────────────────────────────────────────────────

VISUAL_HIERARCHY_INSTRUCTION = (
    "VISUAL HIERARCHY (NON-NEGOTIABLE):\n"
    "Jewellery = PRIMARY SUBJECT.\n"
    "Surface and staging elements = SECONDARY.\n"
    "\n"
    "The jewellery should immediately attract the viewer's attention.\n"
    "The environment must support the product rather than become the subject.\n"
    "\n"
    "Target visual hierarchy:\n"
    "approximately 90% jewellery focus,\n"
    "approximately 10% environment/staging support.\n"
    "\n"
    "This is a visual-priority rule, NOT permission to enlarge or distort\n"
    "the jewellery."
)


# ─── Negative Space Preservation ──────────────────────────────────────

NEGATIVE_SPACE_INSTRUCTION = (
    "NEGATIVE SPACE — HARD REQUIREMENT (NON-NEGOTIABLE):\n"
    "The reference jewellery contains intentional OPEN / EMPTY areas.\n"
    "These are structural features, not gaps to fill.\n"
    "\n"
    "You MUST preserve every open/hollow region:\n"
    "• Hollow crescent or open wireframe structures must remain hollow.\n"
    "• Open centres of circular or geometric frames must remain empty.\n"
    "• Spaces between hanging elements must remain separate.\n"
    "• Gaps between bead clusters must remain visible.\n"
    "• Openwork, filigree, or cut-out patterns must stay open.\n"
    "\n"
    "DO NOT fill any internal void with:\n"
    "• Gold or metal material\n"
    "• Skin or flesh tone\n"
    "• Background colour\n"
    "• Gemstone material\n"
    "• Decorative texture or pattern\n"
    "• Shadow or shading\n"
    "\n"
    "The empty space IS part of the jewellery geometry.\n"
    "Filling it changes the product identity."
)


# ─── Bead / Pearl Cluster Preservation ─────────────────────────────────

BEAD_CLUSTER_PRESERVATION_INSTRUCTION = (
    "BEAD AND PEARL CLUSTER PRESERVATION (NON-NEGOTIABLE):\n"
    "If the reference jewellery contains bead clusters, pearl groups,\n"
    "or dangling bead arrangements:\n"
    "\n"
    "• Each individual bead/pearl must remain visually\n"
    "  distinguishable — no merging, fusing, or melting.\n"
    "• Bead clusters must retain their individual separation — gaps\n"
    "  between beads are part of the design.\n"
    "• Large faceted teardrop drops must remain individually\n"
    "  identifiable — each drop is a separate component.\n"
    "• Hanging bead arrangements must preserve the exact count and\n"
    "  relative positioning.\n"
    "• Bead sizes must match the reference — do not enlarge small\n"
    "  beads or shrink large ones.\n"
    "\n"
    "DO NOT allow:\n"
    "• Fused beads that merge into a single mass\n"
    "• Melted or blob-like bead clusters\n"
    "• Missing drops that were present in the reference\n"
    "• Invented drops that were not in the reference\n"
    "• Random bead blobs replacing structured clusters"
)


# ─── Strictly Forbidden ───────────────────────────────────────────────

STRICTLY_FORBIDDEN = (
    "STRICTLY FORBIDDEN — DO NOT generate:\n"
    "• No redesign\n"
    "• No additional jewellery\n"
    "• No additional stones\n"
    "• No missing stones\n"
    "• No fake gemstones\n"
    "• No altered prongs\n"
    "• No altered clasp\n"
    "• No altered metal structure\n"
    "• No artificial jewellery extensions\n"
    "• No floating pieces\n"
    "• No impossible physics\n"
    "• No humans\n"
    "• No hands\n"
    "• No models\n"
    "• No plants\n"
    "• No flowers\n"
    "• No fabric\n"
    "• No jewellery boxes\n"
    "• No logos\n"
    "• No text\n"
    "• No watermark\n"
    "• No brand elements\n"
    "• No clutter\n"
    "• No busy lifestyle environment"
)


# ─── Quality Control Checklist ─────────────────────────────────────────

QUALITY_CONTROL_CHECKLIST = (
    "QUALITY CONTROL — Before accepting the generated result, verify:\n"
    "\n"
    "1. Product identity matches the reference.\n"
    "2. Stone count and placement are preserved.\n"
    "3. Prongs and settings are preserved.\n"
    "4. Beads/components are preserved.\n"
    "5. Clasp/lock/hook structure is preserved.\n"
    "6. Metal color and structure are preserved.\n"
    "7. Jewellery proportions are preserved.\n"
    "8. Both pieces are physically grounded.\n"
    "9. Contact shadows look realistic.\n"
    "10. No piece is floating.\n"
    "11. No AI-generated jewellery components have been introduced.\n"
    "12. Background remains neutral and secondary.\n"
    "13. Jewellery remains the dominant visual subject.\n"
    "14. No human, decorative, branded, or unrelated object appears.\n"
    "\n"
    "If any answer is FAIL, correct the composition before generating the\n"
    "final image."
)


# ─── Complete Prompt Builder ───────────────────────────────────────────
def build_complementary_shot_prompt(
    earring_type: Optional[str] = None,
) -> str:
    """Build the single authoritative Prompt 5 Complementary Shot prompt.

    This is the complete prompt that gets sent as the user prompt to
    /api/generate-image.  The ImageGenerationManager will auto-append
    REFERENCE_PRIORITY_BLOCK (if reference image present) and marketplace
    rules (if marketplace specified).

    The prompt includes the REFERENCE IMAGE PRIORITY: MAXIMUM marker to
    prevent double-appendition of REFERENCE_PRIORITY_BLOCK.

    Args:
        earring_type: Optional earring type ("Hoop", "Stud", "Dangle").
            When provided, type-specific preservation rules are included.
            When None, generic earring preservation rules are used.

    Returns:
        The complete Prompt 5 Complementary Shot prompt string.
    """
    parts: list[str] = []

    # ── Header ──────────────────────────────────────────────────
    parts.append(
        "TASK: Complementary Lifestyle Editorial Shot.\n"
        "Generate a premium lifestyle editorial complementary image of the\n"
        "EXACT jewellery shown in the reference image.\n"
        "\n"
        "This is visually DISTINCT from the Professional Shot (Prompt 4).\n"
        "While Prompt 4 uses a controlled studio environment with minimal\n"
        "context, this shot uses asymmetric arrangement, premium contextual\n"
        "surfaces, and storytelling composition to create a richer editorial\n"
        "narrative.\n"
        "\n"
        "The jewellery remains the dominant visual subject, but the\n"
        "environment provides tasteful luxury context and depth.\n"
        "This is NOT a plain hero/catalog shot and must NOT replicate a\n"
        "standard e-commerce composition."
    )

    # ── Reference Priority (prevents backend double-appendition) ──
    parts.append(REFERENCE_PRIORITY_MARKER)

    # ── Product Fidelity — Absolute Priority ────────────────────
    parts.append(PRODUCT_FIDELITY_ABSOLUTE)

    # ── Anti-Redesign ───────────────────────────────────────────
    parts.append(
        "ANTI-REDESIGN RULE (NON-NEGOTIABLE):\n"
        "This is a PRODUCT PHOTOGRAPHY task, NOT a design task.\n"
        "You are photographing the EXACT uploaded product in a premium\n"
        "editorial staging setting. You are NOT designing a new earring,\n"
        "creating an inspired variation, or improving a product.\n"
        "The generated image must show the EXACT same product — same shape,\n"
        "same stones, same metal, same proportions, same craftsmanship,\n"
        "same asymmetry, same imperfections.\n"
        "Only the presentation changes: background surface, lighting,\n"
        "composition, arrangement, and editorial quality."
    )

    # ── Anti-Symmetry (CRITICAL — Phase 4D failure mode) ────────
    parts.append(ANTI_SYMMETRY_INSTRUCTION)

    # ── Product Identity Preservation ───────────────────────────
    parts.append(
        "PRODUCT IDENTITY — PRESERVE EXACTLY:\n"
        "• Overall silhouette and outline shape.\n"
        "• Geometry: the exact form (circular, teardrop, geometric,\n"
        "  organic, or any other visible shape).\n"
        "• Proportions: the exact length-to-width ratio, the relationship\n"
        "  between elements, and the relative size of every visible\n"
        "  component.\n"
        "• Stone arrangement: preserve every visible stone's position,\n"
        "  spacing, grouping, and spatial relationship to other stones and\n"
        "  to the metal structure.\n"
        "• Stone placement: do not move stones from their visible\n"
        "  locations.\n"
        "• Stone characteristics: preserve the visible count, shapes,\n"
        "  sizes, colours, and relative prominence of every stone as shown.\n"
        "• Metal appearance: preserve the exact metal colour, finish,\n"
        "  texture, and surface quality as shown in the reference.\n"
        "• Attachment structure: preserve any visible hooks, posts,\n"
        "  clasps, lever-backs, chains, or other attachment mechanisms\n"
        "  exactly as shown.\n"
        "• Decorative details: preserve all visible filigree, engravings,\n"
        "  cut-outs, milgrain, surface patterns, and ornamental elements.\n"
        "• Surface details: preserve visible texture, polish, brushing,\n"
        "  hammering, or any other surface treatment as shown."
    )

    # ── Earring Type ────────────────────────────────────────────
    if earring_type and earring_type in EARRING_TYPE_PRESERVATION:
        parts.append(EARRING_TYPE_PRESERVATION[earring_type])
    else:
        parts.append(GENERIC_EARRING_PRESERVATION)

    # ── Material / Colour Fidelity ──────────────────────────────
    parts.append(MATERIAL_FIDELITY_INSTRUCTION)

    # ── Colour Lock (Task 3 validated — 41% gold shift reduction) ─
    parts.append(COLOUR_LOCK_INSTRUCTION)

    # ── Staging ─────────────────────────────────────────────────
    parts.append(STAGING_INSTRUCTION)

    # ── Jewellery Arrangement ───────────────────────────────────
    parts.append(ARRANGEMENT_INSTRUCTION)

    # ── Physical Contact ────────────────────────────────────────
    parts.append(PHYSICAL_CONTACT_INSTRUCTION)

    # ── Camera ──────────────────────────────────────────────────
    parts.append(CAMERA_INSTRUCTION)

    # ── Lighting ────────────────────────────────────────────────
    parts.append(LIGHTING_INSTRUCTION)

    # ── Background / Color ──────────────────────────────────────
    parts.append(BACKGROUND_COLOR_INSTRUCTION)

    # ── Visual Hierarchy ────────────────────────────────────────
    parts.append(VISUAL_HIERARCHY_INSTRUCTION)

    # ── Storytelling Composition ────────────────────────────────
    parts.append(
        "STORYTELLING COMPOSITION (NON-NEGOTIABLE):\n"
        "This is a lifestyle editorial shot, NOT a controlled studio product\n"
        "shot. The composition should feel natural and aspirational — as if\n"
        "the jewellery belongs in this premium environment.\n"
        "\n"
        "Composition principles:\n"
        "• Asymmetric, dynamic arrangement — not perfectly centered.\n"
        "• Natural visual flow that guides the eye to the jewellery.\n"
        "• Environmental context that enhances the product narrative.\n"
        "• Subtle depth and layering in the scene.\n"
        "• The environment tells a story about the product's premium\n"
        "  positioning and target audience.\n"
        "\n"
        "The jewellery must remain the clear primary focal point.\n"
        "The environment supports the narrative without overwhelming."
    )

    # ── Negative Space ──────────────────────────────────────────
    parts.append(NEGATIVE_SPACE_INSTRUCTION)

    # ── Bead / Pearl Cluster Preservation ───────────────────────
    parts.append(BEAD_CLUSTER_PRESERVATION_INSTRUCTION)

    # ── Strictly Forbidden ─────────────────────────────────────
    parts.append(STRICTLY_FORBIDDEN)

    # ── Output Style ────────────────────────────────────────────
    parts.append(
        "OUTPUT STYLE:\n"
        "Premium lifestyle editorial jewellery photography.\n"
        "Aspirational.\n"
        "Sophisticated.\n"
        "Product-focused with premium environmental context.\n"
        "\n"
        "The jewellery is the hero of the composition.\n"
        "The premium contextual surface provides tasteful context, depth,\n"
        "and lifestyle narrative.\n"
        "\n"
        "IMAGE QUALITY:\n"
        "• Photorealistic lifestyle editorial photography.\n"
        "• Extremely sharp jewellery details.\n"
        "• Preserve fine stones, beads, metal edges, texture, hooks,\n"
        "  posts, and structural details.\n"
        "• Controlled depth of field — jewellery sharp, background\n"
        "  slightly softer.\n"
        "• High-resolution output.\n"
        "• Preferred e-commerce aspect ratio: 4:5.\n"
        "• Maintain sufficient resolution for close inspection and\n"
        "  product-detail verification."
    )

    # ── Quality Control Checklist ────────────────────────────────
    parts.append(QUALITY_CONTROL_CHECKLIST)

    return "\n\n".join(parts)
