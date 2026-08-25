"""TASK 2 — Real image generation using the ACTUAL runtime path.

Mirrors exactly what the frontend + /api/generate-image do:
    prompt = build_earring_ecommerce_prompt(earring_type=None)   # Auto-detect
    manager.generate_image(
        prompt,
        context={"request_id": ..., "aspect_ratio": "4:5"},
        reference_image=<jpeg bytes>,
        marketplace="amazon_india_fashion_earrings",
    )

No production code is modified.
"""

import asyncio
import base64
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from app.ai.image_generation_manager import ImageGenerationManager
from app.services.earring_ecommerce_prompt import (
    build_earring_ecommerce_prompt,
)

REFERENCES = [
    BACKEND_DIR.parent / "Earring Examples" / "ex.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "Ex1.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "example 1.jpeg",
]
OUT_DIR = BACKEND_DIR / "task2_outputs"
OUT_DIR.mkdir(exist_ok=True)


async def main() -> None:
    # Log the effective prompt once so we can verify what reaches providers.
    prompt = build_earring_ecommerce_prompt(earring_type=None)
    (OUT_DIR / "effective_prompt_auto.txt").write_text(prompt, encoding="utf-8")
    print(f"PROMPT LEN={len(prompt)} saved to effective_prompt_auto.txt")
    print("PROMPT HEAD:", prompt[:200].replace("\n", " | "))
    print("=" * 70)

    manager = ImageGenerationManager()

    for ref in REFERENCES:
        ref_bytes = ref.read_bytes()
        print(f"\n=== REFERENCE: {ref.name} ({len(ref_bytes)} bytes) ===")
        t0 = time.time()
        result = await manager.generate_image(
            prompt=prompt,
            context={
                "request_id": f"task2-{ref.stem}",
                "aspect_ratio": "4:5",  # same as frontend handleEcommerceGenerate
            },
            reference_image=ref_bytes,
            reference_mime_type="image/jpeg",
            marketplace="amazon_india_fashion_earrings",  # same as frontend
        )
        elapsed = time.time() - t0
        if result.success and result.image_url:
            b64 = result.image_url.split(",", 1)[-1]
            out_path = OUT_DIR / f"{ref.stem}_output.png"
            out_path.write_bytes(base64.b64decode(b64))
            print(f"SUCCESS provider={result.provider_name} "
                  f"fallback={result.fallback_used} "
                  f"model={result.model_used} time={elapsed:.1f}s")
            print(f"SAVED {out_path}")
        else:
            print(f"FAILURE error={result.error} "
                  f"provider={result.provider_name} time={elapsed:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
