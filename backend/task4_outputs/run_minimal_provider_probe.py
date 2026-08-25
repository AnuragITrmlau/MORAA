"""Task 4 controlled test: invoke the unchanged provider paths with one reference."""

import asyncio
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.ai.image_generation_manager import ImageGenerationManager

PROMPT = (
    "Create a clean Amazon e-commerce main image from this reference.\n"
    "Preserve the exact earring product, including its geometry, material,\n"
    "colour and visible details. Remove only photographic distractions.\n"
    "Do not redesign, replace, simplify or invent any part of the jewellery."
)
REFERENCE = BACKEND_DIR.parent / "Earring Examples" / "ex.jpeg"
OUT_DIR = Path(__file__).resolve().parent


async def run(provider: str) -> dict:
    manager = ImageGenerationManager()
    result = await manager.generate_image(
        prompt=PROMPT,
        context={"request_id": f"task4-minimal-{provider}", "aspect_ratio": "4:5"},
        reference_image=REFERENCE.read_bytes(),
        reference_mime_type="image/jpeg",
        force_provider=provider,
    )
    record = {
        "provider": provider, "success": result.success, "model": result.model_used,
        "error": result.error, "processing_time_seconds": round(result.processing_time, 2),
        "metadata": result.metadata,
    }
    if result.success and result.image_data:
        output = OUT_DIR / f"minimal_ex_{provider}.png"
        output.write_bytes(result.image_data)
        record["output"] = output.name
    return record


async def main() -> None:
    records = [await run(provider) for provider in ("gemini", "openai")]
    (OUT_DIR / "minimal_provider_test_results.json").write_text(
        json.dumps({"reference": str(REFERENCE), "prompt": PROMPT, "results": records}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
