"""Prompt Experiment — Gemini fallback for failed variants.

Completes V3-V7 using Gemini since OpenAI credits ran out.
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
from app.ai.product_fidelity import REFERENCE_IMAGE_ANCHOR

REFERENCES = [
    BACKEND_DIR.parent / "Earring Examples" / "ex.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "Ex1.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "example 1.jpeg",
]

V0 = "Create an e-commerce main image of the reference product."
V1 = V0 + " The reference image is the exact product to reproduce. Preserve the exact shape, geometry, and proportions."
V2 = V1 + " Preserve the exact colours of the metal and stones as shown in the reference. Do not change silver to gold or any other material colour."
V3 = V2 + " Preserve the exact material — gold stays gold, silver stays silver, brass stays brass. Do not change the material appearance."
V4 = V3 + " Preserve every visible detail — stone count, stone placement, stone shape, decorative elements, hooks, posts, connectors. Do not add or remove any visible element."
V5 = V4 + " Remove the human hand, fingers, card, backing, or any non-jewellery element from the image."
V6 = V5 + " Place the product on a clean white background (RGB 255,255,255)."
V7 = V6 + " Use neutral, balanced lighting that does not change the product's natural colour temperature."

# Only test variants that failed on OpenAI
VARIANTS_TO_TEST = {"V3": V3, "V4": V4, "V5": V5, "V6": V6, "V7": V7}


async def main() -> None:
    out_dir = BACKEND_DIR / "prompt_experiment_outputs"
    out_dir.mkdir(exist_ok=True)

    mp = get_marketplace_presentation("amazon_india_fashion_earrings")
    marketplace_prompt = mp.prompt_block if mp else ""

    provider = GeminiImageProvider()

    results = []

    for variant_name, prompt in VARIANTS_TO_TEST.items():
        print(f"\n--- {variant_name} (Gemini) ---")
        for ref_path in REFERENCES:
            ref_bytes = ref_path.read_bytes()
            effective_prompt = prompt
            if marketplace_prompt:
                effective_prompt += f"\n\n{marketplace_prompt}"

            context = {
                "request_id": f"exp-gemini-{variant_name}-{ref_path.stem}",
                "aspect_ratio": "1:1",
            }

            print(f"  {ref_path.name} ... ", end="", flush=True)
            t0 = time.time()
            result = await provider.generate_image(
                effective_prompt, context,
                reference_image=ref_bytes,
                reference_mime_type="image/jpeg",
            )
            elapsed = time.time() - t0

            entry = {
                "variant": variant_name,
                "reference": ref_path.name,
                "success": result.success,
                "provider": "gemini",
                "model": result.model_used,
                "time": round(elapsed, 1),
                "error": result.error,
                "prompt_len": len(effective_prompt) + len(REFERENCE_IMAGE_ANCHOR),
            }

            if result.success and result.image_url:
                b64 = result.image_url.split(",", 1)[-1]
                out_name = f"{variant_name}_{ref_path.stem}.png"
                out_path = out_dir / out_name
                out_path.write_bytes(base64.b64decode(b64))
                entry["saved"] = str(out_path)
                print(f"OK {elapsed:.1f}s -> {out_name}")
            else:
                print(f"FAIL: {result.error[:60]}")

            results.append(entry)

    # Append to existing results
    results_path = out_dir / "results_gemini.json"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nGemini results saved to {results_path}")


if __name__ == "__main__":
    asyncio.run(main())
