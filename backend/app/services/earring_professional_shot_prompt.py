"""Professional Commercial Photography — Dynamic Environment Engine
— Prompt 4 — MORAA GemVision.

Single authoritative prompt foundation for generating professional
commercial earring photography with selectable environment archetypes.

The uploaded product image is the sole source of truth for the jewellery.
This prompt produces high-end professional commercial jewellery photography
in a dynamic studio/tabletop environment.

Architecture::

    REFERENCE IMAGE
          ↓
    DYNAMIC ENVIRONMENT ENGINE  ← this module
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
4. Produce professional commercial jewellery photography
5. Support dynamic environment archetypes (Minimalist, Organic, Luxury)
6. Environment-aware lighting and shadow instructions
7. Realistic contact shadows and grounding
8. Coexist with existing marketplace layers (Amazon India)
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


# ─── Environment Definitions ──────────────────────────────────────────
# Each environment defines a complete backdrop, lighting, and visual
# direction for the professional commercial earring photograph.
# The selected environment determines the environment and lighting instructions.

VALID_ENVIRONMENTS: list[str] = [
    "minimalist",
    "organic",
    "luxury",
]

ENVIRONMENT_LABELS: dict[str, str] = {
    "minimalist": "Minimalist Studio",
    "organic": "Organic Still Life",
    "luxury": "Luxury Drapery",
}


# ─── Environment Instructions per Archetype ────────────────────────────

def _environment_minimalist() -> str:
    """Minimalist Studio — clean, premium, product-focused."""
    return (
        "ENVIRONMENT & BACKDROP (NON-NEGOTIABLE):\n"
        "Minimalist studio mount/stand environment.\n"
        "Clean professional tabletop/studio environment.\n"
        "Controlled neutral presentation.\n"
        "Subtle grounding/contact shadow.\n"
        "\n"
        "The jewellery rests naturally on a clean, premium, minimal surface. "
        "The environment must be visually neutral and unobtrusive — the "
        "jewellery is the sole focal point.\n"
        "\n"
        "Do NOT generate:\n"
        "• textured organic surfaces\n"
        "• fabric or silk backgrounds\n"
        "• busy or cluttered environments\n"
        "• coloured or tinted backdrops\n"
        "• plain pure white isolated catalog backgrounds"
    )


def _environment_organic() -> str:
    """Organic Still Life — natural material textures, controlled composition."""
    return (
        "ENVIRONMENT & BACKDROP (NON-NEGOTIABLE):\n"
        "Raw organic still life environment.\n"
        "Use one or more of: raw slate, warm travertine, raw concrete, "
        "or a similarly appropriate natural neutral texture.\n"
        "\n"
        "Visual direction: premium organic still life with natural material "
        "texture and controlled composition. The jewellery remains the "
        "dominant subject.\n"
        "\n"
        "The natural material texture should be visible but subordinate "
        "to the jewellery. Do not let the background compete with the "
        "product.\n"
        "\n"
        "Do NOT generate:\n"
        "• silk or fabric surfaces\n"
        "• minimalist studio stands\n"
        "• polished reflective surfaces\n"
        "• busy or colourful organic textures\n"
        "• pure white isolated catalog backgrounds"
    )


def _environment_luxury() -> str:
    """Luxury Drapery — elegant folded fabric, controlled sheen."""
    return (
        "ENVIRONMENT & BACKDROP (NON-NEGOTIABLE):\n"
        "Luxury drapery and silk environment.\n"
        "Use one or more of: champagne silk, ivory silk, or an appropriate "
        "neutral satin/silk fabric.\n"
        "\n"
        "Visual direction: luxury commercial jewellery photography with "
        "elegant folded fabric and controlled fabric sheen. The jewellery "
        "remains the dominant subject.\n"
        "\n"
        "The fabric should have realistic folds, controlled sheen, and "
        "natural draping. Do not let the fabric compete with the jewellery.\n"
        "\n"
        "Do NOT generate:\n"
        "• raw organic textures (slate, concrete)\n"
        "• minimalist studio stands\n"
        "• busy or cluttered surfaces\n"
        "• brightly coloured fabrics\n"
        "• pure white isolated catalog backgrounds"
    )


ENVIRONMENT_INSTRUCTIONS: dict[str, object] = {
    "minimalist": _environment_minimalist,
    "organic": _environment_organic,
    "luxury": _environment_luxury,
}


# ─── Lighting Instructions per Archetype ───────────────────────────────

def _lighting_minimalist() -> str:
    """Lighting for Minimalist Studio."""
    return (
        "LIGHTING & SHADING (NON-NEGOTIABLE):\n"
        "Soft controlled studio lighting appropriate to a minimalist "
        "studio environment.\n"
        "\n"
        "• Balanced highlights across the jewellery.\n"
        "• Clean metal-edge definition.\n"
        "• Realistic contact shadow where jewellery meets the surface.\n"
        "• Controlled gemstone brilliance — visible facet detail without "
        "blown highlights.\n"
        "• Subtle environmental reflections on polished metal surfaces "
        "consistent with a clean studio setting.\n"
        "\n"
        "Avoid:\n"
        "• directional dramatic lighting\n"
        "• high-contrast shadows\n"
        "• warm/cool colour tinting\n"
        "• excessive sparkle or artificial brilliance\n"
        "• flat lighting that hides product detail\n"
        "• unrealistic CGI reflections\n"
        "\n"
        "Lighting must reveal the product without changing its appearance."
    )


def _lighting_organic() -> str:
    """Lighting for Organic Still Life."""
    return (
        "LIGHTING & SHADING (NON-NEGOTIABLE):\n"
        "Directional light appropriate to a raw organic still life.\n"
        "\n"
        "• Directional key light creating controlled contrast.\n"
        "• Realistic shadows consistent with natural material surfaces.\n"
        "• Gemstone detail and material response preserved under "
        "directional illumination.\n"
        "• Controlled reflections on polished metal surfaces consistent "
        "with the organic environment.\n"
        "• Realistic contact shadow where jewellery rests on the surface.\n"
        "\n"
        "Avoid:\n"
        "• flat or omnidirectional lighting\n"
        "• excessive specular highlights\n"
        "• warm/cool colour tinting that changes product colour\n"
        "• artificial sparkle or CGI plastic appearance\n"
        "• lighting that obscures the product\n"
        "\n"
        "Lighting must reveal the product without changing its appearance."
    )


def _lighting_luxury() -> str:
    """Lighting for Luxury Drapery."""
    return (
        "LIGHTING & SHADING (NON-NEGOTIABLE):\n"
        "Soft grazing directional light appropriate to luxury silk/satin "
        "drapery.\n"
        "\n"
        "• Soft grazing directional light revealing fabric texture and "
        "controlled sheen.\n"
        "• Controlled reflections on polished metal surfaces consistent "
        "with the silk environment.\n"
        "• Readable metal and gemstone detail under soft directional "
        "illumination.\n"
        "• Realistic fabric sheen without overpowering the jewellery.\n"
        "• Realistic contact shadow where jewellery rests on or near "
        "the fabric.\n"
        "\n"
        "Avoid:\n"
        "• harsh directional lighting\n"
        "• excessive fabric sheen that competes with jewellery\n"
        "• warm/cool colour tinting that changes product colour\n"
        "• artificial sparkle or CGI plastic appearance\n"
        "• flat lighting that hides product detail\n"
        "\n"
        "Lighting must reveal the product without changing its appearance."
    )


LIGHTING_INSTRUCTIONS: dict[str, object] = {
    "minimalist": _lighting_minimalist,
    "organic": _lighting_organic,
    "luxury": _lighting_luxury,
}


# ─── Negative Constraints ──────────────────────────────────────────────

NEGATIVE_CONSTRAINTS = (
    "NEGATIVE CONSTRAINTS (NON-NEGOTIABLE):\n"
    "Prevent the following failure modes:\n"
    "• on-ear, human model, earlobe, human ear\n"
    "• skin texture, jawline, neck, portrait framing\n"
    "• subsurface skin scattering, anatomical deformation\n"
    "• distorted jewellery geometry\n"
    "• altered product proportions\n"
    "• altered prong count\n"
    "• altered gemstone count\n"
    "• altered gemstone cuts\n"
    "• missing gemstones\n"
    "• additional gemstones\n"
    "• blurry gemstones\n"
    "• floating product\n"
    "• missing contact shadows\n"
    "• unrealistic grounding\n"
    "• artificial CGI plastic look\n"
    "• flat lighting\n"
    "• duplicated jewellery\n"
    "• unrelated accessories\n"
    "• redesigned jewellery"
)


# ─── Complete Prompt Builder ───────────────────────────────────────────

def build_professional_shot_prompt(
    earring_type: Optional[str] = None,
    environment: str = "minimalist",
) -> str:
    """Build the single authoritative Prompt 4 Professional Commercial
    Photography prompt with dynamic environment selection.

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
        environment: Environment archetype. Must be one of:
            "minimalist", "organic", "luxury".
            Defaults to "minimalist".

    Returns:
        The complete Prompt 4 Professional Commercial Photography
        prompt string.
    """
    # Validate environment
    if environment not in VALID_ENVIRONMENTS:
        environment = "minimalist"

    label = ENVIRONMENT_LABELS[environment]
    env_fn = ENVIRONMENT_INSTRUCTIONS[environment]
    light_fn = LIGHTING_INSTRUCTIONS[environment]

    parts: list[str] = []

    # ── Header ──────────────────────────────────────────────────
    parts.append(
        f"TASK: Professional Commercial Earring Photography & "
        f"Dynamic Environment Engine.\n"
        f"\n"
        f"Environment: {label}\n"
        f"\n"
        f"Generate a professional commercial photograph of the exact "
        f"earring from the uploaded reference image, placed in a "
        f"premium professional studio/tabletop environment matching "
        f"the selected archetype.\n"
        f"The result must look like high-end professional commercial "
        f"jewellery photography."
    )

    # ── Reference Priority (prevents backend double-appendition) ──
    parts.append(REFERENCE_PRIORITY_MARKER)

    # ── Product Fidelity — Highest Priority ─────────────────────
    parts.append(
        "PRODUCT FIDELITY — HIGHEST PRIORITY (NON-NEGOTIABLE):\n"
        "The uploaded reference image is the single source of truth for "
        "the jewellery.\n"
        "Preserve the exact visible product characteristics:\n"
        "\n"
        "Preserve EXACTLY:\n"
        "• overall earring identity\n"
        "• geometry\n"
        "• shape\n"
        "• proportions\n"
        "• metal structure\n"
        "• metal colour\n"
        "• bezel geometry\n"
        "• prong count\n"
        "• prong placement\n"
        "• gemstone count\n"
        "• gemstone placement\n"
        "• gemstone shape\n"
        "• facet/cut characteristics\n"
        "• visible construction details\n"
        "• hooks/posts\n"
        "• links and joints\n"
        "• asymmetry\n"
        "• existing physical characteristics\n"
        "\n"
        "Zero intentional product redesign is allowed.\n"
        "\n"
        "Do NOT:\n"
        "• add gemstones\n"
        "• remove gemstones\n"
        "• move gemstones\n"
        "• change gemstone cuts\n"
        "• alter prongs\n"
        "• change bezel geometry\n"
        "• change metal colour\n"
        "• change material\n"
        "• change proportions\n"
        "• beautify the jewellery\n"
        "• make the jewellery more symmetrical\n"
        "• invent missing product details\n"
        "• replace the product with a similar jewellery design\n"
        "\n"
        "If any detail is unclear in the reference, DO NOT invent a "
        "replacement detail."
    )

    # ── Anti-Redesign ───────────────────────────────────────────
    parts.append(
        "ANTI-REDESIGN RULE (NON-NEGOTIABLE):\n"
        "This is a PRODUCT PHOTOGRAPHY task, NOT a design task.\n"
        "You are placing the EXACT uploaded earring into a professional "
        "studio/tabletop environment. You are NOT designing a new earring, "
        "creating an inspired variation, or improving a product.\n"
        "The generated image must show the EXACT same product — same shape, "
        "same stones, same metal, same proportions, same craftsmanship, "
        "same asymmetry, same imperfections.\n"
        "The camera perspective changes to a professional commercial "
        "product-photography view. The jewellery must not change."
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

    # ── Environment-Specific Environment ────────────────────────
    parts.append(env_fn())  # type: ignore[operator]

    # ── Environment-Specific Lighting ───────────────────────────
    parts.append(light_fn())  # type: ignore[operator]

    # ── Optical Style ───────────────────────────────────────────
    parts.append(
        "OPTICAL STYLE (NON-NEGOTIABLE):\n"
        "Professional macro product photography.\n"
        "Approximately 100mm macro visual perspective and f/4 "
        "depth-of-field appearance.\n"
        "Keep the jewellery sharply resolved with controlled photographic "
        "depth of field.\n"
        "\n"
        "Note: These values are visual photographic guidance, not guaranteed "
        "physical camera parameters. Treat them as direction for the "
        "visual aesthetic.\n"
        "\n"
        "Maintain:\n"
        "• clear gemstone detail\n"
        "• clear prongs/settings\n"
        "• readable metal edges\n"
        "• realistic depth of field\n"
        "\n"
        "Avoid:\n"
        "• blurry gemstones\n"
        "• excessive depth-of-field blur that hides the jewellery\n"
        "• artificial sharpening that invents product detail"
    )

    # ── Gemstone Presentation ───────────────────────────────────
    parts.append(
        "GEMSTONE PRESENTATION (NON-NEGOTIABLE):\n"
        "Gemstones should have:\n"
        "• clear detail\n"
        "• realistic facet visibility\n"
        "• controlled brilliance\n"
        "• realistic optical response\n"
        "• appropriate dispersion where naturally visible\n"
        "\n"
        "Avoid:\n"
        "• excessive artificial sparkle\n"
        "• glowing gemstones\n"
        "• blown highlights on gemstones\n"
        "• fake gemstone geometry\n"
        "• altered gemstone cuts\n"
        "\n"
        "Visual enhancement must never change the actual product."
    )

    # ── Environment Interaction ─────────────────────────────────
    parts.append(
        "ENVIRONMENT INTERACTION (NON-NEGOTIABLE):\n"
        "Allow the selected environment to influence realistic lighting, "
        "reflections, shadows, and visual context without changing the "
        "underlying jewellery geometry or product identity.\n"
        "\n"
        "• Dynamic environment lighting/reflection should visually affect "
        "polished metal surfaces while preserving the underlying jewellery "
        "geometry.\n"
        "• Represent environmental reflections as prompt-level photographic "
        "guidance — the image model should render realistic reflections "
        "consistent with the selected environment.\n"
        "• The jewellery's metal surfaces should show subtle reflections "
        "consistent with the surrounding environment.\n"
        "\n"
        "Do NOT:\n"
        "• change jewellery geometry to match environment reflections\n"
        "• add artificial ray-traced reflections\n"
        "• override product identity with environment styling"
    )

    # ── Grounding & Contact Shadows ─────────────────────────────
    parts.append(
        "GROUNDING & CONTACT SHADOWS (NON-NEGOTIABLE):\n"
        "• Realistic grounding — the product must appear physically "
        "resting on or in contact with the selected environment surface.\n"
        "• Natural contact shadows beneath the jewellery consistent "
        "with the surface type and lighting.\n"
        "• Realistic ambient occlusion where the jewellery meets "
        "the surface.\n"
        "• Product must appear physically present in the scene.\n"
        "\n"
        "Avoid:\n"
        "• floating jewellery\n"
        "• disconnected shadows\n"
        "• impossible grounding\n"
        "• excessive shadows that obscure the product\n"
        "• shadows inconsistent with the lighting direction"
    )

    # ── Primary Subject ─────────────────────────────────────────
    parts.append(
        "PRIMARY SUBJECT (NON-NEGOTIABLE):\n"
        "The exact jewellery product remains the dominant subject.\n"
        "The environment is a supporting element, not the primary focus.\n"
        "The jewellery must be the sharpest and most visually prominent "
        "element in the composition."
    )

    # ── Negative Constraints ────────────────────────────────────
    parts.append(NEGATIVE_CONSTRAINTS)

    # ── Image Quality ───────────────────────────────────────────
    parts.append(
        "OUTPUT STYLE:\n"
        "Professional commercial jewellery photography.\n"
        "Premium studio/tabletop aesthetic.\n"
        "Product detail-focused.\n"
        "Editorial quality.\n"
        "\n"
        "The jewellery is the primary visual subject.\n"
        "\n"
        "IMAGE QUALITY:\n"
        "• High-end professional macro jewellery photography.\n"
        "• Extremely sharp jewellery details where in focus.\n"
        "• Preserve fine stones, metal edges, texture, hooks, posts, "
        "and structural details.\n"
        "• High-resolution output.\n"
        "• Preferred aspect ratio: 4:5."
    )

    # ── Final Verification Checklist ────────────────────────────
    parts.append(
        "FINAL VERIFICATION — Before producing the final image, internally "
        "verify:\n"
        "\n"
        "1. Is the jewellery the EXACT same product as the reference?\n"
        "2. Are all gemstones, prongs, metal components, hooks, posts, "
        "and structural details preserved?\n"
        "3. Has the jewellery's original size/proportion remained unchanged?\n"
        "4. Is the environment consistent with the selected archetype?\n"
        "5. Are there realistic contact shadows beneath the jewellery?\n"
        "6. Is the jewellery the sharpest element in the image?\n"
        "7. Is the environment subordinate to the jewellery?\n"
        "8. Do metal surfaces show realistic environmental reflections?\n"
        "9. Does the image look like professional commercial jewellery "
        "photography?\n"
        "10. Is there absolutely NO human model, ear, skin, or anatomy "
        "visible?\n"
        "\n"
        "If any answer is NO, correct the composition before generating the "
        "final image."
    )

    return "\n\n".join(parts)
