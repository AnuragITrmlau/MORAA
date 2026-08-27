"""Earring Scale Reference Shot Prompt — Prompt 3 — MORAA GemVision.

Single authoritative prompt foundation for generating e-commerce-ready
scale-reference images for Fashion Jewellery → Earrings.

The uploaded product image is the sole source of truth for the jewellery.
This prompt communicates the approximate physical scale of the exact
uploaded product by showing it naturally resting on a single open human
hand.

Architecture::

    REFERENCE IMAGE (Prompt 1 output preferred, raw upload fallback)
          ↓
    SCALE REFERENCE FOUNDATION  ← this module
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
2. Communicate approximate physical scale via ONE feminine human hand
3. Prevent anti-symmetry normalisation (Phase 4D failure mode)
4. Prevent colour/material shift (Task 3 validated)
5. Preserve negative space and bead cluster structure
6. Support Hoop, Stud, Dangle earring types with type-specific placement
7. Enforce no-piercing / no-skin-penetration rules
8. Produce clean e-commerce-ready presentation on pure white background
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
    ECOMMERCE_PRESENTATION_INSTRUCTION,
)


# ─── Product Fidelity — Absolute Priority ──────────────────────────────

PRODUCT_FIDELITY_ABSOLUTE = (
    "PRODUCT FIDELITY — ABSOLUTE PRIORITY:\n"
    "Reproduce the exact original earring from the reference image.\n"
    "Preserve 100% of the original design, silhouette, dimensions, "
    "proportions, metal color, finish, stones, gemstones, beads, motifs, "
    "links, hooks, pins, backs, clasps, and every visible structural detail.\n"
    "\n"
    "ZERO redesign.\n"
    "ZERO beautification that changes the product.\n"
    "ZERO addition, removal, substitution, duplication, simplification, or "
    "reinterpretation of any product component.\n"
    "\n"
    "Do not make the earring larger, smaller, thicker, thinner, longer, "
    "shorter, wider, narrower, heavier, or more delicate than the reference.\n"
    "The hand is ONLY a physical scale reference. The jewellery itself must "
    "remain geometrically and proportionally constant."
)


# ─── Hand Requirements ─────────────────────────────────────────────────

HAND_REQUIREMENTS_INSTRUCTION = (
    "HAND REQUIREMENT (NON-NEGOTIABLE):\n"
    "Show exactly ONE natural human hand.\n"
    "\n"
    "• Use a clean, soft, feminine adult hand with a delicate appearance "
    "suitable for premium women's jewellery.\n"
    "• Hand should appear well-groomed and naturally manicured, with "
    "clean nails.\n"
    "• Skin should look realistic, healthy, and natural.\n"
    "• Avoid rough, heavily textured, masculine-looking, muscular, or "
    "excessively veined hands.\n"
    "• No jewellery, rings, bracelets, watches, tattoos, or other "
    "accessories on the hand.\n"
    "• No second hand anywhere in the frame.\n"
    "• No wrist styling or unnecessary body parts.\n"
    "\n"
    "The hand is ONLY a physical scale reference.\n"
    "THE EARRING IS THE HERO SUBJECT."
)


# ─── Earring Placement Rules (type-specific) ───────────────────────────

EARRING_PLACEMENT_RULES = (
    "EARRING PLACEMENT RULES (NON-NEGOTIABLE):\n"
    "Determine placement from the actual earring construction visible in "
    "the reference image.\n"
    "\n"
    "IF DANGLE / DROP EARRING:\n"
    "• Place the earring completely flat and naturally resting on the "
    "open palm.\n"
    "• The entire earring must rest ON TOP of the skin.\n"
    "• Do NOT pierce, insert, push, embed, or penetrate any part of the "
    "earring into the skin.\n"
    "• Metal pins, hooks, posts, wires, or findings must remain visibly "
    "above the skin and must NEVER appear to enter or puncture the palm.\n"
    "• Do not bend or reshape the earring to fit the hand.\n"
    "\n"
    "IF STUD EARRING:\n"
    "• Place the stud naturally near the fingertips / finger area.\n"
    "• It must be resting on top of the hand, not inserted into the skin.\n"
    "• The post/pin must remain completely outside the skin.\n"
    "• NEVER depict the stud as pierced or being worn.\n"
    "\n"
    "IF HOOP / LOOP EARRING:\n"
    "• Hold the hoop naturally and gently between the fingers of the "
    "SAME hand.\n"
    "• The fingers may lightly support the earring only.\n"
    "• Do not squeeze, deform, stretch, or reshape the hoop.\n"
    "• Preserve the exact original circular/curved geometry and dimensions.\n"
    "\n"
    "GENERAL PLACEMENT RULE:\n"
    "The earring is a physical object being displayed for size comparison, "
    "NOT being worn.\n"
    "No piercing.\n"
    "No skin penetration.\n"
    "No pin entering skin.\n"
    "No clasp inserted into skin.\n"
    "No fingers passing through the earring unless the reference "
    "construction requires natural holding of a hoop/loop."
)


# ─── Size & Scale Accuracy ─────────────────────────────────────────────

SIZE_SCALE_ACCURACY_INSTRUCTION = (
    "SIZE & SCALE ACCURACY (NON-NEGOTIABLE):\n"
    "• Maintain the exact physical proportion of the original earring.\n"
    "• Do not use AI-generated assumptions to alter its size.\n"
    "• The hand provides visual scale only; it must NOT cause the jewellery "
    "to be resized or redesigned.\n"
    "• Preserve the relative dimensions between every component of the "
    "earring.\n"
    "• Do not exaggerate the jewellery for visual impact.\n"
    "• Do not minimize it to make it appear delicate.\n"
    "• The generated image must communicate the product's true apparent "
    "physical scale as faithfully as possible.\n"
    "\n"
    "PRODUCT FIDELITY HAS PRIORITY OVER SCALE PRESENTATION."
)


# ─── Occlusion & Anti-Reconstruction ───────────────────────────────────

OCCLUSION_ANTI_RECONSTRUCTION_INSTRUCTION = (
    "OCCLUSION & ANTI-RECONSTRUCTION (NON-NEGOTIABLE):\n"
    "The hand must not intentionally hide important earring details.\n"
    "\n"
    "If any part of the earring becomes naturally obscured by the hand:\n"
    "DO NOT reconstruct, invent, or assume the hidden geometry.\n"
    "Do not use symmetry to guess the hidden side.\n"
    "Do not invent hidden stones, beads, connectors, hooks, or decorative "
    "elements.\n"
    "Preserve only the product structure supported by the uploaded reference.\n"
    "\n"
    "VISIBLE REFERENCE DATA ALWAYS HAS PRIORITY OVER AI ASSUMPTION."
)


# ─── Dimension Integrity ───────────────────────────────────────────────

DIMENSION_INTEGRITY_INSTRUCTION = (
    "DIMENSION INTEGRITY:\n"
    "Use the hand only as a visual scale reference.\n"
    "If verified product dimensions are separately provided, those verified "
    "dimensions are authoritative.\n"
    "\n"
    "If verified dimensions are NOT provided:\n"
    "• Do not invent millimetre measurements.\n"
    "• Do not invent centimetre measurements.\n"
    "• Do not add dimension labels.\n"
    "• Do not create measurement callouts.\n"
    "• Do not display fake numerical values.\n"
    "• Do not claim an exact measurement from visual estimation.\n"
    "\n"
    "The image communicates relative physical scale only.\n"
    "Do not alter the jewellery to satisfy an assumed measurement."
)


# ─── Negative Space ────────────────────────────────────────────────────

NEGATIVE_SPACE_INSTRUCTION = (
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


# ─── Bead / Pearl Cluster Preservation ─────────────────────────────────

BEAD_CLUSTER_PRESERVATION_INSTRUCTION = (
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


# ─── Negative / Failure Prevention ─────────────────────────────────────

NEGATIVE_FAILURE_PREVENTION = (
    "NEGATIVE / FAILURE PREVENTION — DO NOT generate:\n"
    "• redesigned jewellery\n"
    "• altered jewellery proportions\n"
    "• different stones\n"
    "• missing beads\n"
    "• extra beads\n"
    "• changed metal color\n"
    "• changed clasp\n"
    "• changed hook\n"
    "• changed pin/post\n"
    "• duplicate earrings\n"
    "• extra jewellery\n"
    "• two hands\n"
    "• male/rough hand\n"
    "• rough skin\n"
    "• excessive veins\n"
    "• rings or bracelets\n"
    "• piercing\n"
    "• earring post entering skin\n"
    "• pin penetrating palm\n"
    "• earring embedded in skin\n"
    "• deformed hoop\n"
    "• stretched jewellery\n"
    "• resized jewellery\n"
    "• floating jewellery\n"
    "• unrealistic hand anatomy\n"
    "• off-white background\n"
    "• grey background\n"
    "• cream background\n"
    "• decorative props\n"
    "• text\n"
    "• labels\n"
    "• measurements\n"
    "• watermarks\n"
    "• logos"
)


# ─── Final Verification Checklist ──────────────────────────────────────

FINAL_VERIFICATION_CHECKLIST = (
    "FINAL VERIFICATION — Before producing the final image, internally "
    "verify:\n"
    "\n"
    "1. Is there exactly ONE hand?\n"
    "2. Does the hand look clean, soft, feminine, and manicured?\n"
    "3. Is the earring the EXACT same product as the reference?\n"
    "4. Are all stones, beads, metal components, hooks, posts, and "
    "structural details preserved?\n"
    "5. Has the earring's original size/proportion remained unchanged?\n"
    "6. If resting on the palm, is EVERY part of the earring above the "
    "skin?\n"
    "7. Is NO pin/post/hook penetrating or appearing to pierce the skin?\n"
    "8. Is the background truly #FFFFFF rather than near-white?\n"
    "9. Are there absolutely NO additional props?\n"
    "10. Does the image clearly communicate the jewellery's real physical "
    "scale?\n"
    "\n"
    "If any answer is NO, correct the composition before generating the "
    "final image."
)


# ─── Complete Prompt Builder ───────────────────────────────────────────

def build_scale_reference_prompt(
    earring_type: Optional[str] = None,
) -> str:
    """Build the single authoritative earring scale-reference prompt.

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
        The complete earring scale-reference prompt string.
    """
    parts: list[str] = []

    # ── Header ──────────────────────────────────────────────────
    parts.append(
        "Create a clean, premium e-commerce scale-reference photograph "
        "using the uploaded original earring image as the ONLY product "
        "reference.\n"
        "\n"
        "PRIMARY OBJECTIVE:\n"
        "Show the true physical size, proportion, silhouette, and visual "
        "scale of the EXACT SAME EARRING by placing it naturally on a "
        "single open human hand."
    )

    # ── Reference Priority (prevents backend double-appendition) ──
    parts.append(REFERENCE_PRIORITY_MARKER)

    # ── Product Fidelity — Absolute Priority ────────────────────
    parts.append(PRODUCT_FIDELITY_ABSOLUTE)

    # ── Anti-Redesign ───────────────────────────────────────────
    parts.append(
        "ANTI-REDESIGN RULE (NON-NEGOTIABLE):\n"
        "This is a PRODUCT PHOTOGRAPHY task, NOT a design task.\n"
        "You are photographing the EXACT uploaded product in a scale-reference "
        "composition. You are NOT designing a new earring, creating an "
        "inspired variation, or improving a product.\n"
        "The generated image must show the EXACT same product — same shape, "
        "same stones, same metal, same proportions, same craftsmanship, "
        "same asymmetry, same imperfections.\n"
        "Only the presentation changes: background, lighting, composition, "
        "scale reference (hand), and commercial quality."
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

    # ── Hand Requirements ──────────────────────────────────────
    parts.append(HAND_REQUIREMENTS_INSTRUCTION)

    # ── Earring Placement Rules (type-specific) ─────────────────
    parts.append(EARRING_PLACEMENT_RULES)

    # ── Size & Scale Accuracy ──────────────────────────────────
    parts.append(SIZE_SCALE_ACCURACY_INSTRUCTION)

    # ── Negative Space ──────────────────────────────────────────
    parts.append(NEGATIVE_SPACE_INSTRUCTION)

    # ── Bead / Pearl Cluster Preservation ───────────────────────
    parts.append(BEAD_CLUSTER_PRESERVATION_INSTRUCTION)

    # ── Occlusion / Anti-Reconstruction ─────────────────────────
    parts.append(OCCLUSION_ANTI_RECONSTRUCTION_INSTRUCTION)

    # ── Dimension Integrity ─────────────────────────────────────
    parts.append(DIMENSION_INTEGRITY_INSTRUCTION)

    # ── Background ──────────────────────────────────────────────
    parts.append(
        "BACKGROUND (NON-NEGOTIABLE):\n"
        "Background must be ABSOLUTELY PURE WHITE:\n"
        "RGB: 255, 255, 255\n"
        "HEX: #FFFFFF\n"
        "\n"
        "No off-white.\n"
        "No cream.\n"
        "No ivory.\n"
        "No grey.\n"
        "No warm-white.\n"
        "No gradient.\n"
        "No visible studio wall.\n"
        "No textured surface.\n"
        "No background props.\n"
        "White should remain #FFFFFF throughout the visible background."
    )

    # ── Lighting ────────────────────────────────────────────────
    parts.append(
        "LIGHTING:\n"
        "Clean neutral e-commerce studio lighting.\n"
        "• Soft, even illumination.\n"
        "• Accurate product color reproduction.\n"
        "• Controlled natural-looking contact shadow beneath the "
        "jewellery/hand where physically appropriate.\n"
        "• No dramatic shadows.\n"
        "• No colored lighting.\n"
        "• No cinematic color grading.\n"
        "• No excessive highlights that hide product details.\n"
        "\n"
        "Lighting must reveal the product. Lighting must NOT beautify, "
        "recolour, redesign, or alter the jewellery.\n"
        "The hand and earring should appear naturally illuminated by the "
        "same scene lighting."
    )

    # ── Composition ─────────────────────────────────────────────
    parts.append(
        "COMPOSITION:\n"
        "• Single hand + exact original earring ONLY.\n"
        "• Jewellery remains the visual focal point.\n"
        "• Hand provides contextual scale without dominating the "
        "composition.\n"
        "• Clean centered/controlled e-commerce framing.\n"
        "• No additional objects or decorative props.\n"
        "• No ruler, measuring tape, coins, cards, flowers, fabric, "
        "boxes, or accessories.\n"
        "\n"
        "Do not change the earring's meaningful viewing orientation merely "
        "to improve composition."
    )

    # ── Image Quality ───────────────────────────────────────────
    parts.append(
        "IMAGE QUALITY:\n"
        "• Photorealistic commercial e-commerce photography.\n"
        "• Extremely sharp jewellery details.\n"
        "• Preserve fine stones, beads, metal edges, texture, hooks, "
        "posts, and structural details.\n"
        "• High-resolution output.\n"
        "• Preferred e-commerce aspect ratio: 4:5.\n"
        "• Square 1:1 may be used only where the downstream marketplace "
        "requires it.\n"
        "• Maintain sufficient resolution for close inspection and "
        "product-detail verification.\n"
        "\n"
        "IMPORTANT: Do not assume that requesting \"4K\" or \"8K\" in a prompt "
        "guarantees that resolution. The implementation must preserve the "
        "provider's actual supported output resolution.\n"
        "Do not add fake resolution metadata.\n"
        "Do not upscale solely to claim 4K/8K unless the existing pipeline "
        "already supports a legitimate image upscaling stage."
    )

    # ── Negative / Failure Prevention ───────────────────────────
    parts.append(NEGATIVE_FAILURE_PREVENTION)

    # ── Final Verification Checklist ────────────────────────────
    parts.append(FINAL_VERIFICATION_CHECKLIST)

    return "\n\n".join(parts)
