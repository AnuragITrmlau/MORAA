"""Chandelier Yellow-Gold Earring — Product Identity Spec Layer.

Lean 3-block architecture (2026-09-17 revision) for generating commercial
photography of ONE specific product: warm yellow-gold chandelier/dangle
earrings with a princess-cut centre stone, pavé petal setting, and hanging
pear droplets (~6.0 cm strict drop).

Visual-failure fixes in this revision:
- SCALE DISTORTION: the scale-reference execution now enforces the strict
  anatomical proportion clause ("strictly 6.0 cm, under 30% of palm area,
  never covering the full palm or wrist-to-finger length") instead of a
  soft range statement.
- BACKGROUND CAST: the e-commerce and scale-reference executions enforce a
  pure white knockout — "100% flat pure digital white (#FFFFFF,
  RGB 255, 255, 255) across the entire canvas edge-to-edge" with zero grey
  falloff / colour tint / vignette / floor seam / textured canvas, plus
  ISOLATED studio lighting (zero ambient fill, zero bounce light) so soft
  shadows can never tint the canvas grey/lilac.
- TOKEN LEANNESS: the 10-point FINAL VERIFICATION checklist and OUTPUT
  QUALITY conversational sections were stripped — non-functional for
  image models and diluting.  Three blocks remain: Identity & Metal Lock,
  Task & Style Execution, Negative Token Cleanliness.

This module is ADDITIVE by design.  It deliberately does NOT modify
``earring_ecommerce_prompt.py`` (Prompt 1), ``earring_scale_reference_prompt.py``,
or any other existing builder: those files are hash-protected by
``backend/tests/test_prompt1_freeze_guard.py`` (MD5) and
``backend/tests/test_part4_audits.py`` (SHA-256).  This spec layer is the
sanctioned place for the background/metal/scale locks on those frozen paths.

Priority order (never reverse):
    1. REFERENCE IMAGE PRIORITY (ground truth)
    2. PRODUCT IDENTITY & METAL LOCK
    3. TASK & STYLE EXECUTION
    4. NEGATIVE TOKEN CLEANLINESS

Zero-token: deterministic string composition only.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Final, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ─── Canonical reference-priority marker ─────────────────────────────────
# MUST equal the marker checked by ImageGenerationManager:
#     if has_reference and "REFERENCE IMAGE PRIORITY" not in prompt.upper():
# Importing the canonical constant keeps the guard in sync in one place.
# (Reference-priority TEXT still arrives via REFERENCE_IMAGE_INSTRUCTION
# imported from the fidelity layer below — it closes the lean prompt as the
# canonical fidelity-layer anchor.)
from app.ai.product_fidelity import REFERENCE_IMAGE_INSTRUCTION

REFERENCE_PRIORITY_MARKER: Final[str] = "REFERENCE IMAGE PRIORITY: MAXIMUM"


# ─── Product identity spec (typed, validated) ───────────────────────────


class MetalColour(str, Enum):
    """Locked metal colour for this product."""

    WARM_YELLOW_GOLD = "warm yellow gold"


class ChandelierIdentitySpec(BaseModel):
    """Validated physical identity of the chandelier yellow-gold earring.

    Every field is mandatory with an explicit default so a caller can never
    silently produce an under-specified identity prompt.  ``model_config``
    forbids extra fields: typos raise immediately instead of degrading the
    identity lock.
    """

    model_config = ConfigDict(extra="forbid")

    product_category: str = Field(
        default="Fashion Dangle/Chandelier Earrings",
        description="Product category for the task header.",
        min_length=3,
    )
    metal_colour: MetalColour = Field(
        default=MetalColour.WARM_YELLOW_GOLD,
        description="LOCKED metal colour — never substituted.",
    )
    metal_lock: str = Field(
        default=(
            "100% warm saturated yellow gold across all prongs, links, and "
            "surfaces"
        ),
        description="Affirmative metal lock clause injected verbatim.",
        min_length=10,
    )
    stone_description: str = Field(
        default="clear white faceted CZ diamonds",
        description="Stone inventory injected verbatim.",
        min_length=5,
    )
    cleanup_targets: List[str] = Field(
        default_factory=lambda: [
            'the white "MORAA" cardboard tag',
            "the plastic holder",
            "human fingers",
            "background clutter",
        ],
        description="Photographic distractions to eliminate completely.",
        min_length=1,
    )
    drop_length_cm_min: float = Field(
        default=6.0,
        ge=1.0,
        le=15.0,
        description="Minimum real-world total drop length in cm.",
    )
    drop_length_cm_max: float = Field(
        default=6.5,
        ge=1.0,
        le=20.0,
        description="Maximum real-world total drop length in cm.",
    )
    max_palm_fraction: float = Field(
        default=0.30,
        gt=0.0,
        le=1.0,
        description="Max fraction of total palm length the earring may cover.",
    )

    @field_validator("drop_length_cm_max")
    @classmethod
    def _validate_length_range(cls, v: float, info) -> float:  # noqa: ANN001
        min_len = info.data.get("drop_length_cm_min")
        if min_len is not None and v < min_len:
            raise ValueError(
                f"drop_length_cm_max ({v}) must be >= drop_length_cm_min ({min_len})"
            )
        return v

    def structural_invariants_text(self) -> str:
        """Render structural invariants as a bullet list."""
        return "\n".join(f"• {item}" for item in self.structural_invariants())

    def structural_invariants(self) -> List[str]:
        """Structural elements whose exact count must be preserved."""
        return [
            "prong count",
            "drop count",
            "hanging link chain",
            "petal cluster arrangement",
            "post/attachment structure",
        ]

    def cleanup_targets_text(self) -> str:
        """Render cleanup targets as a comma-separated clause."""
        return ", ".join(self.cleanup_targets)

    def drop_length_text(self) -> str:
        """Render the real-world length range clause."""
        return (
            f"Approximately {self.drop_length_cm_min:.1f} cm to "
            f"{self.drop_length_cm_max:.1f} cm total drop length"
        )

    def strict_drop_length_text(self) -> str:
        """Render the STRICT length clause used by scale enforcement."""
        return f"strictly {self.drop_length_cm_min:.1f} cm"

    def palm_rule_text(self) -> str:
        """Render the strict palm-coverage rule."""
        pct = round(self.max_palm_fraction * 100)
        return (
            f"covering strictly under {pct}% of the palm surface. It must "
            "appear as a delicate chandelier earring, NEVER covering the "
            "full palm or wrist-to-finger length"
        )


# ─── Style blocks ────────────────────────────────────────────────────────


class StyleKind(str, Enum):
    """The four supported STYLE_BLOCK executions."""

    ECOMMERCE = "ecommerce"
    MACRO = "macro"
    SCALE_REFERENCE = "scale_reference"
    ON_EAR = "on_ear"


# Hardcoded background lock shared by white-background executions.
_WHITE_BACKGROUND_LOCK: Final[str] = (
    "Background: 100% flat pure digital white (#FFFFFF, RGB 255, 255, 255) "
    "across the entire canvas edge-to-edge. Zero grey falloff, zero color "
    "tint, zero vignette, zero floor seam, zero textured canvas. Pure white "
    "knockout background. The earring pair is suspended or placed with only "
    "a crisp subtle contact drop shadow directly underneath."
)

_ECOMMERCE_STYLE_BLOCK: Final[str] = (
    "[STYLE SPECIFIC EXECUTION — CLEAN E-COMMERCE CATALOG PACKSHOT]\n"
    "Style: Clean E-Commerce Catalog Packshot.\n"
    + _WHITE_BACKGROUND_LOCK
    + "\n"
    "Framing: Centered balanced earring pair, side by side, occupying 85% "
    "of vertical frame height.\n"
    "Lighting: ISOLATED studio lighting — light falls on the earrings only. "
    "Zero ambient fill, zero bounce light washing the canvas. Lighting "
    "illuminates the product; it must never tint the background. A crisp "
    "subtle contact drop shadow directly underneath the earrings only — no "
    "cast shadows anywhere else."
)

_MACRO_STYLE_BLOCK: Final[str] = (
    "[STYLE SPECIFIC EXECUTION — EXTREME MACRO JEWELRY CLOSE-UP]\n"
    "Style: Extreme Macro Jewelry Close-Up.\n"
    "Focus: Extreme macro focus on the center stone and micro-pavé prongs "
    "— razor-sharp facets, prong structure, and metal texture.\n"
    "Color Lock: Preserve rich yellow gold saturation; zero desaturation "
    "or silver conversion, no specular highlight blowouts.\n"
    "Background: Soft neutral luxury out-of-focus studio surface with "
    "shallow depth of field (f/4)."
)

_SCALE_REFERENCE_STYLE_BLOCK: Final[str] = (
    "[STYLE SPECIFIC EXECUTION — ANATOMICAL SCALE REFERENCE SHOT]\n"
    "Style: Anatomical Scale Reference Shot.\n"
    "Model: One single feminine manicured hand, resting naturally flat or "
    "slightly cupped.\n"
    "Placement: The single earring rests naturally on the open "
    "palm/fingers. Earring drop length {strict_length}, {palm_rule}.\n"
    "Scale: Miniature-to-medium scale, never oversized.\n"
    + _WHITE_BACKGROUND_LOCK
)

_ON_EAR_STYLE_BLOCK: Final[str] = (
    "[STYLE SPECIFIC EXECUTION — MACRO ON-EAR COMMERCIAL SHOT]\n"
    "Style: Macro On-Ear Commercial Shot.\n"
    "Model: Realistic feminine earlobe, natural skin texture with subtle "
    "pores and no pimples (no plastic AI smoothing).\n"
    "Fit: The top stud attached through the earlobe piercing; the "
    "chandelier drops hang freely below the lobe without merging into "
    "neck skin."
)

_STYLE_BLOCKS: Final[Dict[StyleKind, str]] = {
    StyleKind.ECOMMERCE: _ECOMMERCE_STYLE_BLOCK,
    StyleKind.MACRO: _MACRO_STYLE_BLOCK,
    StyleKind.SCALE_REFERENCE: _SCALE_REFERENCE_STYLE_BLOCK,
    StyleKind.ON_EAR: _ON_EAR_STYLE_BLOCK,
}


def get_style_block(style: StyleKind, spec: ChandelierIdentitySpec) -> str:
    """Return the style-specific execution block for ``style``.

    Args:
        style: One of the four supported :class:`StyleKind` values.
        spec: The validated identity spec (supplies the strict length and
            palm rule for the scale-reference block).

    Returns:
        The rendered style block text.

    Raises:
        ValueError: If ``style`` is not a supported :class:`StyleKind`.
    """
    try:
        style_kind = StyleKind(style)
    except ValueError as exc:
        valid = ", ".join(s.value for s in StyleKind)
        raise ValueError(
            f"Unknown style '{style}'. Valid styles: {valid}"
        ) from exc

    block = _STYLE_BLOCKS[style_kind]
    if style_kind is StyleKind.SCALE_REFERENCE:
        block = block.format(
            strict_length=spec.strict_drop_length_text(),
            palm_rule=spec.palm_rule_text(),
        )
    return block


# ─── Lean prompt builder (3-block architecture) ──────────────────────────


def build_chandelier_gold_prompt(
    style: StyleKind = StyleKind.ECOMMERCE,
    spec: Optional[ChandelierIdentitySpec] = None,
) -> str:
    """Build the lean 3-block image-generation prompt for the earring.

    Block 1 — Identity & Metal Lock (affirmative colour anchoring).
    Block 2 — Task & Style Execution (the rendered style block).
    Block 3 — Negative Token Cleanliness (concise, non-diluting).

    The output embeds the canonical ``REFERENCE IMAGE PRIORITY: MAXIMUM``
    marker so ``ImageGenerationManager`` does not double-append its block,
    and closes with the canonical ``REFERENCE_IMAGE_INSTRUCTION`` imported
    from ``app.ai.product_fidelity`` — keeping this module compatible with
    the existing provider/manager pipeline (OpenAI edits endpoint, Gemini
    multimodal anchoring, marketplace overlay).

    Args:
        style: Which style block to execute. Defaults to the clean
            e-commerce catalog packshot.
        spec: Optional custom identity spec. Defaults to a fresh
            :class:`ChandelierIdentitySpec` (the validated defaults encode
            this product's locked identity).

    Returns:
        The complete prompt string.

    Raises:
        ValueError: If ``style`` is not a supported :class:`StyleKind`.
    """
    active_spec = spec if spec is not None else ChandelierIdentitySpec()
    style_block = get_style_block(style, active_spec)

    # ── BLOCK 1 — Identity & Metal Lock ─────────────────────────────
    block_identity = (
        "IDENTITY & METAL LOCK (NON-NEGOTIABLE):\n"
        "Authoritative ground truth: the uploaded reference image is the "
        "absolute source of truth — preserve the exact earring structure "
        "from the reference (princess-cut centre stone, pavé petal "
        "cluster, hanging pear droplets; exact "
        + "; ".join(active_spec.structural_invariants())
        + ").\n"
        f"Metal finish: {active_spec.metal_lock}. Under NO circumstances "
        "convert to silver, rhodium, platinum, or white gold.\n"
        f"Stones: {active_spec.stone_description}.\n"
        f"Cleanup: completely remove {active_spec.cleanup_targets_text()}. "
        "Preserve 100% of the earring's structural integrity."
    )

    # ── BLOCK 3 — Negative Token Cleanliness ────────────────────────
    block_negatives = (
        "DO NOT generate: silver or rhodium metal, oversized scale, grey "
        "background, fused droplets, missing pear drops, warped links, "
        "text, watermarks, plastic sheen."
    )

    parts: List[str] = [
        # Task header (short — folded into Block 1 lead)
        (
            "TASK: E-Commerce Jewelry Photography Transformation — "
            f"{active_spec.product_category}.\n"
        ),
        # Reference priority marker (prevents manager double-append)
        REFERENCE_PRIORITY_MARKER,
        # BLOCK 1
        block_identity,
        # BLOCK 2
        style_block,
        # BLOCK 3
        block_negatives,
        # Canonical fidelity-layer anchor (reference-image priority text)
        REFERENCE_IMAGE_INSTRUCTION,
    ]

    return "\n\n".join(parts)


# ─── Self-test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    for kind in StyleKind:
        prompt = build_chandelier_gold_prompt(style=kind)
        assert REFERENCE_PRIORITY_MARKER in prompt
        assert "yellow gold" in prompt.lower()
        assert "silver" in prompt.lower()  # present as a prohibition
        assert "FINAL VERIFICATION" not in prompt
        print(f"{kind.value}: {len(prompt)} chars")
