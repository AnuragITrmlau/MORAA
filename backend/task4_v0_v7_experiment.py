"""Task 4 — V0-V7 Controlled Prompt Experiment (Gemini-only).

Tests V0-V7 against 3 real reference images using ONLY Gemini
gemini-3.1-flash-image for fair single-provider comparison.

The previous experiment (PROMPT_EXPERIMENT_REPORT.md) mixed providers:
V0-V2 were OpenAI, V3-V7 were Gemini. This experiment eliminates
that confound by using Gemini for ALL variants.

Only prompt text changes between variants — same provider, same
settings, same reference-image mechanism.

Usage:
    cd backend && python task4_v0_v7_experiment.py
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
    BACKEND_DIR.parent / "Earring Examples" / "ex.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "Ex1.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "example 1.jpeg",
]


# ─── V0-V7 EXACT PROMPTS (from task specification) ─────────────────────
# Each variant builds on the previous one.

V0 = (
    "Create an e-commerce main image of the reference product."
)

V1 = (
    "Create an e-commerce main image of the reference product.\n"
    "Preserve the exact product shown in the reference image."
)

V2 = (
    "Create an e-commerce main image of the reference product.\n"
    "Preserve the exact product shown in the reference image.\n"
    "Preserve the exact shape, geometry, proportions, thickness, curvature, "
    "and component arrangement visible in the reference."
)

V3 = (
    "Create an e-commerce main image of the reference product.\n"
    "Preserve the exact product shown in the reference image.\n"
    "Preserve the exact shape, geometry, proportions, thickness, curvature, "
    "and component arrangement visible in the reference.\n"
    "Preserve every visible jewellery detail, including stones, links, hooks, "
    "posts, clasps, connectors, patterns, textures, and decorative elements."
)

V4 = (
    "Create an e-commerce main image of the reference product.\n"
    "Preserve the exact product shown in the reference image.\n"
    "Preserve the exact shape, geometry, proportions, thickness, curvature, "
    "and component arrangement visible in the reference.\n"
    "Preserve every visible jewellery detail, including stones, links, hooks, "
    "posts, clasps, connectors, patterns, textures, and decorative elements.\n"
    "Preserve the exact material and original colour of the reference product. "
    "Do not recolour, reinterpret, warm, cool, tint, or transform the product."
)

V5 = (
    "Create an e-commerce main image of the reference product.\n"
    "Preserve the exact product shown in the reference image.\n"
    "Preserve the exact shape, geometry, proportions, thickness, curvature, "
    "and component arrangement visible in the reference.\n"
    "Preserve every visible jewellery detail, including stones, links, hooks, "
    "posts, clasps, connectors, patterns, textures, and decorative elements.\n"
    "Preserve the exact material and original colour of the reference product. "
    "Do not recolour, reinterpret, warm, cool, tint, or transform the product.\n"
    "Do not redesign, beautify, simplify, complete, reconstruct, or invent "
    "any part of the jewellery. Preserve only what is supported by the "
    "visible reference."
)

V6 = (
    "Create an e-commerce main image of the reference product.\n"
    "Preserve the exact product shown in the reference image.\n"
    "Preserve the exact shape, geometry, proportions, thickness, curvature, "
    "and component arrangement visible in the reference.\n"
    "Preserve every visible jewellery detail, including stones, links, hooks, "
    "posts, clasps, connectors, patterns, textures, and decorative elements.\n"
    "Preserve the exact material and original colour of the reference product. "
    "Do not recolour, reinterpret, warm, cool, tint, or transform the product.\n"
    "Do not redesign, beautify, simplify, complete, reconstruct, or invent "
    "any part of the jewellery. Preserve only what is supported by the "
    "visible reference.\n"
    "Remove the hand, card, packaging, surface, and unrelated background "
    "elements without removing or modifying any part of the jewellery."
)

V7 = (
    "Create an e-commerce main image of the reference product.\n"
    "Preserve the exact product shown in the reference image.\n"
    "Preserve the exact shape, geometry, proportions, thickness, curvature, "
    "and component arrangement visible in the reference.\n"
    "Preserve every visible jewellery detail, including stones, links, hooks, "
    "posts, clasps, connectors, patterns, textures, and decorative elements.\n"
    "Preserve the exact material and original colour of the reference product. "
    "Do not recolour, reinterpret, warm, cool, tint, or transform the product.\n"
    "Do not redesign, beautify, simplify, complete, reconstruct, or invent "
    "any part of the jewellery. Preserve only what is supported by the "
    "visible reference.\n"
    "Remove the hand, card, packaging, surface, and unrelated background "
    "elements without removing or modifying any part of the jewellery.\n"
    "Present the preserved jewellery on a clean white e-commerce background "
    "with neutral balanced lighting and appropriate margins."
)

VARIANTS = {
    "V0": ("MINIMUM", V0),
    "V1": ("+ IDENTITY", V1),
    "V2": ("+ GEOMETRY", V2),
    "V3": ("+ DETAILS", V3),
    "V4": ("+ MATERIAL + COLOUR", V4),
    "V5": ("+ NO INVENTION", V5),
    "V6": ("+ CLEANUP", V6),
    "V7": ("+ E-COMMERCE", V7),
}


async def generate_one(
    variant_name: str,
    prompt: str,
    ref_path: Path,
    provider: GeminiImageProvider,
) -> dict:
    """Generate one image for one variant + one reference."""
    ref_bytes = ref_path.read_bytes()

    context = {
        "request_id": f"v0v7-{variant_name}-{ref_path.stem}",
        "aspect_ratio": "1:1",
    }

    t0 = time.time()
    result = await provider.generate_image(
        prompt, context,
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
        "prompt_len": len(prompt),
    }


async def main() -> None:
    out_dir = BACKEND_DIR / "task4_outputs"
    out_dir.mkdir(exist_ok=True)

    provider = GeminiImageProvider()

    # Save prompts for inspection
    for name, (desc, prompt) in VARIANTS.items():
        (out_dir / f"v0v7_{name}_prompt.txt").write_text(prompt, encoding="utf-8")
        print(f"{name} ({desc}): {len(prompt)} chars")

    print("=" * 70)
    print("V0-V7 Controlled Experiment — Gemini Only")
    print("=" * 70)

    results = []

    for variant_name, (desc, prompt) in VARIANTS.items():
        print(f"\n--- {variant_name}: {desc} ---")

        for ref_path in REFERENCES:
            print(f"  {ref_path.name} ... ", end="", flush=True)
            result = await generate_one(variant_name, prompt, ref_path, provider)
            results.append(result)

            if result["success"]:
                b64 = result["image_url"].split(",", 1)[-1]
                out_name = f"v0v7_{variant_name}_{ref_path.stem}.png"
                out_path = out_dir / out_name
                out_path.write_bytes(base64.b64decode(b64))
                print(f"OK {result['time']}s -> {out_name}")
            else:
                print(f"FAIL: {result['error'][:80]}")

    # Save results JSON
    results_clean = [{k: v for k, v in r.items() if k != "image_url"} for r in results]
    (out_dir / "v0v7_experiment_results.json").write_text(
        json.dumps(results_clean, indent=2), encoding="utf-8"
    )

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Var':4s} | {'Reference':22s} | {'Status':6s} | {'Time':6s} | {'Chars':6s}")
    print("-" * 70)
    for r in results_clean:
        status = "OK" if r["success"] else "FAIL"
        print(
            f"{r['variant']:4s} | {r['reference']:22s} | {status:6s} | "
            f"{r['time']:5.1f}s | {r['prompt_len']:5d}"
        )

    print(f"\nResults saved to {out_dir / 'v0v7_experiment_results.json'}")
    print(f"Images saved to {out_dir}")


if __name__ == "__main__":
    asyncio.run(main())
