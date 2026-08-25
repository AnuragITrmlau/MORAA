"""Task 5 — Final Test: Most explicit reproduction instruction.

Tests whether the most forceful possible instruction to reproduce
the reference image can overcome the product destruction problem.

V9: Maximum explicitness — "This is a PHOTO of the product. Do not generate.
    Copy the product pixels exactly."

Usage:
    cd backend && python task5_final_test.py
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

V9 = (
    "You are a photo editor. The attached image IS the product photo. "
    "Your ONLY job is to produce a clean e-commerce version of THIS exact photo. "
    "Do not generate a new image. Do not draw a new earring. "
    "Keep the earring pixels exactly as they appear in the photo. "
    "Replace ONLY the background with clean white. "
    "The earring must look identical to how it looks in the attached photo."
)


async def main():
    out_dir = BACKEND_DIR / "task5_outputs"
    out_dir.mkdir(exist_ok=True)

    mp = get_marketplace_presentation("amazon_india_fashion_earrings")
    marketplace_prompt = mp.prompt_block if mp else ""
    provider = GeminiImageProvider()

    effective = V9 + (f"\n\n{marketplace_prompt}" if marketplace_prompt else "")
    (out_dir / "V9_prompt.txt").write_text(effective, encoding="utf-8")
    print(f"V9: {len(effective)} chars")

    for ref_path, ref_id in REFERENCES:
        ref_bytes = ref_path.read_bytes()
        context = {"request_id": f"task5f-V9-{ref_id}", "aspect_ratio": "1:1"}
        print(f"  {ref_id} ... ", end="", flush=True)
        t0 = time.time()
        result = await provider.generate_image(
            effective, context,
            reference_image=ref_bytes,
            reference_mime_type="image/jpeg",
        )
        elapsed = time.time() - t0
        if result.success:
            b64 = result.image_url.split(",", 1)[-1]
            out_path = out_dir / f"V9_{ref_id}.png"
            out_path.write_bytes(base64.b64decode(b64))
            print(f"OK {elapsed:.1f}s")
        else:
            print(f"FAIL: {result.error[:80]}")

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
