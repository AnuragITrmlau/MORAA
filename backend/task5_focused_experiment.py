"""Task 5 — Focused Experiment: Fix Product Destruction.

The V1-V5 experiment revealed that ALL variants destroy the product
(97.7% product area → 16-20%) when asked for a white background.

This focused experiment tests whether removing/changing the background
instruction preserves the product.

V6: No background instruction at all (just preserve product)
V7: Explicit "do NOT remove the product" + white background
V8: "Keep the earring in the same position, only change the background behind it"

Usage:
    cd backend && python task5_focused_experiment.py
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

# ─── FOCUSED PROMPT VARIANTS ──────────────────────────────────────────

V6 = (
    "Generate an e-commerce image of the earring in the reference photo. "
    "Keep the exact earring exactly as it appears — same shape, same metal, "
    "same stones, same proportions. Do not change, remove or redraw any "
    "part of the jewellery."
)

V7 = (
    "Generate an e-commerce image of the earring in the reference photo. "
    "Keep the exact earring exactly as it appears — same shape, same metal, "
    "same stones, same proportions. Do not change, remove or redraw any "
    "part of the jewellery. "
    "Place the earring on a clean white background (RGB 255,255,255). "
    "IMPORTANT: Do NOT remove the earring itself — only change the "
    "background behind it. The earring must remain fully visible and "
    "unchanged."
)

V8 = (
    "Generate an e-commerce image of the earring in the reference photo. "
    "Keep the exact earring exactly as it appears — same shape, same metal, "
    "same stones, same proportions. Do not change, remove or redraw any "
    "part of the jewellery. "
    "Keep the earring in its current position and orientation. Only replace "
    "the background behind the earring with a clean white surface. "
    "The earring is the product and must remain fully intact."
)

VARIANTS = {
    "V6": ("No background instruction", V6),
    "V7": ("White bg + do NOT remove product", V7),
    "V8": ("Keep position + replace bg only", V8),
}


async def generate_one(variant_name, prompt, ref_path, ref_id, provider, marketplace_prompt):
    ref_bytes = ref_path.read_bytes()
    effective_prompt = prompt
    if marketplace_prompt:
        effective_prompt += f"\n\n{marketplace_prompt}"
    context = {"request_id": f"task5f-{variant_name}-{ref_id}", "aspect_ratio": "1:1"}
    t0 = time.time()
    result = await provider.generate_image(
        effective_prompt, context,
        reference_image=ref_bytes,
        reference_mime_type="image/jpeg",
    )
    elapsed = time.time() - t0
    return {
        "variant": variant_name, "reference": ref_id,
        "success": result.success, "time": round(elapsed, 1),
        "error": result.error,
        "image_url": result.image_url if result.success else None,
        "prompt_len": len(effective_prompt),
    }


async def main():
    out_dir = BACKEND_DIR / "task5_outputs"
    out_dir.mkdir(exist_ok=True)

    mp = get_marketplace_presentation("amazon_india_fashion_earrings")
    marketplace_prompt = mp.prompt_block if mp else ""
    provider = GeminiImageProvider()

    for name, (desc, prompt) in VARIANTS.items():
        effective = prompt + (f"\n\n{marketplace_prompt}" if marketplace_prompt else "")
        (out_dir / f"{name}_prompt.txt").write_text(effective, encoding="utf-8")
        print(f"{name} ({desc}): {len(effective)} chars")

    print("=" * 70)
    results = []
    for variant_name, (desc, prompt) in VARIANTS.items():
        print(f"\n--- {variant_name}: {desc} ---")
        for ref_path, ref_id in REFERENCES:
            print(f"  {ref_id} ... ", end="", flush=True)
            result = await generate_one(variant_name, prompt, ref_path, ref_id, provider, marketplace_prompt)
            results.append(result)
            if result["success"]:
                b64 = result["image_url"].split(",", 1)[-1]
                out_path = out_dir / f"{variant_name}_{ref_id}.png"
                out_path.write_bytes(base64.b64decode(b64))
                print(f"OK {result['time']}s")
            else:
                print(f"FAIL: {result['error'][:80]}")

    results_clean = [{k: v for k, v in r.items() if k != "image_url"} for r in results]
    (out_dir / "focused_results.json").write_text(
        json.dumps(results_clean, indent=2), encoding="utf-8"
    )
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
