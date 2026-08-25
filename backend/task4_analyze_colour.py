"""Analyse V0-V7 experiment outputs for colour fidelity metrics.

Measures gold%, silver%, skin%, area%, and white% for each output
and compares against reference baselines.

Usage:
    cd backend && python task4_analyze_colour.py
"""

import json
import sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("Install dependencies: pip install Pillow numpy")
    sys.exit(1)

BACKEND_DIR = Path(__file__).resolve().parent
OUT_DIR = BACKEND_DIR / "task4_outputs"

REFERENCES = [
    ("ex.jpeg", "R1"),
    ("Ex1.jpeg", "R2"),
    ("example 1.jpeg", "R3"),
]

VARIANTS = ["V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7"]

REF_DIR = BACKEND_DIR.parent / "Earring Examples"


def classify_pixel_hsv(h: float, s: float, v: float) -> str:
    """Classify a pixel into gold/silver/skin/white/other based on HSV."""
    # White: low saturation, high value
    if s < 0.15 and v > 0.85:
        return "white"
    # Skin: hue in skin range, moderate saturation
    if (5 <= h <= 35) and (0.15 <= s <= 0.65) and (0.3 <= v <= 0.95):
        return "skin"
    # Gold: hue 20-50, moderate-high saturation, moderate-high value
    if (20 <= h <= 50) and (s > 0.25) and (v > 0.4):
        return "gold"
    # Silver: low saturation, moderate-high value (not white)
    if s < 0.15 and v > 0.4:
        return "silver"
    # Dark/metallic
    if v < 0.3:
        return "dark"
    return "other"


def measure_colours(image_path: Path) -> dict:
    """Measure colour distribution in an image."""
    img = Image.open(image_path).convert("RGB")
    # Resize for speed
    img = img.resize((512, 512), Image.LANCZOS)
    arr = np.array(img)

    # Convert to HSV
    from colorsys import rgb_to_hsv
    h, w, _ = arr.shape

    counts = {"gold": 0, "silver": 0, "skin": 0, "white": 0, "dark": 0, "other": 0}
    total = h * w

    # Vectorized approach: process in batches
    for y in range(0, h, 2):  # sample every other pixel
        for x in range(0, w, 2):
            r, g, b = arr[y, x] / 255.0
            hv, sv, vv = rgb_to_hsv(r, g, b)
            hv *= 360  # 0-360 degrees
            category = classify_pixel_hsv(hv, sv, vv)
            counts[category] += 1

    sampled = sum(counts.values())
    result = {}
    for k, v in counts.items():
        result[f"{k}%"] = round(v / sampled * 100, 1)

    return result


def main():
    print("=" * 70)
    print("V0-V7 Colour Fidelity Analysis (Gemini Only)")
    print("=" * 70)

    # Measure reference images
    ref_metrics = {}
    for ref_file, ref_id in REFERENCES:
        ref_path = REF_DIR / ref_file
        if ref_path.exists():
            m = measure_colours(ref_path)
            ref_metrics[ref_id] = m
            print(f"\n{ref_id} ({ref_file}): {m}")

    print("\n" + "=" * 70)

    # Measure variant outputs
    all_results = []
    for ref_file, ref_id in REFERENCES:
        ref_stem = ref_file.replace(".jpeg", "")
        ref_m = ref_metrics.get(ref_id, {})
        ref_gold = ref_m.get("gold%", 0)
        ref_silver = ref_m.get("silver%", 0)

        print(f"\n--- {ref_id} ({ref_file}) ---")
        print(f"{'Var':4s} | {'Gold%':6s} | {'Shift':7s} | {'Silver%':7s} | {'Skin%':6s} | {'White%':7s}")
        print("-" * 55)

        for variant in VARIANTS:
            img_path = OUT_DIR / f"v0v7_{variant}_{ref_stem}.png"
            if not img_path.exists():
                print(f"{variant:4s} | MISSING")
                continue

            m = measure_colours(img_path)
            gold = m.get("gold%", 0)
            silver = m.get("silver%", 0)
            skin = m.get("skin%", 0)
            white = m.get("white%", 0)
            gold_shift = round(gold - ref_gold, 1)
            sign = "+" if gold_shift >= 0 else ""

            print(
                f"{variant:4s} | {gold:5.1f}% | {sign}{gold_shift:5.1f}% | "
                f"{silver:5.1f}% | {skin:5.1f}% | {white:5.1f}%"
            )

            all_results.append({
                "reference": ref_id,
                "variant": variant,
                "gold%": gold,
                "gold_shift": gold_shift,
                "silver%": silver,
                "skin%": skin,
                "white%": white,
                "ref_gold%": ref_gold,
                "ref_silver%": ref_silver,
            })

    # Save results
    results_path = OUT_DIR / "v0v7_colour_analysis.json"
    results_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\nResults saved to {results_path}")

    # Summary: average gold shift per variant
    print("\n" + "=" * 70)
    print("AVERAGE GOLD SHIFT BY VARIANT (all references)")
    print("=" * 70)
    for variant in VARIANTS:
        shifts = [r["gold_shift"] for r in all_results if r["variant"] == variant]
        avg_shift = sum(shifts) / len(shifts) if shifts else 0
        sign = "+" if avg_shift >= 0 else ""
        print(f"  {variant}: {sign}{avg_shift:.1f}%")


if __name__ == "__main__":
    main()
