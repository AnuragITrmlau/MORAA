"""Prompt Experiment — find the smallest reliable prompt for earring e-commerce.

Tests V0-V7 against 3 reference images using OpenAI gpt-image-1.
Only the prompt text changes between variants.

Usage:
    cd backend && python prompt_experiment.py
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
from app.ai.providers.openai_image_provider import OPENAI_IDENTITY_ANCHOR

REFERENCES = [
    BACKEND_DIR.parent / "Earring Examples" / "ex.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "Ex1.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "example 1.jpeg",
]


# ─── PROMPT VARIANTS ───────────────────────────────────────────────────

V0 = "Create an e-commerce main image of the reference product."

V1 = V0 + " The reference image is the exact product to reproduce. Preserve the exact shape, geometry, and proportions."

V2 = V1 + " Preserve the exact colours of the metal and stones as shown in the reference. Do not change silver to gold or any other material colour."

V3 = V2 + " Preserve the exact material — gold stays gold, silver stays silver, brass stays brass. Do not change the material appearance."

V4 = V3 + " Preserve every visible detail — stone count, stone placement, stone shape, decorative elements, hooks, posts, connectors. Do not add or remove any visible element."

V5 = V4 + " Remove the human hand, fingers, card, backing, or any non-jewellery element from the image."

V6 = V5 + " Place the product on a clean white background (RGB 255,255,255)."

V7 = V6 + " Use neutral, balanced lighting that does not change the product's natural colour temperature."

VARIANTS = {
    "V0": V0,
    "V1": V1,
    "V2": V2,
    "V3": V3,
    "V4": V4,
    "V5": V5,
    "V6": V6,
    "V7": V7,
}


async def generate_one(
    variant_name: str,
    prompt: str,
    ref_path: Path,
    provider: OpenAIImageProvider,
    marketplace_prompt: str,
) -> dict:
    """Generate one image for one variant + one reference."""
    ref_bytes = ref_path.read_bytes()

    # Append marketplace block (same as production)
    effective_prompt = prompt
    if marketplace_prompt:
        effective_prompt += f"\n\n{marketplace_prompt}"

    # Prepend identity anchor (same as production OpenAI path)
    openai_prompt = f"{OPENAI_IDENTITY_ANCHOR}\n\n{effective_prompt}"

    context = {
        "request_id": f"exp-{variant_name}-{ref_path.stem}",
        "aspect_ratio": "1:1",
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
    out_dir = BACKEND_DIR / "prompt_experiment_outputs"
    out_dir.mkdir(exist_ok=True)

    mp = get_marketplace_presentation("amazon_india_fashion_earrings")
    marketplace_prompt = mp.prompt_block if mp else ""

    provider = OpenAIImageProvider()

    # Save prompts for inspection
    for name, prompt in VARIANTS.items():
        effective = prompt
        if marketplace_prompt:
            effective += f"\n\n{marketplace_prompt}"
        full = f"{OPENAI_IDENTITY_ANCHOR}\n\n{effective}"
        (out_dir / f"{name}_prompt.txt").write_text(full, encoding="utf-8")
        print(f"{name}: {len(full)} chars")

    print("=" * 70)

    results = []

    for variant_name, prompt in VARIANTS.items():
        print(f"\n--- {variant_name} ---")
        for ref_path in REFERENCES:
            print(f"  {ref_path.name} ... ", end="", flush=True)
            result = await generate_one(
                variant_name, prompt, ref_path, provider, marketplace_prompt
            )
            results.append(result)

            if result["success"]:
                b64 = result["image_url"].split(",", 1)[-1]
                out_name = f"{variant_name}_{ref_path.stem}.png"
                out_path = out_dir / out_name
                out_path.write_bytes(base64.b64decode(b64))
                print(f"OK {result['time']}s")
            else:
                print(f"FAIL: {result['error'][:60]}")

    # Save results
    results_clean = [{k: v for k, v in r.items() if k != "image_url"} for r in results]
    (out_dir / "results.json").write_text(
        json.dumps(results_clean, indent=2), encoding="utf-8"
    )
    print(f"\nResults saved to {out_dir / 'results.json'}")


if __name__ == "__main__":
    asyncio.run(main())
