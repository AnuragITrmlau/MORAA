"""Macro Shot Prompt — Prompt 7 — MORAA GemVision.

Single authoritative prompt foundation for generating realistic macro/detail
photographs of the exact jewellery product provided by the user.

The uploaded product image is the sole source of truth for the jewellery.
This prompt produces a professional macro photograph that highlights genuine
fine product details such as stone settings, cuts, prongs, metal texture,
surface finish, edges, joints, hooks, links, and construction details.

Architecture::

    REFERENCE IMAGE
          ↓
    MACRO SHOT FOUNDATION  ← this module
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
4. Produce a professional macro photograph
5. Highlight genuine fine detail visibility
6. Never alter the product identity for photographic quality
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
def build_macro_shot_prompt(
    earring_type: Optional[str] = None,
) -> str:
    """Build the single authoritative Prompt 7 Macro Shot prompt.

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
        The complete Prompt 7 Macro Shot prompt string.
    """
    parts: list[str] = []

    # ── Header ──────────────────────────────────────────────────
    parts.append(
        "TASK: Macro Shot.\n"
        "Create a realistic macro/detail photograph of the exact jewellery "
        "from the provided reference image.\n"
        "The image must show the same jewellery product photographed at "
        "macro/close range so that genuine fine product details are clearly "
        "visible — stone settings, stone cuts, prongs, metal texture, "
        "surface finish, edges, joints, hooks, links, engraving, and other "
        "construction details."
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
        "- surface finish (polished, brushed, matte, hammered)\n"
        "- construction details (joints, links, settings)\n"
        "- visible imperfections\n"
        "- asymmetry\n"
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
        "- make the design more symmetrical\n"
        "- repair imperfections\n"
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
        "You are creating a macro photograph of the EXACT uploaded product. "
        "You are NOT designing a new earring, creating an inspired variation, "
        "or improving a product.\n"
        "The generated image must show the EXACT same product — same shape, "
        "same stones, same metal, same proportions, same craftsmanship, "
        "same asymmetry, same imperfections.\n"
        "The camera perspective changes to macro scale. The jewellery must not."
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

    # ── Macro Photography Requirement ───────────────────────────
    parts.append(
        "MACRO PHOTOGRAPHY REQUIREMENT (NON-NEGOTIABLE):\n"
        "The output must look like a real professional macro product "
        "photograph.\n"
        "\n"
        "Visual treatment:\n"
        "• Close-range product photography.\n"
        "• High optical detail.\n"
        "• Controlled depth of field with realistic focus falloff.\n"
        "• Realistic material response to light.\n"
        "• Controlled studio lighting.\n"
        "• Natural photographic perspective.\n"
        "• Sharp rendering of the intended product detail.\n"
        "\n"
        "Do NOT:\n"
        "• Create an artificial CGI appearance.\n"
        "• Create an exaggerated fantasy macro effect.\n"
        "• Use excessive sharpening or artificial clarity that changes "
        "the physical appearance.\n"
        "• Digital zoom — this is macro photography, not a cropped zoom."
    )

    # ── Detail Visibility ───────────────────────────────────────
    parts.append(
        "DETAIL VISIBILITY (NON-NEGOTIABLE):\n"
        "The purpose is to show genuine fine product details clearly.\n"
        "\n"
        "Highlight what actually exists in the reference:\n"
        "• Stone setting style (prong, bezel, pave, channel, etc.)\n"
        "• Stone cuts and shapes (round, oval, marquise, pear, etc.)\n"
        "• Prong structure and condition\n"
        "• Metal texture and surface finish\n"
        "• Edges and joints\n"
        "• Hooks, links, clasps, and connectors\n"
        "• Engraving or surface markings\n"
        "• Other visible construction details\n"
        "\n"
        "If a detail is unclear in the reference, DO NOT invent it.\n"
        "If a detail is out of focus in the reference, DO NOT fabricate it.\n"
        "Only show details that genuinely exist in the source image."
    )

    # ── Framing ─────────────────────────────────────────────────
    parts.append(
        "FRAMING (NON-NEGOTIABLE):\n"
        "The jewellery/detail should occupy a significant portion of the "
        "image so that fine details are easy to inspect.\n"
        "\n"
        "Macro framing must remain physically believable:\n"
        "• Do not crop important structural information unnecessarily.\n"
        "• Do not cut through important stones or jewellery components "
        "without photographic reason.\n"
        "• Do not create extreme perspective distortion.\n"
        "• Do not stretch or deform the jewellery.\n"
        "• Do not make the product appear physically different because of "
        "the camera angle.\n"
        "\n"
        "The result must clearly remain identifiable as the same jewellery "
        "product from the uploaded reference.\n"
        "This must be a macro photograph, not an arbitrary digital zoom."
    )

    # ── Focus ───────────────────────────────────────────────────
    parts.append(
        "FOCUS (NON-NEGOTIABLE):\n"
        "Focus should be placed on the most informative visible product "
        "detail.\n"
        "The image should make genuine jewellery details easy to see while "
        "retaining enough surrounding context to establish the relationship "
        "to the original product.\n"
        "\n"
        "Do NOT:\n"
        "• Invent detail to fill areas that are out of focus.\n"
        "• Use artificial sharpening to manufacture details not present "
        "in the reference."
    )

    # ── Lighting ────────────────────────────────────────────────
    parts.append(
        "LIGHTING (NON-NEGOTIABLE):\n"
        "Use controlled professional product photography lighting.\n"
        "Lighting must reveal:\n"
        "• metal surface\n"
        "• stone setting\n"
        "• edges\n"
        "• texture\n"
        "• construction details\n"
        "\n"
        "Lighting must NOT:\n"
        "• change the apparent product colour\n"
        "• create fake gemstones\n"
        "• create excessive sparkle\n"
        "• hide important product details\n"
        "• introduce dramatic effects that alter product identity\n"
        "• produce unrealistic reflections that make the product appear "
        "different"
    )

    # ── Background ──────────────────────────────────────────────
    parts.append(
        "BACKGROUND (NON-NEGOTIABLE):\n"
        "Use a clean, unobtrusive photographic background.\n"
        "The background must remain secondary to the jewellery.\n"
        "\n"
        "Do NOT introduce:\n"
        "• distracting props\n"
        "• decorative objects\n"
        "• lifestyle scenes\n"
        "• people or hands\n"
        "• additional jewellery\n"
        "• unrelated objects\n"
        "\n"
        "The product is the sole visual focus."
    )

    # ── Anti-Beautification ─────────────────────────────────────
    parts.append(
        "ANTI-BEAUTIFICATION (NON-NEGOTIABLE):\n"
        "The purpose is detail visibility, NOT product beautification.\n"
        "\n"
        "Do NOT:\n"
        "• make stones unnaturally brilliant\n"
        "• make metal unnaturally glossy\n"
        "• smooth real surface characteristics\n"
        "• perfect manufacturing irregularities\n"
        "• improve symmetry\n"
        "• make the jewellery look more expensive than the reference\n"
        "• add luxury styling that changes the product\n"
        "\n"
        "Professional photographic quality is allowed.\n"
        "Product alteration is not."
    )

    # ── Anti-Reconstruction ─────────────────────────────────────
    parts.append(
        "ANTI-RECONSTRUCTION (NON-NEGOTIABLE):\n"
        "The model must not treat the reference as inspiration.\n"
        "It must treat it as the product identity reference.\n"
        "\n"
        "The output must represent the same physical jewellery product "
        "photographed at macro scale.\n"
        "NOT a new jewellery product inspired by the reference."
    )

    # ── Reference Priority ──────────────────────────────────────
    parts.append(
        "REFERENCE PRIORITY (NON-NEGOTIABLE):\n"
        "When visual quality conflicts with product accuracy:\n"
        "PRODUCT ACCURACY WINS.\n"
        "\n"
        "Priority order:\n"
        "1. Exact product identity\n"
        "2. Product geometry and construction\n"
        "3. Stone/material accuracy\n"
        "4. Detail visibility\n"
        "5. Photographic realism\n"
        "6. Lighting and composition\n"
        "\n"
        "Never sacrifice product fidelity to make the image aesthetically "
        "better."
    )

    # ── Strictly Forbidden ─────────────────────────────────────
    parts.append(
        "STRICTLY FORBIDDEN — DO NOT generate:\n"
        "• No redesigned jewellery\n"
        "• No altered jewellery proportions\n"
        "• No different stones\n"
        "• No changed metal color\n"
        "• No changed clasp/hook/post\n"
        "• No deformed geometry\n"
        "• No stretched or resized jewellery\n"
        "• No artificial detail invented for out-of-focus areas\n"
        "• No excessive sharpening that changes physical appearance\n"
        "• No CGI render aesthetic\n"
        "• No fantasy macro effect\n"
        "• No text, logo, or watermark"
    )

    # ── Image Quality ───────────────────────────────────────────
    parts.append(
        "OUTPUT STYLE:\n"
        "Professional macro product photography.\n"
        "High optical detail.\n"
        "Controlled studio lighting.\n"
        "Realistic depth of field.\n"
        "Product detail-focused.\n"
        "\n"
        "IMAGE QUALITY:\n"
        "• Professional macro photography aesthetic.\n"
        "• Extremely sharp jewellery details where in focus.\n"
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
        "4. Is the image a genuine macro photograph (not a digital zoom)?\n"
        "5. Are macro details visible and informative?\n"
        "6. Is the lighting controlled and professional?\n"
        "7. Is the background clean and unobtrusive?\n"
        "8. Is the jewellery the sole visual focus?\n"
        "9. Have no details been invented or fabricated?\n"
        "10. Does the product remain 100% identifiable as the original?\n"
        "\n"
        "If any answer is NO, correct the composition before generating the "
        "final image."
    )

    return "\n\n".join(parts)
