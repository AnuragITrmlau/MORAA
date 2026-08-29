"""Professional Shot Prompt — Prompt 4 — MORAA GemVision.

Single authoritative prompt foundation for generating professional
editorial/studio jewellery images for Fashion Jewellery → Earrings.

The uploaded product image is the sole source of truth for the jewellery.
This prompt produces a premium professional studio photograph with a
realistic grey linen + light marble environment and editorial lighting.

Architecture::

    REFERENCE IMAGE (Prompt 1 output preferred, raw upload fallback)
          ↓
    PROFESSIONAL SHOT FOUNDATION  ← this module
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
4. Produce a professional editorial studio image on grey linen + marble
5. Enforce no-human-model / no-props / no-decorative-elements rules
6. Support Hoop, Stud, Dangle earring types
7. Coexist with existing marketplace layers (Amazon India)
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


# ─── Complete Prompt Builder ───────────────────────────────────────────
def build_professional_shot_prompt(
    earring_type: Optional[str] = None,
) -> str:
    """Build the single authoritative Prompt 4 Professional Shot prompt.

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
        The complete Prompt 4 Professional Shot prompt string.
    """
    parts: list[str] = []

    # ── Header ──────────────────────────────────────────────────
    parts.append(
        "TASK: Professional / Editorial Luxury Jewelry Studio Photography.\n"
        "Use the uploaded jewellery as the exact product source of truth.\n"
        "Create a premium realistic luxury studio environment for the "
        "jewellery from the provided reference image.\n"
        "The jewellery is the primary visual subject, professionally "
        "photographed in a premium studio setting."
    )

    # ── Reference Priority (prevents backend double-appendition) ──
    parts.append(REFERENCE_PRIORITY_MARKER)

    # ── Product Fidelity — Absolute Priority ────────────────────
    parts.append(
        "PRODUCT FIDELITY — ABSOLUTE PRIORITY:\n"
        "The uploaded reference image is the single source of truth for "
        "the jewellery.\n"
        "Preserve the original product exactly.\n"
        "\n"
        "Preserve:\n"
        "- exact product geometry\n"
        "- exact silhouette\n"
        "- gemstone count\n"
        "- gemstone placement\n"
        "- gemstone cuts and facet structure\n"
        "- prong settings\n"
        "- micro-pave details\n"
        "- bead arrangement\n"
        "- hanging components\n"
        "- hooks and connectors\n"
        "- metal structure\n"
        "- silver/white-gold appearance\n"
        "- original proportions\n"
        "- distinctive product details\n"
        "\n"
        "Do NOT:\n"
        "- redesign the jewellery\n"
        "- reconstruct into a similar product\n"
        "- add stones\n"
        "- remove stones\n"
        "- duplicate stones\n"
        "- merge components\n"
        "- change metal color\n"
        "- change geometry\n"
        "- beautify into a different design\n"
        "- invent missing details\n"
        "- simplify detailed components\n"
        "\n"
        "Every visible stone, bead, prong, connector, clasp, hook, link, and "
        "structural element must correspond to the reference image.\n"
        "If any detail is unclear in the reference, DO NOT invent a "
        "replacement detail."
    )

    # ── Anti-Redesign ───────────────────────────────────────────
    parts.append(
        "ANTI-REDESIGN RULE (NON-NEGOTIABLE):\n"
        "This is a PRODUCT PHOTOGRAPHY task, NOT a design task.\n"
        "You are photographing the EXACT uploaded product in a professional "
        "studio setting. You are NOT designing a new earring, creating an "
        "inspired variation, or improving a product.\n"
        "The generated image must show the EXACT same product — same shape, "
        "same stones, same metal, same proportions, same craftsmanship, "
        "same asymmetry, same imperfections.\n"
        "Only the presentation changes: background, lighting, composition, "
        "and commercial quality."
    )

    # ── Anti-Symmetry (CRITICAL — Phase 4D failure mode) ────────
    parts.append(ANTI_SYMMETRY_INSTRUCTION)

    # ── Product Identity Preservation ───────────────────────────
    parts.append(
        "PRODUCT IDENTITY — PRESERVE EXACTLY:\n"
        "• Overall silhouette and outline shape.\n"
        "• Geometry: the exact form (circular, teardrop, geometric, "
        "organic, or any other visible shape).\n"
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
        "hammering, or any other surface treatment as shown."
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

    # ── Size & Proportion ──────────────────────────────────────
    parts.append(
        "SIZE & PROPORTION (NON-NEGOTIABLE):\n"
        "Maintain the jewellery's original proportions from the reference.\n"
        "Do not make the jewellery unnaturally large, small, elongated, "
        "compressed, widened, thickened, or otherwise distorted.\n"
        "The output should look like the SAME physical jewellery "
        "photographed professionally in a luxury studio.\n"
        "\n"
        "Preserve relative dimensions between every component.\n"
        "Do not exaggerate or minimize any element for visual impact.\n"
        "PRODUCT FIDELITY HAS PRIORITY OVER VISUAL STYLING."
    )

    # ── Negative Space ──────────────────────────────────────────
    parts.append(
        "NEGATIVE SPACE — HARD REQUIREMENT (NON-NEGOTIABLE):\n"
        "The reference jewellery contains intentional OPEN / EMPTY areas. "
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
        "The empty space IS part of the jewellery geometry. Filling it "
        "changes the product identity."
    )

    # ── Bead / Pearl Cluster Preservation ───────────────────────
    parts.append(
        "BEAD AND PEARL CLUSTER PRESERVATION (NON-NEGOTIABLE):\n"
        "If the reference jewellery contains bead clusters, pearl groups, "
        "or dangling bead arrangements:\n"
        "\n"
        "• Each individual bead/pearl must remain visually "
        "distinguishable — no merging, fusing, or melting.\n"
        "• Bead clusters must retain their individual separation — gaps "
        "between beads are part of the design.\n"
        "• Large faceted teardrop drops must remain individually "
        "identifiable — each drop is a separate component.\n"
        "• Hanging bead arrangements must preserve the exact count and "
        "relative positioning.\n"
        "• Bead sizes must match the reference — do not enlarge small "
        "beads or shrink large ones.\n"
        "\n"
        "DO NOT allow:\n"
        "• Fused beads that merge into a single mass\n"
        "• Melted or blob-like bead clusters\n"
        "• Missing drops that were present in the reference\n"
        "• Invented drops that were not in the reference\n"
        "• Random bead blobs replacing structured clusters"
    )

    # ── Studio Environment (non-negotiable) ────────────────────
    parts.append(
        "STUDIO ENVIRONMENT (NON-NEGOTIABLE):\n"
        "Create a premium realistic luxury studio environment.\n"
        "\n"
        "Replace the surrounding background with soft textured grey linen "
        "fabric layered naturally over a polished light marble surface.\n"
        "\n"
        "The jewellery should be naturally laid flat at an approximately "
        "45-degree editorial angle where the source geometry permits.\n"
        "\n"
        "Create realistic physical contact between the jewellery and the "
        "surface.\n"
        "\n"
        "Maintain realistic contact shadows beneath the jewellery.\n"
        "\n"
        "The jewellery must remain the sharpest and primary visual subject.\n"
        "\n"
        "Do NOT generate:\n"
        "• Pure flat white background\n"
        "• White isolated catalog background\n"
        "• White-only e-commerce presentation\n"
        "• Plain empty canvas\n"
        "• No background at all"
    )

    # ── Lighting ────────────────────────────────────────────────
    parts.append(
        "LIGHTING (NON-NEGOTIABLE):\n"
        "Use diffused softbox studio lighting.\n"
        "\n"
        "• Highlight the natural facet reflections of the gemstones.\n"
        "• Show realistic metallic sheen of the prongs and metal.\n"
        "• Use gentle background falloff and realistic depth.\n"
        "• Maintain realistic contact shadows beneath the jewellery.\n"
        "• Controlled gemstone reflections.\n"
        "• Realistic metallic highlights.\n"
        "• Visible stone facets.\n"
        "• Realistic prong reflections.\n"
        "\n"
        "Lighting must reveal the product. Lighting must NOT beautify, "
        "recolour, redesign, or alter the jewellery.\n"
        "No dramatic shadows.\n"
        "No colored lighting.\n"
        "No cinematic color grading.\n"
        "No excessive highlights that hide product details."
    )

    # ── Strictly Forbidden ─────────────────────────────────────
    parts.append(
        "STRICTLY FORBIDDEN — DO NOT generate:\n"
        "• No human model\n"
        "• No face\n"
        "• No hand\n"
        "• No fingers\n"
        "• No body parts\n"
        "• No clothing\n"
        "• No jewellery stand\n"
        "• No box\n"
        "• No flowers\n"
        "• No decorative props\n"
        "• No text\n"
        "• No logo\n"
        "• No watermark\n"
        "• No additional objects\n"
        "• No pure white background\n"
        "• No white isolated catalog shot\n"
        "• No plain empty canvas\n"
        "• No redesigned jewellery\n"
        "• No altered jewellery proportions\n"
        "• No different stones\n"
        "• No missing beads\n"
        "• No extra beads\n"
        "• No changed metal color\n"
        "• No changed clasp\n"
        "• No changed hook\n"
        "• No changed pin/post\n"
        "• No deformed geometry\n"
        "• No stretched jewellery\n"
        "• No resized jewellery\n"
        "• No floating jewellery"
    )

    # ── Image Quality ───────────────────────────────────────────
    parts.append(
        "OUTPUT STYLE:\n"
        "Premium professional editorial jewellery photography.\n"
        "Luxury studio aesthetic.\n"
        "Accurate.\n"
        "Product-focused.\n"
        "Editorial quality.\n"
        "\n"
        "The product itself is more important than visual styling.\n"
        "\n"
        "IMAGE QUALITY:\n"
        "• Photorealistic professional studio photography.\n"
        "• Extremely sharp jewellery details.\n"
        "• Preserve fine stones, beads, metal edges, texture, hooks, "
        "posts, and structural details.\n"
        "• High-resolution output.\n"
        "• Preferred aspect ratio: 4:5."
    )

    # ── Final Verification Checklist ────────────────────────────
    parts.append(
        "FINAL VERIFICATION — Before producing the final image, internally "
        "verify:\n"
        "\n"
        "1. Is the jewellery the EXACT same product as the reference?\n"
        "2. Are all stones, beads, metal components, hooks, posts, clasps, "
        "and structural details preserved?\n"
        "3. Has the jewellery's original size/proportion remained unchanged?\n"
        "4. Is there absolutely NO human model, face, hand, or body part?\n"
        "5. Is there absolutely NO prop, box, flower, stand, or decorative "
        "element?\n"
        "6. Is the background a realistic grey linen + light marble "
        "environment?\n"
        "7. Is there NO pure white background or isolated white canvas?\n"
        "8. Is the jewellery naturally laid flat on the surface?\n"
        "9. Are there realistic contact shadows beneath the jewellery?\n"
        "10. Is the product the sharpest and primary visual subject?\n"
        "11. Does the image look like a premium professional studio "
        "photograph?\n"
        "\n"
        "If any answer is NO, correct the composition before generating the "
        "final image."
    )

    return "\n\n".join(parts)
