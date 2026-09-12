"""Earring E-Commerce Main Image Prompt Foundation — MORAA GemVision.

Single authoritative prompt foundation for generating e-commerce-ready
main images for Fashion Jewellery → Earrings.

This module is:
- **Provider-independent**: works with OpenAI, Gemini, or any future provider.
- **Marketplace-independent**: contains NO Amazon/Myntra/eBay-specific rules.
  Marketplace rules are appended by ImageGenerationManager separately.
- **Reusable**: consumed by the /api/earring-ecommerce/prompt endpoint.

Architecture::

    REFERENCE IMAGE
          ↓
    EARRING E-COMMERCE FOUNDATION  ← this module
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
3. Prevent anti-beautification / geometry normalisation
4. Support Hoop, Stud, Dangle earring types
5. Preserve material and colour fidelity
6. Remove photographic distractions (hand, card, backing, packaging)
7. Produce clean e-commerce-ready presentation
8. Coexist with existing marketplace layers (Amazon India)
"""

from typing import Optional


# ─── Earring Type Definitions ─────────────────────────────────────────
# Each type has specific preservation requirements that the image model
# must follow.  Adding a new earring type only requires adding a new
# entry to this dict.

EARRING_TYPE_PRESERVATION: dict[str, str] = {
    "Hoop": (
        "EARRING TYPE — HOOP: Preserve the EXACT hoop geometry including "
        "diameter, thickness, opening width, closure mechanism, curvature, "
        "and any decorative elements on the hoop surface. Do NOT change the "
        "hoop into a stud or dangle. Do NOT alter the curvature, thickness, "
        "or diameter. Preserve the closure/clasp mechanism exactly."
    ),
    "Stud": (
        "EARRING TYPE — STUD: Preserve the EXACT front shape, post/attachment "
        "structure, and backing when visible as part of the product. Preserve "
        "stone placement, proportions, decorative details, and geometry. "
        "Do NOT convert the stud into a hoop or dangle. Do NOT add hanging "
        "elements that are not in the reference."
    ),
    "Dangle": (
        "EARRING TYPE — DANGLE/DROP: Preserve the EXACT vertical structure "
        "including top attachment (hook/post/lever-back), connecting elements, "
        "hanging sections, relative lengths of each section, decorative "
        "elements, stones, and asymmetry. Do NOT convert into a hoop or stud. "
        "Do NOT shorten or lengthen any section. Do NOT remove hanging "
        "elements."
    ),
}

GENERIC_EARRING_PRESERVATION = (
    "EARRING TYPE: Preserve the exact earring type as shown in the reference. "
    "Do not convert one earring type into another (e.g. hoop to stud, stud "
    "to dangle, dangle to hoop). Preserve the complete structure including "
    "all attachment mechanisms, hanging elements, and connecting components."
)


# ─── Material / Colour Fidelity ───────────────────────────────────────
# The reference image is the visual source of truth for material appearance.
# The model must preserve what it sees, not what it thinks looks better.

MATERIAL_FIDELITY_INSTRUCTION = (
    "MATERIAL & COLOUR FIDELITY (NON-NEGOTIABLE):\n"
    "The reference image is the authoritative source for all material "
    "appearance. Preserve EXACTLY as shown:\n"
    "• Metal colour — do not convert silver to gold, gold to silver, "
    "brass to gold, or any other material substitution.\n"
    "• Metal finish — preserve polished, brushed, matte, hammered, or "
    "any other surface treatment exactly.\n"
    "• Plating appearance — preserve gold plating, silver plating, or "
    "any coating as shown.\n"
    "• Gemstone colour — preserve every stone's exact colour without "
    "oversaturation or artificial brightening.\n"
    "• Pearl appearance — preserve lustre, colour, and surface quality.\n"
    "• Bead appearance — preserve colour, size, and arrangement.\n"
    "• Reflectivity — preserve the natural reflectivity of the metal "
    "and stones.\n"
    "Do NOT oversaturate colours. Do NOT artificially brighten the "
    "jewellery. A white background must NOT be interpreted as white "
    "jewellery. The material in the reference is the truth."
)


# ─── Anti-Symmetry / Anti-Beautification ──────────────────────────────
# CRITICAL: Based on Phase 4D evidence where OpenAI outputs became
# significantly more symmetric than references (R1: ~54 → ~94-99,
# R2: ~64 → ~95-97).  This instruction is designed to prevent that.

ANTI_SYMMETRY_INSTRUCTION = (
    "CRITICAL — ANTI-SYMMETRY & ANTI-BEAUTIFICATION RULE (NON-NEGOTIABLE):\n"
    "The reference image's actual visible asymmetry IS part of the product "
    "identity. If the reference shows asymmetry, the output MUST preserve "
    "that asymmetry exactly.\n"
    "\n"
    "DO NOT:\n"
    "• Make both sides identical simply because symmetry looks more "
    "aesthetically pleasing.\n"
    "• Normalise geometry — do not straighten curves, regularise shapes, "
    "or correct perceived manufacturing imperfections.\n"
    "• Beautify the product — do not smooth surfaces, round edges, or "
    "improve proportions beyond what the reference shows.\n"
    "• Correct asymmetry — do not mirror one side to match the other.\n"
    "• Adjust proportions — do not elongate, compress, or resize any "
    "element for visual balance.\n"
    "• Invent details — do not add stones, engravings, filigree, or "
    "decorative elements not visible in the reference.\n"
    "• Remove genuine details — do not remove elements that appear "
    "irregular, imperfect, or asymmetric.\n"
    "• Convert an asymmetric product into a symmetric one.\n"
    "• Treat visible irregularity as an error to be corrected.\n"
    "\n"
    "The product in the reference is the ground truth. Any asymmetry, "
    "irregularity, or imperfection in the reference IS the product. "
    "Reproduce it faithfully."
)


# ─── Input Cleanup ────────────────────────────────────────────────────
# Remove photographic distractions while preserving jewellery components.

INPUT_CLEANUP_INSTRUCTION = (
    "INPUT CLEANUP (NON-NEGOTIABLE):\n"
    "The reference image may contain photographic distractions that must "
    "be removed from the e-commerce output. Remove:\n"
    "• Human hand, fingers, or body parts holding the earring.\n"
    "• Jewellery display card, backing card, or packaging.\n"
    "• Surface or table the earring is resting on.\n"
    "• Background distractions, unrelated objects, clutter.\n"
    "• Shadows cast on the background by the earring or hand.\n"
    "• Inconsistent lighting artefacts.\n"
    "\n"
    "CRITICAL: When removing a card, backing, or hand, NEVER remove a "
    "component that is actually part of the jewellery product. An earring "
    "hook, post, clasp, chain, connector, lever-back, or decorative "
    "component must NOT be mistaken for removable background material.\n"
    "When in doubt, PRESERVE the component — it may be part of the "
    "jewellery.\n"
    "\n"
    "ANTI-RECONSTRUCTION RULE:\n"
    "If a section of the product is hidden behind a hand, angle, or other "
    "object in the reference, do NOT reconstruct or invent that section. "
    "Preserve only what is visibly present in the reference. Omitted "
    "geometry is preferable to fabricated geometry. Do not hallucinate "
    "product details that are not visible in the source image."
)


# ─── Angle / View Preservation ────────────────────────────────────────
# Do not invent a new viewing angle. Preserve the reference's orientation.

ANGLE_PRESERVATION_INSTRUCTION = (
    "ANGLE & VIEW PRESERVATION:\n"
    "Preserve the meaningful visible orientation of the reference wherever "
    "possible. Do NOT rotate the product to make the composition prettier. "
    "Do NOT convert a front-facing product into an artificial perspective. "
    "Do NOT change the visible geometry by changing the viewing angle. "
    "If the source image is photographed at an angle, preserve the "
    "product's actual structure while cleaning the presentation. "
    "The earring's orientation in the reference is the correct orientation "
    "for the e-commerce output."
)


# ─── E-Commerce Presentation ──────────────────────────────────────────
# What the output should look like (presentation-only, not product-identity).

ECOMMERCE_PRESENTATION_INSTRUCTION = (
    "E-COMMERCE PRESENTATION (PRESENTATION ONLY — not product-identity):\n"
    "Generate a clean, professional e-commerce main image:\n"
    "• Clean commercial presentation with clear product visibility.\n"
    "• Product centred appropriately with sufficient margins.\n"
    "• Sharp product with accurate material rendering — do NOT enhance "
    "or alter the material appearance.\n"
    "• Neutral, balanced lighting — no harsh shadows on the product. "
    "Do NOT apply warm, cool, or coloured lighting that would change "
    "the perceived product material.\n"
    "• Reflections must be natural and consistent with the reference — "
    "do NOT add specular highlights that alter the metal appearance.\n"
    "• No distracting props, text, logos, watermarks, or overlays.\n"
    "• No packaging, no jewellery card, no display backing.\n"
    "• The product is the sole visual focus.\n"
    "• Clean e-commerce presentation suitable for an e-commerce "
    "product listing.\n"
    "• Background should be clean and non-distracting.\n"
    "• Accurate scale — the earring should appear at realistic size "
    "relative to its actual dimensions.\n"
    "• CRITICAL: The colour temperature of the output MUST match "
    "the reference. Silver metals must stay silver. Gold metals must "
    "stay gold. Do NOT warm or cool the product's natural colour."
)


# ─── Colour Lock (Experimental — Task 3 validated) ──────────────────
# Evidence: Variant D experiment showed 41% reduction in gold shift
# when this instruction is included.  Silver→gold colour shift is the
# highest-priority fidelity failure mode.

COLOUR_LOCK_INSTRUCTION = (
    "COLOUR LOCK (NON-NEGOTIABLE — HIGHEST PRIORITY):\n"
    "The reference image is the sole authority for the product's actual "
    "material and colour.\n"
    "Do NOT reinterpret, warm, cool, enhance, beautify, recolour, tint, "
    "tone-shift, or transform the product's metal or stone colours.\n"
    "Silver must remain silver.\n"
    "Gold must remain gold.\n"
    "Gold plating must remain gold plating.\n"
    "Silver plating must remain silver plating.\n"
    "Platinum must remain platinum.\n"
    "Brass must remain brass.\n"
    "925 silver must remain 925 silver.\n"
    "Blue stones must remain blue.\n"
    "Red stones must remain red.\n"
    "Green stones must remain green.\n"
    "Clear stones must remain clear.\n"
    "Do not infer a different material from studio lighting or reflections.\n"
    "Lighting may change illumination ONLY.\n"
    "Lighting must NEVER change the perceived underlying product material "
    "or colour.\n"
    "The colour temperature of the output MUST match the reference. "
    "If the reference shows cool/silver tones, the output must NOT warm "
    "them to gold. If the reference shows warm tones, the output must "
    "NOT cool them to silver."
)


# ─── Reference Image Priority Marker ──────────────────────────────────
# This marker tells ImageGenerationManager that REFERENCE_PRIORITY_BLOCK
# is already covered — preventing double-appendition.
# The marker MUST start with "REFERENCE IMAGE PRIORITY: MAXIMUM" to match
# the check in image_generation_manager.py:
#   if has_reference and "REFERENCE IMAGE PRIORITY" not in prompt.upper():

REFERENCE_PRIORITY_MARKER = "REFERENCE IMAGE PRIORITY: MAXIMUM"


# ─── Anti-Redesign Summary ────────────────────────────────────────────
# A concise anti-redesign instruction that reinforces the above rules.

ANTI_REDESIGN_INSTRUCTION = (
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


# ─── Complete Prompt Builder ───────────────────────────────────────────

def build_earring_ecommerce_prompt(
    earring_type: Optional[str] = None,
) -> str:
    """Build the single authoritative earring e-commerce main-image prompt.

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
        The complete earring e-commerce main-image prompt string.
    """
    parts: list[str] = []

    # ── 1:1 Visual Preservation Lock (NON-NEGOTIABLE — highest priority) ─
    parts.append(
        "CRITICAL: The earrings in the output MUST be an exact 1:1 physical "
        "replica of the earrings provided in the reference image. Retain "
        "exact stone count, stone shapes (e.g., baguette, marquise, pear, "
        "round), prong setting structure, metal tone, and earring "
        "silhouette. DO NOT alter the core jewelry design or invent "
        "alternate motifs."
    )

    # ── Input Extraction (remove packaging / distractions) ────────────
    parts.append(
        "Remove all retail packaging, polybags, display cards, plastic "
        "film, and human fingers. Extract the jewelry piece with pristine "
        "studio fidelity."
    )

    # ── Header ──────────────────────────────────────────────────
    parts.append(
        "TASK: Generate a single e-commerce main image for a Fashion "
        "Jewellery Earring product. The uploaded reference image is the "
        "authoritative source of truth for the actual product."
    )

    # ── Reference Priority (prevents backend double-appendition) ──
    parts.append(REFERENCE_PRIORITY_MARKER)

    # ── Anti-Redesign ───────────────────────────────────────────
    parts.append(ANTI_REDESIGN_INSTRUCTION)

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

    # ── Input Cleanup ───────────────────────────────────────────
    parts.append(INPUT_CLEANUP_INSTRUCTION)

    # ── Angle Preservation ──────────────────────────────────────
    parts.append(ANGLE_PRESERVATION_INSTRUCTION)

    # ── E-Commerce Presentation ─────────────────────────────────
    parts.append(ECOMMERCE_PRESENTATION_INSTRUCTION)

    # ── Output Rule ─────────────────────────────────────────────
    parts.append(
        "OUTPUT RULE:\n"
        "The earring must appear WITHOUT any jewellery card, display "
        "backing, packaging, human hand, or non-jewellery elements. "
        "The earring is the ONLY object in the image."
    )

    return "\n\n".join(parts)
