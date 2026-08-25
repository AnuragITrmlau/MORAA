"""Task 4 — Gemini provider comparison test.

Generates one output for each of the 3 references using Gemini
instead of OpenAI, to determine if the provider is the primary
limitation for colour fidelity.
"""

import asyncio
import base64
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from app.ai.image_generation_manager import ImageGenerationManager
from app.services.earring_ecommerce_prompt import build_earring_ecommerce_prompt

REFERENCES = [
    BACKEND_DIR.parent / "Earring Examples" / "ex.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "Ex1.jpeg",
    BACKEND_DIR.parent / "Earring Examples" / "example 1.jpeg",
]
OUT_DIR = BACKEND_DIR / "task4_outputs"
OUT_DIR.mkdir(exist_ok=True)


async def main() -> None:
    prompt = build_earring_ecommerce_prompt(earring_type=None)
    
    manager = ImageGenerationManager()
    
    # Test Gemini specifically
    for ref in REFERENCES:
        ref_bytes = ref.read_bytes()
        print(f"\n=== {ref.name} (Gemini) ===")
        t0 = time.time()
        result = await manager.generate_image(
            prompt=prompt,
            context={
                "request_id": f"task4-gemini-{ref.stem}",
                "aspect_ratio": "4:5",
            },
            reference_image=ref_bytes,
            reference_mime_type="image/jpeg",
            marketplace="amazon_india_fashion_earrings",
            force_provider="gemini",
        )
        elapsed = time.time() - t0
        if result.success and result.image_url:
            b64 = result.image_url.split(",", 1)[-1]
            out_path = OUT_DIR / f"{ref.stem}_gemini.png"
            out_path.write_bytes(base64.b64decode(b64))
            print(f"SUCCESS provider={result.provider_name} "
                  f"model={result.model_used} time={elapsed:.1f}s")
            print(f"SAVED {out_path}")
        else:
            print(f"FAILURE error={result.error[:100]} "
                  f"provider={result.provider_name} time={elapsed:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
