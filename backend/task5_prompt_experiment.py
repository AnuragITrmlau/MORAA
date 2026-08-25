"""Task 5 — Systematic Prompt Experiment for Earring E-Commerce.

Phase 1-4: Create minimal prompt, test, evaluate, add one rule at a time.

V1: Minimal prompt (1-3 sentences)
V2: + Stronger identity preservation
V3: + Material/colour lock
V4: + Cleanup rule (remove hand/card)
V5: + Geometry/detail preservation

Uses Gemini only (single provider for fair comparison).
Does NOT overwrite existing Task 2/3/4 artifacts.

Usage:
    cd backend && python task5_prompt_experiment.py
"""

import asyncio
import base64
import json
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from app.ai.providers.gemini_image_provider import GeminiImageProvider
from app.ai.marketplaces.registry import get_marketplace_presentation

REFERENCES = [
    (BACKEND_DIR.parent / "Earring Examples" / "ex.jpeg", "R1"),
    (BACKEND_DIR.parent / "Earring Examples" / "Ex1.jpeg", "R2"),
    (BACKEND_DIR.parent / "Earring Examples" / "example 1.jpeg", "R3"),
]

# ─── PROMPT VARIANTS ───────────────────────────────────────────────────
# Each variant adds ONE instruction to the previous variant.
# V1 is the absolute minimum.

V1 = (
    "Create a clean e-commerce main image of the earring shown in the "
    "reference image. The reference image is the source of truth for the "
    "exact product. Preserve the earring's identity, geometry, material, "
    "colour and visible details exactly as shown. Remove photographic "
    "distractions and present the same product on a clean white background."
)

V2 = V1 + (
    " This is a product photography task, not a design task. "
    "Do not redesign, beautify, simplify, symmetrise, or invent any part "
    "of the jewellery. The generated image must show the exact same earring "
    "with the same shape, stones, metal, proportions and craftsmanship."
)

V3 = V2 + (
    " Preserve the exact material and colour: gold stays gold, silver stays "
    "silver, brass stays brass. Do not recolour, warm, cool, tint, or "
    "transform the product's metal or stone colours."
)

V4 = V3 + (
    " Remove the human hand, fingers, card, backing, packaging, surface "
    "and any non-jewellery element. When removing these, do NOT remove or "
    "modify any part of the actual jewellery — hooks, posts, chains, "
    "clasps and decorative components are part of the product."
)

V5 = V4 + (
    " Preserve every visible jewellery detail: stone count, stone placement, "
    "stone shape, bead arrangement, hooks, posts, chains, connectors, "
    "clasps, filigree, engravings, textures and decorative elements. "
    "Preserve any visible asymmetry — do not symmetrise an asymmetric design."
)

VARIANTS = {
    "V1": ("Minimal (1-3 sentences)", V1),
    "V2": ("+ Identity lock", V2),
    "V3": ("+ Material/colour lock", V3),
    "V4": ("+ Cleanup rule", V4),
    "V5": ("+ Detail preservation", V5),
}


async def generate_one(
    variant_name: str,
    prompt: str,
    ref_path: Path,
    ref_id: str,
    provider: GeminiImageProvider,
    marketplace_prompt: str,
) -> dict:
    """Generate one image for one variant + one reference."""
    ref_bytes = ref_path.read_bytes()

    # Append marketplace block (same as production)
    effective_prompt = prompt
    if marketplace_prompt:
        effective_prompt += f"\n\n{marketplace_prompt}"

    context = {
        "request_id": f"task5-{variant_name}-{ref_id}",
        "aspect_ratio": "1:1",
    }

    t0 = time.time()
    result = await provider.generate_image(
        effective_prompt, context,
        reference_image=ref_bytes,
        reference_mime_type="image/jpeg",
    )
    elapsed = time.time() - t0

    return {
        "variant": variant_name,
        "reference": ref_id,
        "reference_file": ref_path.name,
        "success": result.success,
        "provider": result.provider_name,
        "model": result.model_used,
        "time": round(elapsed, 1),
        "error": result.error,
        "image_url": result.image_url if result.success else None,
        "prompt_len": len(effective_prompt),
    }


async def main() -> None:
    out_dir = BACKEND_DIR / "task5_outputs"
    out_dir.mkdir(exist_ok=True)

    mp = get_marketplace_presentation("amazon_india_fashion_earrings")
    marketplace_prompt = mp.prompt_block if mp else ""

    provider = GeminiImageProvider()

    # Save prompts for inspection
    for name, (desc, prompt) in VARIANTS.items():
        effective = prompt
        if marketplace_prompt:
            effective += f"\n\n{marketplace_prompt}"
        (out_dir / f"{name}_prompt.txt").write_text(effective, encoding="utf-8")
        print(f"{name} ({desc}): {len(effective)} chars, {len(effective.split())} words")

    print("=" * 70)
    print("Task 5 — Systematic Prompt Experiment (Gemini Only)")
    print("=" * 70)

    results = []

    for variant_name, (desc, prompt) in VARIANTS.items():
        print(f"\n--- {variant_name}: {desc} ---")

        for ref_path, ref_id in REFERENCES:
            print(f"  {ref_id} ({ref_path.name}) ... ", end="", flush=True)
            result = await generate_one(
                variant_name, prompt, ref_path, ref_id, provider, marketplace_prompt
            )
            results.append(result)

            if result["success"]:
                b64 = result["image_url"].split(",", 1)[-1]
                out_name = f"{variant_name}_{ref_id}.png"
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

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Var':4s} | {'Ref':3s} | {'Status':6s} | {'Time':6s} | {'Chars':6s}")
    print("-" * 50)
    for r in results_clean:
        status = "OK" if r["success"] else "FAIL"
        print(
            f"{r['variant']:4s} | {r['reference']:3s} | {status:6s} | "
            f"{r['time']:5.1f}s | {r['prompt_len']:5d}"
        )

    print(f"\nResults saved to {out_dir / 'experiment_results.json'}")
    print(f"Images saved to {out_dir}")


if __name__ == "__main__":
    asyncio.run(main())
