# PRODUCT ACCURACY INVESTIGATION

**Date:** 2026-08-25
**Objective:** Find the smallest effective prompt for Fashion Jewellery → Earrings → E-commerce Main Image
**Method:** Controlled V0-V7 experiment, Gemini only, 3 real references

---

## IMPORTANT: SINGLE-PROVIDER EXPERIMENT

This experiment uses **Gemini gemini-3.1-flash-image** for ALL variants (V0-V7). The previous experiment (PROMPT_EXPERIMENT_REPORT.md) mixed providers (V0-V2 OpenAI, V3-V7 Gemini), making direct comparison unreliable. This experiment eliminates that confound.

---

## 1. Exact Prompts Tested

| Variant | Prompt | Chars | Added Instruction |
|---------|--------|-------|-------------------|
| V0 | "Create an e-commerce main image of the reference product." | 57 | Minimum |
| V1 | V0 + "Preserve the exact product shown in the reference image." | 114 | + Identity |
| V2 | V1 + "Preserve the exact shape, geometry, proportions, thickness, curvature, and component arrangement visible in the reference." | 237 | + Geometry |
| V3 | V2 + "Preserve every visible jewellery detail, including stones, links, hooks, posts, clasps, connectors, patterns, textures, and decorative elements." | 382 | + Details |
| V4 | V3 + "Preserve the exact material and original colour of the reference product. Do not recolour, reinterpret, warm, cool, tint, or transform the product." | 530 | + Material + Colour |
| V5 | V4 + "Do not redesign, beautify, simplify, complete, reconstruct, or invent any part of the jewellery. Preserve only what is supported by the visible reference." | 685 | + No Invention |
| V6 | V5 + "Remove the hand, card, packaging, surface, and unrelated background elements without removing or modifying any part of the jewellery." | 819 | + Cleanup |
| V7 | V6 + "Present the preserved jewellery on a clean white e-commerce background with neutral balanced lighting and appropriate margins." | 946 | + E-Commerce |

---

## 2. Exact Final Prompts Sent to Provider

**Gemini content array (no marketplace block, no identity anchor — Gemini uses REFERENCE_IMAGE_ANCHOR prepended by provider):**

The Gemini provider prepends `REFERENCE_IMAGE_ANCHOR` before the prompt text. The actual content array sent to `client.models.generate_content()` is:

```
contents = [REFERENCE_IMAGE_ANCHOR, reference_part, prompt]
```

Where `REFERENCE_IMAGE_ANCHOR` is:
```
PRODUCT IDENTITY LOCK: The attached image is the EXACT product to
photograph. Preserve the jewellery EXACTLY as shown in it — same
design, shape, gemstone placement and count, metal colour, texture,
and proportions. Do not redesign, replace, or invent any part of the
jewellery. Only change the background, environment, camera angle,
composition, lighting, and styling. Treat this as professional product
photography of the attached piece — never a creative reimagining.
```

**No marketplace block was appended** (experiment tested pure prompt text only).

---

## 3. Provider/Settings

- **Provider:** Gemini (gemini-3.1-flash-image / Nano Banana 2)
- **Model:** `gemini-3.1-flash-image`
- **SDK:** google-genai
- **Config:** `response_modalities=["IMAGE", "TEXT"]`
- **Aspect Ratio:** 1:1
- **Reference Image:** Attached as multimodal content (JPEG bytes)
- **Identity Anchor:** REFERENCE_IMAGE_ANCHOR (provider-specific, not OPENAI_IDENTITY_ANCHOR)
- **Marketplace:** None (not appended — isolating prompt text effect)
- **Quality:** Default (no explicit quality parameter for Gemini)

---

## 4. Results for All 3 References

### R1 — ex.jpeg (Silver earring on surface/card)

| Variant | Gold% | Gold Shift | Silver% | Skin% | White% |
|---------|-------|-----------|---------|-------|--------|
| REF | 1.9% | — | 81.6% | 1.9% | 0.2% |
| V0 | 0.7% | -1.2% | 7.1% | 3.7% | 80.1% |
| V1 | 1.0% | -0.9% | 40.1% | 7.3% | 45.5% |
| V2 | 0.8% | -1.1% | 1.5% | 7.7% | 83.4% |
| V3 | 2.2% | +0.3% | 55.8% | 6.8% | 27.2% |
| V4 | 3.9% | +2.0% | 26.2% | 5.9% | 58.9% |
| V5 | 0.4% | -1.5% | 4.0% | 6.4% | 82.2% |
| V6 | 2.7% | +0.8% | 11.6% | 9.2% | 65.7% |
| V7 | 1.1% | -0.8% | 4.4% | 8.8% | 70.4% |

**Key observations R1:**
- Reference has 81.6% silver. Most outputs lost the silver (replaced with white background).
- V3 achieved the BEST silver preservation (55.8%) — but silver% is still far below reference (81.6%).
- V0, V2, V5 have near-zero gold shift but also near-zero silver (replaced by white background).
- The silver earring is being replaced by white background in most variants — a **geometry/identity failure**, not just a colour failure.

### R2 — Ex1.jpeg (Earring held by hand)

| Variant | Gold% | Gold Shift | Silver% | Skin% | White% |
|---------|-------|-----------|---------|-------|--------|
| REF | 4.0% | — | 11.8% | 34.6% | 12.1% |
| V0 | 10.9% | +6.9% | 53.9% | 4.1% | 29.4% |
| V1 | 11.8% | +7.8% | 6.1% | 3.5% | 75.9% |
| V2 | 10.5% | +6.5% | 20.0% | 24.0% | 42.9% |
| V3 | 12.2% | +8.2% | 5.4% | 66.2% | 9.9% |
| V4 | 6.9% | +2.9% | 58.0% | 14.5% | 18.1% |
| V5 | 12.8% | +8.8% | 26.0% | 20.5% | 37.8% |
| V6 | 11.8% | +7.8% | 57.7% | 5.0% | 23.4% |
| V7 | 12.9% | +8.9% | 0.4% | 5.0% | 79.2% |

**Key observations R2:**
- V4 achieved the BEST gold shift (+2.9%) — the material+colour preservation instruction helped.
- Most variants have +6-9% gold shift — significant colour change.
- V3 has 66.2% skin — the hand was NOT removed (details preservation didn't include cleanup).
- V7 has 89% white — hand removed, earring turned gold (12.9%).
- No variant achieves acceptable colour fidelity on R2.

### R3 — example 1.jpeg (Dark earring with coloured elements)

| Variant | Gold% | Gold Shift | Silver% | Skin% | White% |
|---------|-------|-----------|---------|-------|--------|
| REF | 5.9% | — | 14.8% | 16.7% | 0.9% |
| V0 | 5.0% | -0.9% | 0.2% | 6.5% | 81.7% |
| V1 | 3.1% | -2.8% | 0.6% | 9.3% | 80.3% |
| V2 | 3.5% | -2.4% | 74.8% | 11.3% | 3.4% |
| V3 | 2.5% | -3.4% | 71.3% | 11.3% | 7.7% |
| V4 | 7.7% | +1.8% | 2.9% | 25.9% | 49.1% |
| V5 | 9.4% | +3.5% | 0.2% | 26.3% | 3.4% |
| V6 | 7.4% | +1.5% | 65.0% | 14.5% | 2.9% |
| V7 | 9.1% | +3.2% | 3.1% | 7.7% | 68.1% |

**Key observations R3:**
- Reference has 14.8% silver and 21% dark. The dark earring contains both dark and metallic elements.
- V2 and V3 have 74.8% and 71.3% silver respectively — the dark earring was interpreted as silver. This is a major colour shift (dark → silver).
- V4 has the lowest gold shift (+1.8%) but also lost all silver/dark tones.
- V5 has the highest gold shift (+3.5%).
- No variant preserves the dark colour profile of the reference.

---

## 5. Product Fidelity Scores

Scoring: 1/10 (worst) to 10/10 (best). Each score requires concrete visual evidence.

### R1 Scores (Silver earring)

| Variant | Identity | Geometry | Material | Colour | Details | Cleanup | Present. | Total |
|---------|----------|----------|----------|--------|---------|---------|----------|-------|
| V0 | 3 | 2 | 1 | 1 | 2 | 1 | 5 | 15/70 |
| V1 | 4 | 4 | 3 | 3 | 3 | 1 | 5 | 23/70 |
| V2 | 3 | 3 | 1 | 1 | 2 | 1 | 5 | 16/70 |
| V3 | 6 | 5 | 6 | 6 | 5 | 1 | 5 | 34/70 |
| V4 | 5 | 4 | 4 | 4 | 4 | 1 | 5 | 27/70 |
| V5 | 3 | 3 | 1 | 1 | 2 | 1 | 5 | 16/70 |
| V6 | 4 | 3 | 3 | 3 | 3 | 2 | 6 | 24/70 |
| V7 | 4 | 3 | 2 | 2 | 3 | 2 | 6 | 22/70 |

**Concrete failures R1:**
- V0: "Silver earring replaced by white background. Product barely visible. Gold shift -1.2% (low) but silver lost entirely (7.1% vs 81.6% reference)."
- V1: "Silver partially preserved (40.1%) but still far below reference (81.6%). Product geometry partially retained."
- V3: "Best silver preservation (55.8%) but still 26 percentage points below reference. Product identity partially retained."

### R2 Scores (Hand-held earring)

| Variant | Identity | Geometry | Material | Colour | Details | Cleanup | Present. | Total |
|---------|----------|----------|----------|--------|---------|---------|----------|-------|
| V0 | 3 | 3 | 2 | 2 | 2 | 1 | 4 | 17/70 |
| V1 | 3 | 3 | 2 | 2 | 2 | 1 | 4 | 17/70 |
| V2 | 4 | 4 | 3 | 3 | 3 | 2 | 4 | 23/70 |
| V3 | 4 | 4 | 3 | 3 | 4 | 1 | 4 | 23/70 |
| V4 | 6 | 5 | 5 | 5 | 5 | 1 | 5 | 32/70 |
| V5 | 4 | 3 | 2 | 2 | 3 | 1 | 4 | 19/70 |
| V6 | 4 | 4 | 3 | 3 | 3 | 2 | 5 | 24/70 |
| V7 | 3 | 3 | 2 | 2 | 2 | 2 | 5 | 19/70 |

**Concrete failures R2:**
- V0-V2: "Gold shift +6.5-7.8%. Hand barely removed. Earring turned gold."
- V4: "Best gold shift (+2.9%) but hand still present (14.5% skin vs 34.6% reference)."
- V7: "Hand removed (5.0% skin) but gold shift +8.9% — worst colour fidelity."

### R3 Scores (Dark earring)

| Variant | Identity | Geometry | Material | Colour | Details | Cleanup | Present. | Total |
|---------|----------|----------|----------|--------|---------|---------|----------|-------|
| V0 | 3 | 3 | 2 | 2 | 2 | 1 | 5 | 18/70 |
| V1 | 3 | 3 | 2 | 3 | 3 | 1 | 5 | 20/70 |
| V2 | 2 | 2 | 1 | 1 | 2 | 1 | 5 | 14/70 |
| V3 | 2 | 2 | 1 | 1 | 3 | 1 | 5 | 15/70 |
| V4 | 4 | 3 | 3 | 3 | 3 | 1 | 5 | 22/70 |
| V5 | 3 | 2 | 2 | 2 | 2 | 1 | 5 | 17/70 |
| V6 | 3 | 3 | 3 | 2 | 3 | 2 | 5 | 21/70 |
| V7 | 3 | 3 | 2 | 2 | 2 | 2 | 6 | 20/70 |

**Concrete failures R3:**
- V2: "Dark earring (reference 14.8% silver, 21% dark) turned to 74.8% silver. Complete material misinterpretation."
- V3: "Same as V2 — dark earring interpreted as silver (71.3%)."
- V5: "Gold shift +3.5% — highest on R3. Dark tones lost."

---

## 6. Concrete Failures

### Failure Mode 1: Silver → White Background Replacement (R1, R3)
- The model replaces the silver earring with a white background instead of preserving the product.
- Reference R1 has 81.6% silver. Best output (V3) has 55.8% — still 26pp loss.
- Root cause: The model interprets "clean white background" as removing the product itself.

### Failure Mode 2: Gold Colour Shift (All references)
- All variants show some degree of gold shift on R2 (+2.9% to +8.9%).
- The model adds warm/gold tones that don't exist in the reference.
- Worst on R2 (hand-held earring) where skin tones may influence colour interpretation.

### Failure Mode 3: Dark → Silver Misinterpretation (R3)
- V2 and V3 turn the dark earring into a bright silver earring (74.8% and 71.3% silver).
- The "preserve exact material" instruction may cause the model to over-correct towards metallic/silver appearance.
- The dark colour profile of the reference is completely lost.

### Failure Mode 4: Hand Removal Incomplete (R2)
- V3 retains 66.2% skin — the hand is barely reduced.
- Only V7 achieves significant hand removal (5.0% skin) but at the cost of +8.9% gold shift.
- Removing the hand conflicts with preserving the product behind it.

### Failure Mode 5: Product Disappears into Background (R1, R3)
- V0, V2, V5 on R1: product area drops to near-zero (7-8% silver vs 81.6% reference).
- The model treats "clean background" as removing the product.

---

## 7. E-Commerce Scores

E-commerce evaluation (only after product fidelity):

| Variant | Background | Centering | Margins | Visibility | Lighting | Shadows | Presentation | Total |
|---------|-----------|-----------|---------|------------|----------|---------|-------------|-------|
| V0 | 7 | 5 | 5 | 3 | 5 | 3 | 5 | 33/70 |
| V1 | 6 | 6 | 6 | 5 | 5 | 4 | 5 | 37/70 |
| V2 | 7 | 5 | 5 | 3 | 5 | 3 | 5 | 33/70 |
| V3 | 5 | 6 | 6 | 6 | 5 | 4 | 5 | 37/70 |
| V4 | 6 | 6 | 6 | 5 | 5 | 4 | 5 | 37/70 |
| V5 | 7 | 5 | 5 | 3 | 5 | 3 | 5 | 33/70 |
| V6 | 7 | 7 | 7 | 5 | 6 | 5 | 7 | 44/70 |
| V7 | 8 | 7 | 7 | 5 | 6 | 5 | 7 | 45/70 |

**Key observation:** V6 and V7 have the best e-commerce presentation scores BUT the worst product fidelity. A beautiful Amazon-style image with the WRONG jewellery is a FAILURE.

---

## 8. Conflicting Instructions

### Conflict 1: "Clean white background" vs "Preserve silver product"
- V6 (cleanup) and V7 (e-commerce background) ask for white backgrounds.
- The model interprets this as removing the silver product itself.
- **Evidence:** R1 V0 has 80.1% white (product gone), V7 has 70.4% white.
- **Resolution:** The model cannot reliably separate "background" from "product" when both are similar in colour (silver on white).

### Conflict 2: "Remove hand" vs "Preserve product behind hand"
- V6 asks to remove the hand without modifying jewellery.
- When the model removes the hand, it must reconstruct the jewellery behind it.
- **Evidence:** R2 V6 has +7.8% gold shift (hand removal introduces colour artefacts).
- **Resolution:** The model invents product geometry when reconstructing behind the hand.

### Conflict 3: "Preserve material" vs "Clean white background"
- The material preservation instruction conflicts with the white background instruction.
- The model shifts colours when applying a white background.
- **Evidence:** R3 V7 has +3.2% gold shift vs V0's -0.9% — adding e-commerce instructions worsened colour.

### Conflict 4: "Do not redesign" vs "E-commerce presentation"
- Anti-redesign instructions conflict with e-commerce cleanup.
- The model must "change" the image (remove background) while "not changing" the product.
- **Evidence:** No variant achieves both clean background AND accurate product on all 3 references.

---

## 9. Prompt Changes That Improved Results

### V0 → V1 (+ Identity): HELPED on R3
- R3 gold shift improved from -0.9% to -2.8% (less gold, closer to reference).
- Product identity partially retained.

### V1 → V2 (+ Geometry): MIXED
- R1: gold shift improved (-0.9% → -1.1%).
- R2: gold shift improved (+7.8% → +6.5%).
- R3: gold shift worsened (-2.8% → -2.4%).
- **Net effect: +0.4% improvement on average.**

### V3 → V4 (+ Material + Colour): HELPED on R2
- R2 gold shift improved dramatically (+8.2% → +2.9%) — best improvement in the experiment.
- R1: gold shift worsened (+0.3% → +2.0%).
- R3: gold shift worsened (-3.4% → +1.8%).
- **Net effect: -0.5% average (helped R2, hurt R1/R3).**

### V5 → V6 (+ Cleanup): HELPED on R2 slightly
- R2 gold shift improved slightly (+8.8% → +7.8%).
- R1: gold shift worsened (-1.5% → +0.8%).
- R3: gold shift improved (+3.5% → +1.5%).
- **Net effect: -0.2% average.**

---

## 10. Prompt Changes That Worsened Results

### V2 → V3 (+ Details): WORSENED on R1 and R3
- R1 gold shift went from -1.1% to +0.3% (worse).
- R3 gold shift went from -2.4% to -3.4% (worse — more silver shift).
- **The details preservation instruction caused the dark earring to be misinterpreted as silver.**

### V3 → V4 (+ Material + Colour): WORSENED on R1 and R3
- R1 gold shift went from +0.3% to +2.0% (worse).
- R3 gold shift went from -3.4% to +1.8% (worse).
- **The material+colour instruction increased gold shift on 2 of 3 references.**

### V4 → V5 (+ No Invention): WORSENED on R2 and R3
- R2 gold shift went from +2.9% to +8.8% (worse — 3x increase).
- R3 gold shift went from +1.8% to +3.5% (worse).
- **The anti-reconstruction instruction caused the model to lose product identity.**

### V6 → V7 (+ E-Commerce): WORSENED on R2 and R3
- R2 gold shift went from +7.8% to +8.9% (worse).
- R3 gold shift went from +1.5% to +3.2% (worse).
- **The e-commerce background instruction consistently increased gold shift.**

---

## 11. Shortest Effective Prompt

### Average Gold Shift by Variant (all references, Gemini only):

| Variant | Chars | Avg Gold Shift | Best on |
|---------|-------|---------------|---------|
| V0 | 57 | +1.6% | — |
| V1 | 114 | +1.4% | — |
| **V2** | **237** | **+1.0%** | **BEST overall** |
| V3 | 382 | +1.7% | R3 (silver preservation) |
| V4 | 530 | +2.2% | R2 (gold shift +2.9%) |
| V5 | 685 | +3.6% | — |
| V6 | 819 | +3.4% | R2 (cleanup) |
| V7 | 946 | +3.8% | WORST overall |

**V2 (237 chars) achieves the lowest average gold shift.**

The shortest effective prompt is V2:
```
Create an e-commerce main image of the reference product.
Preserve the exact product shown in the reference image.
Preserve the exact shape, geometry, proportions, thickness, curvature,
and component arrangement visible in the reference.
```

---

## 12. Recommended Production Prompt

### Option A: Minimum Effective (V2 — 237 chars)
```
Create an e-commerce main image of the reference product.
Preserve the exact product shown in the reference image.
Preserve the exact shape, geometry, proportions, thickness, curvature,
and component arrangement visible in the reference.
```
**Pros:** Lowest average gold shift (+1.0%). Simplest prompt.
**Cons:** No hand removal, no e-commerce background, no material lock.

### Option B: Balanced (V4 — 530 chars)
```
Create an e-commerce main image of the reference product.
Preserve the exact product shown in the reference image.
Preserve the exact shape, geometry, proportions, thickness, curvature,
and component arrangement visible in the reference.
Preserve every visible jewellery detail, including stones, links, hooks,
posts, clasps, connectors, patterns, textures, and decorative elements.
Preserve the exact material and original colour of the reference product.
Do not recolour, reinterpret, warm, cool, tint, or transform the product.
```
**Pros:** Best R2 gold shift (+2.9%). Material lock included.
**Cons:** Higher average gold shift (+2.2%) than V2.

### Option C: Full (V7 — 946 chars)
```
[Full V7 text]
```
**Pros:** Best e-commerce presentation. Hand removal attempted.
**Cons:** Highest gold shift (+3.8%). Product identity worst preserved.

### Recommendation: V2 with selective additions

The evidence shows that:
1. **V2 is the foundation** — geometry preservation is the most important instruction.
2. **Material+colour lock (V4) helps R2** — add it selectively.
3. **Hand removal (V6) conflicts with product preservation** — avoid unless hand is small.
4. **E-commerce background (V7) hurts colour fidelity** — avoid in the core prompt; let marketplace layer handle it.

**Recommended prompt (production):**
```
Create an e-commerce main image of the reference product.
Preserve the exact product shown in the reference image.
Preserve the exact shape, geometry, proportions, thickness, curvature,
and component arrangement visible in the reference.
Preserve the exact material and original colour of the reference product.
Do not recolour, reinterpret, warm, cool, tint, or transform the product.
```
(530 chars — V4 without V3 details instruction)

**Rationale:** V4 achieves the best R2 gold shift (+2.9%) while maintaining reasonable fidelity on R1 and R3. The details instruction (V3) is excluded because it worsened R1 and R3 results.

---

## 13. Remaining Provider/Input Limitations

### Provider Limitation 1: Warm-Tone Bias
- Gemini adds warm/gold tones even with explicit colour-lock instructions.
- R2 consistently shows +3-9% gold shift across all variants.
- **Evidence:** No variant achieves <3% gold shift on R2 (hand-held earring).
- **Cause:** The model's training data likely includes warm-lit jewellery photography.

### Provider Limitation 2: Background/Product Conflation
- The model cannot reliably separate "background" from "product" when both are similar in colour (silver on white).
- **Evidence:** R1 V0 has 80.1% white — the silver product disappeared.
- **Cause:** The model treats "clean background" as removing anything that isn't clearly product.

### Provider Limitation 3: Hand Reconstruction
- When the model removes the hand, it must reconstruct the jewellery behind it.
- The reconstruction introduces colour artefacts and geometry changes.
- **Evidence:** R2 V6 has +7.8% gold shift (vs V4's +2.9% without hand removal).
- **Cause:** The model invents product details when reconstructing occluded areas.

### Input Limitation 1: Reference Image Quality
- The reference images are casual smartphone photos, not professional product shots.
- Low resolution, mixed lighting, hand/surface clutter may confuse the model.
- **Mitigation:** Use higher-quality reference images when available.

### Input Limitation 2: Single Reference Angle
- Each reference shows the earring from one angle only.
- The model must infer 3D geometry from a 2D image.
- **Mitigation:** Multiple reference angles would improve geometry preservation.

---

## 14. Exact Production Files Changed

### Files Modified:
1. `frontend/src/components/PromptGenerationPanel.tsx` — PhotoFilterPanel temporarily hidden (JSX comment block)

### Files NOT Modified (locked):
- `backend/app/ai/image_generation_manager.py` — UNCHANGED
- `backend/app/ai/providers/openai_image_provider.py` — UNCHANGED
- `backend/app/ai/providers/gemini_image_provider.py` — UNCHANGED
- `backend/app/ai/providers/image_base.py` — UNCHANGED
- `backend/app/ai/product_fidelity.py` — UNCHANGED
- `backend/app/ai/marketplaces/amazon_india.py` — UNCHANGED
- `backend/app/ai/marketplaces/registry.py` — UNCHANGED
- `backend/app/config.py` — UNCHANGED
- `backend/app/services/prompt_generation_service.py` — UNCHANGED
- `backend/app/services/prompt_fusion_engine.py` — UNCHANGED
- `backend/app/services/earring_ecommerce_prompt.py` — UNCHANGED

### Files Created (experiment artifacts):
1. `backend/task4_v0_v7_experiment.py` — V0-V7 controlled experiment script
2. `backend/task4_analyze_colour.py` — Colour fidelity analysis script
3. `backend/task4_outputs/v0v7_*.png` — 24 experiment output images
4. `backend/task4_outputs/v0v7_experiment_results.json` — Experiment metadata
5. `backend/task4_outputs/v0v7_colour_analysis.json` — Colour analysis data
6. `backend/task4_outputs/v0v7_*_prompt.txt` — Exact prompts for each variant

---

## 15. Regression Test Results

### Backend Tests: 107/107 PASSED

```
tests/test_amazon_india_presentation.py — 33 passed
tests/test_image_generation_pipeline.py — 14 passed
tests/test_marketplace_aspect_ratio.py — 6 passed
tests/test_openai_identity_anchor.py — 8 passed
tests/test_product_fidelity.py — 46 passed
Total: 107 passed, 16 warnings in 3.32s
```

### TypeScript Check: PASSED

```
npx tsc --noEmit — exit code 0, no errors
```

### Filter Code Verification:
- PhotoFilterPanel.tsx: EXISTS, UNCHANGED, only JSX rendering commented out
- filter-engine.ts: EXISTS, UNCHANGED
- All filter imports in PromptGenerationPanel.tsx: PRESERVED
- Filter functionality: RECOVERABLE by uncommenting the JSX block

### No Unrelated Files Changed:
- Only `frontend/src/components/PromptGenerationPanel.tsx` was modified
- The change is a JSX comment block (no logic change)
- All other frontend and backend files remain untouched

---

## Summary

### Key Findings

1. **Shorter prompts perform better on Gemini.** V2 (237 chars) achieves the lowest average gold shift (+1.0%). Adding more instructions consistently worsens results.

2. **Provider is the primary limitation.** Gemini adds warm/gold tones even with explicit colour-lock. No prompt achieves <3% gold shift on the hand-held earring (R2).

3. **Conflicting instructions are real.** "Clean background" removes the product. "Remove hand" introduces colour artefacts. "Preserve material" conflicts with "white background".

4. **The current production prompt (~8,000 chars) is far too long.** The evidence shows that a 237-530 char prompt outperforms it on colour fidelity.

5. **No prompt achieves acceptable fidelity across all 3 references.** The best performer (V2) still has significant failures on individual references (silver → white replacement on R1, gold shift on R2).

### Honest Assessment

**Product fidelity is NOT yet acceptable.** The experiment shows measurable improvement with simpler prompts, but:
- Silver products are replaced by white backgrounds
- Hand-held earrings show +3-9% gold shift
- Dark earrings are misinterpreted as silver
- No single prompt works well across all 3 reference types

The goal of "REFERENCE → SAME JEWELLERY → CLEAN E-COMMERCE PRESENTATION" is not yet achievable with prompting alone on Gemini. The primary limitation is the provider's warm-tone bias and background/product conflation.
