"""Task 3 — Controlled Prompt Experiment.

Tests 4 prompt variants against 3 reference images to isolate
whether prompt wording affects material/colour fidelity.

Variant A: Current Task 1 prompt exactly as-is (baseline)
Variant B: Current prompt + explicit colour lock instruction
Variant C: Current prompt + colour lock + remove "colour temperature"
           from MAY CHANGE + neutral lighting instruction
Variant D: Current prompt + colour/material lock + stronger
           reconstruction prohibition + remove "enhance" language

Usage:
    cd backend && python task3_experiment.py
"""

import asyncio
import base64
import json
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from app.ai.providers.openai_image_provider import OpenAIImageProvider
from app.ai.marketplaces.registry import get_marketplace_presentation
from app.config import settings

REFERENCES = [
    BACKEND_DIR.parent / "Earring Examples" / "ex.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "Ex1.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "example 1.jpeg",
]

# ─── COLOUR LOCK INSTRUCTION (experimental) ────────────────────────────

COLOUR_LOCK = (
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


# ─── VARIANT BUILDERS ──────────────────────────────────────────────────

def _base_prompt() -> str:
    """Return the current Task 1 prompt exactly as-is."""
    from app.services.earring_ecommerce_prompt import (
        ANTI_REDESIGN_INSTRUCTION,
        ANTI_SYMMETRY_INSTRUCTION,
        ANGLE_PRESERVATION_INSTRUCTION,
        ECOMMERCE_PRESENTATION_INSTRUCTION,
        GENERIC_EARRING_PRESERVATION,
        INPUT_CLEANUP_INSTRUCTION,
        MATERIAL_FIDELITY_INSTRUCTION,
        REFERENCE_PRIORITY_MARKER,
    )

    parts = [
        "TASK: Generate a single e-commerce main image for a Fashion "
        "Jewellery Earring product. The uploaded reference image is the "
        "authoritative source of truth for the actual product.",
        REFERENCE_PRIORITY_MARKER,
        ANTI_REDESIGN_INSTRUCTION,
        ANTI_SYMMETRY_INSTRUCTION,
        (
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
        ),
        GENERIC_EARRING_PRESERVATION,
        MATERIAL_FIDELITY_INSTRUCTION,
        INPUT_CLEANUP_INSTRUCTION,
        ANGLE_PRESERVATION_INSTRUCTION,
        ECOMMERCE_PRESENTATION_INSTRUCTION,
        (
            "OUTPUT RULE:\n"
            "The earring must appear WITHOUT any jewellery card, display "
            "backing, packaging, human hand, or non-jewellery elements. "
            "The earring is the ONLY object in the image."
        ),
    ]
    return "\n\n".join(parts)


def variant_a() -> str:
    """Variant A: Current Task 1 prompt exactly as-is (baseline)."""
    return _base_prompt()


def variant_b() -> str:
    """Variant B: Current prompt + explicit colour lock."""
    return _base_prompt() + "\n\n" + COLOUR_LOCK


def variant_c() -> str:
    """Variant C: Current prompt + colour lock + remove "colour temperature"
    from MAY CHANGE + neutral lighting instruction."""
    base = _base_prompt()

    # Remove the ECOMMERCE_PRESENTATION section and replace with a
    # version that does NOT allow colour temperature changes and uses
    # neutral lighting.
    old_presentation = (
        "E-COMMERCE PRESENTATION (PRESENTATION ONLY — not product-identity):\n"
        "Generate a clean, professional e-commerce main image:\n"
        "• Clean commercial presentation with clear product visibility.\n"
        "• Product centred appropriately with sufficient margins.\n"
        "• Sharp product with realistic material rendering.\n"
        "• Realistic, controlled lighting — no harsh shadows on the product.\n"
        "• Controlled reflections that enhance the metal and stone appearance.\n"
        "• No distracting props, text, logos, watermarks, or overlays.\n"
        "• No packaging, no jewellery card, no display backing.\n"
        "• The product is the sole visual focus.\n"
        "• Professional studio-quality presentation suitable for an "
        "e-commerce product listing.\n"
        "• Background should be clean and non-distracting.\n"
        "• Accurate scale — the earring should appear at realistic size "
        "relative to its actual dimensions."
    )

    new_presentation = (
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
        "• CRITICAL: The colour temperature of the lighting MUST match "
        "the reference. Silver metals must stay silver. Gold metals must "
        "stay gold. Do NOT warm or cool the product's natural colour."
    )

    base = base.replace(old_presentation, new_presentation)
    return base + "\n\n" + COLOUR_LOCK


def variant_d() -> str:
    """Variant D: Current prompt + colour/material lock + stronger
    reconstruction prohibition + remove "enhance" language."""
    base = variant_c()  # Start from variant C (which already has fixes)

    # Also strengthen the anti-redesign instruction
    old_redesign = (
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

    new_redesign = (
        "ANTI-REDESIGN RULE (NON-NEGOTIABLE — HIGHEST PRIORITY):\n"
        "This is a PRODUCT PHOTOGRAPHY task, NOT a design task.\n"
        "You are photographing the EXACT uploaded product in a clean studio "
        "setting. You are NOT designing a new earring, creating an "
        "inspired variation, or improving a product.\n"
        "The generated image must show the EXACT same product — same shape, "
        "same stones, same metal colour, same proportions, same craftsmanship, "
        "same asymmetry, same imperfections.\n"
        "Do NOT reconstruct or infer product geometry that is hidden or "
        "occluded in the reference. If a section of the product is hidden "
        "by a hand or angle, that section must NOT be invented — leave it "
        "as it appears or omit it rather than fabricating unsupported details.\n"
        "Only the presentation changes: background, lighting direction, "
        "composition, and commercial quality. The product's material, "
        "colour, and geometry must remain byte-for-byte identical to the "
        "reference."
    )

    base = base.replace(old_redesign, new_redesign)
    return base


# ─── EXPERIMENT RUNNER ─────────────────────────────────────────────────

VARIANTS = {
    "A": ("Baseline (current prompt)", variant_a),
    "B": ("+ Colour Lock", variant_b),
    "C": ("+ Colour Lock + Neutral Lighting", variant_c),
    "D": ("+ Colour Lock + Neutral Lighting + Anti-Reconstruct", variant_d),
}


async def run_variant(
    variant_name: str,
    prompt: str,
    ref_path: Path,
    provider: OpenAIImageProvider,
    marketplace_prompt: str,
) -> dict:
    """Run a single variant against a single reference image."""
    ref_bytes = ref_path.read_bytes()

    # Append marketplace block (same as production)
    effective_prompt = prompt
    if marketplace_prompt:
        effective_prompt += f"\n\n{marketplace_prompt}"

    # Prepend identity anchor (same as production OpenAI path)
    from app.ai.providers.openai_image_provider import OPENAI_IDENTITY_ANCHOR
    openai_prompt = f"{OPENAI_IDENTITY_ANCHOR}\n\n{effective_prompt}"

    context = {
        "request_id": f"task3-{variant_name}-{ref_path.stem}",
        "aspect_ratio": "1:1",  # Amazon default
    }

    t0 = time.time()
    result = await provider.generate_image(
        openai_prompt, context,
        reference_image=ref_bytes,
        reference_mime_type="image/jpeg",
    )
    elapsed = time.time() - t0

    return {
        "variant": variant_name,
        "reference": ref_path.name,
        "success": result.success,
        "provider": result.provider_name,
        "model": result.model_used,
        "time": round(elapsed, 1),
        "error": result.error,
        "image_url": result.image_url if result.success else None,
        "prompt_len": len(openai_prompt),
    }


async def main() -> None:
    out_dir = BACKEND_DIR / "task3_outputs"
    out_dir.mkdir(exist_ok=True)

    # Get marketplace block
    mp = get_marketplace_presentation("amazon_india_fashion_earrings")
    marketplace_prompt = mp.prompt_block if mp else ""

    provider = OpenAIImageProvider()

    # Save variant prompts for inspection
    for name, (_, builder) in VARIANTS.items():
        prompt = builder()
        prompt += f"\n\n{marketplace_prompt}"
        from app.ai.providers.openai_image_provider import OPENAI_IDENTITY_ANCHOR
        full = f"{OPENAI_IDENTITY_ANCHOR}\n\n{prompt}"
        (out_dir / f"variant_{name}_prompt.txt").write_text(full, encoding="utf-8")
        print(f"Variant {name}: {len(full)} chars")

    print("=" * 70)

    results = []

    for variant_name, (description, builder) in VARIANTS.items():
        prompt = builder()
        print(f"\n--- Variant {variant_name}: {description} ---")

        for ref_path in REFERENCES:
            print(f"  Reference: {ref_path.name} ... ", end="", flush=True)
            result = await run_variant(
                variant_name, prompt, ref_path, provider, marketplace_prompt
            )
            results.append(result)

            if result["success"]:
                b64 = result["image_url"].split(",", 1)[-1]
                out_name = f"{variant_name}_{ref_path.stem}_output.png"
                out_path = out_dir / out_name
                out_path.write_bytes(base64.b64decode(b64))
                print(f"OK {result['time']}s -> {out_name}")
            else:
                print(f"FAIL: {result['error'][:80]}")

    # Save results JSON
    results_clean = [{k: v for k, v in r.items() if k != "image_url"} for r in results]
    (out_dir / "experiment_results.json").write_text(
        json.dumps(results_clean, indent=2), encoding="utf-8"
    )
    print(f"\nResults saved to {out_dir / 'experiment_results.json'}")

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for r in results_clean:
        status = "OK" if r["success"] else "FAIL"
        print(
            f"  {r['variant']} | {r['reference']:20s} | {status} | "
            f"{r['time']:5.1f}s | {r['prompt_len']} chars"
        )


if __name__ == "__main__":
    asyncio.run(main())
