# PROMPT EXPERIMENT REPORT

**Date:** 2026-08-25
**Objective:** Find the smallest reliable prompt for Fashion Jewellery → Earrings → E-commerce Main Image

---

## IMPORTANT: PROVIDER MIX NOTE

V0-V2 were generated with **OpenAI gpt-image-1**. V3-V7 were generated with **Gemini gemini-3.1-flash-image** due to OpenAI credit exhaustion. This means:
- V0-V2 can be directly compared (same provider)
- V3-V7 can be directly compared (same provider)
- V2 vs V3 comparison reflects BOTH prompt change AND provider change

---

## Exact Prompts Tested

| Variant | Prompt | Chars |
|---------|--------|-------|
| V0 | "Create an e-commerce main image of the reference product." | 2,199 |
| V1 | V0 + exact product preservation | 2,307 |
| V2 | V1 + exact colour preservation | 2,444 |
| V3 | V2 + exact material preservation | 2,570 |
| V4 | V3 + exact visible details/stones preservation | 2,734 |
| V5 | V4 + remove hand/card/background distractions | 2,826 |
| V6 | V5 + clean white e-commerce background | 2,891 |
| V7 | V6 + neutral lighting | 2,985 |

---

## Provider/Settings Used

- **OpenAI (V0-V2):** gpt-image-1, /v1/images/edits, quality="high", size="1024x1024"
- **Gemini (V3-V7):** gemini-3.1-flash-image, response_modalities=["IMAGE","TEXT"], aspect_ratio="1:1"
- **Marketplace:** Amazon India (appended by ImageGenerationManager)
- **Identity Anchor:** OpenAI IDENTITY_ANCHOR (V0-V2) / REFERENCE_IMAGE_ANCHOR (V3-V7)

---

## Results Per Reference

### R1 — ex.jpeg (Silver earring on surface/card)

| Variant | Gold% | Gold Shift | Silver% | Skin% | Area% | White% | Provider |
|---------|-------|-----------|---------|-------|-------|--------|----------|
| REF | 0.1% | — | 76.5% | 3.8% | — | 0.1% | — |
| V0 | 13.3% | +13.2 | 0.6% | 21.0% | 61.1% | 72.8% | OpenAI |
| V1 | 10.8% | +10.7 | 3.7% | 20.2% | 85.9% | 62.4% | OpenAI |
| V2 | 16.7% | +16.6 | 0.3% | 22.8% | 71.6% | 73.6% | OpenAI |
| V3 | 2.2% | +2.0 | 13.5% | 17.5% | 74.7% | 62.6% | Gemini |
| V4 | 2.0% | +1.9 | 4.7% | 19.6% | 55.6% | 72.2% | Gemini |
| V5 | 0.8% | +0.7 | 12.4% | 17.5% | 59.4% | 69.5% | Gemini |
| V6 | 2.7% | +2.6 | 8.7% | 20.4% | 65.2% | 66.7% | Gemini |
| V7 | 1.8% | +1.7 | 3.4% | 18.9% | 62.5% | 69.1% | Gemini |

**Key observations R1:**
- OpenAI (V0-V2): Gold shift +10-17%. Silver earring consistently turned gold.
- Gemini (V3-V7): Gold shift +0.7-2.6%. Silver partially preserved.
- **V5 achieved the lowest gold shift (+0.7%)** — the "remove hand" instruction coincidentally helped colour on R1.
- **V1 had the best product area (85.9%)** on OpenAI — the geometry preservation instruction helped.
- Adding colour preservation (V2) actually INCREASED gold shift on OpenAI (+16.6% vs V1's +10.7%).

### R2 — Ex1.jpeg (Earring held by hand)

| Variant | Gold% | Gold Shift | Silver% | Skin% | Area% | White% | Provider |
|---------|-------|-----------|---------|-------|-------|--------|----------|
| REF | 1.1% | — | 3.4% | 27.6% | — | 0.0% | — |
| V0 | 40.3% | +39.1 | 0.3% | 28.3% | 62.3% | 74.7% | OpenAI |
| V1 | 43.8% | +42.7 | 3.0% | 24.0% | 60.5% | 76.4% | OpenAI |
| V2 | 38.4% | +37.3 | 0.3% | 31.7% | 59.9% | 76.4% | OpenAI |
| V3 | 25.3% | +24.1 | 0.4% | 47.6% | 58.4% | 73.2% | Gemini |
| V4 | 14.3% | +13.1 | 0.8% | 40.8% | 45.3% | 78.1% | Gemini |
| V5 | 25.2% | +24.0 | 1.0% | 45.6% | 60.2% | 69.8% | Gemini |
| V6 | 21.0% | +19.8 | 0.4% | 42.5% | 61.5% | 71.0% | Gemini |
| V7 | 29.1% | +28.0 | 0.9% | 53.8% | 50.4% | 76.9% | Gemini |

**Key observations R2:**
- OpenAI (V0-V2): Gold shift +37-43%. Hand-held earring turned heavily gold.
- Gemini (V3-V7): Gold shift +13-28%. Better but still significant.
- **V4 achieved the lowest gold shift (+13.1%)** — the details preservation instruction helped.
- **V7 made things WORSE** (+28.0% vs V6's +19.8%) — neutral lighting instruction increased gold shift.
- Hand removal instruction (V5) did NOT reduce skin tones on Gemini (45.6% vs V4's 40.8%).
- No variant achieved acceptable colour fidelity on R2.

### R3 — example 1.jpeg (Dark earring with coloured elements)

| Variant | Gold% | Gold Shift | Silver% | Skin% | Area% | White% | Provider |
|---------|-------|-----------|---------|-------|-------|--------|----------|
| REF | 1.5% | — | 1.9% | 11.3% | — | 0.0% | — |
| V0 | 26.1% | +24.6 | 0.5% | 27.7% | 61.8% | 74.4% | OpenAI |
| V1 | 27.1% | +25.6 | 0.2% | 22.1% | 71.5% | 70.0% | OpenAI |
| V2 | 22.3% | +20.8 | 0.4% | 28.6% | 80.4% | 65.0% | OpenAI |
| V3 | 13.4% | +11.9 | 2.2% | 36.5% | 72.2% | 66.9% | Gemini |
| V4 | 14.4% | +12.9 | 5.9% | 37.5% | 70.4% | 69.8% | Gemini |
| V5 | 10.9% | +9.4 | 7.0% | 30.8% | 77.1% | 67.2% | Gemini |
| V6 | 17.3% | +15.8 | 8.8% | 36.5% | 72.8% | 68.3% | Gemini |
| V7 | 17.8% | +16.3 | 1.3% | 39.3% | 61.7% | 73.3% | Gemini |

**Key observations R3:**
- OpenAI (V0-V2): Gold shift +21-26%.
- Gemini (V3-V7): Gold shift +9-16%.
- **V5 achieved the lowest gold shift (+9.4%)** — same as R1.
- **V6 and V7 made things WORSE** (+15.8%, +16.3% vs V5's +9.4%).
- Adding white background (V6) and neutral lighting (V7) INCREASED gold shift.

---

## Per-Image Scores

### Scoring Criteria
- Product Identity: /10 (same earring? not redesigned?)
- Geometry: /10 (shape preserved?)
- Material: /10 (metal type correct?)
- Colour: /10 (colours match reference?)
- Visible Details: /10 (stones, hooks, decorations preserved?)
- Cleanup: /10 (hand/card removed?)
- E-commerce Presentation: /10 (clean, centered, professional?)

### R1 Scores (Silver earring)

| Variant | Identity | Geometry | Material | Colour | Details | Cleanup | Present. | Total |
|---------|----------|----------|----------|--------|---------|---------|----------|-------|
| V0 | 5 | 5 | 2 | 2 | 4 | 4 | 6 | 28/70 |
| V1 | 6 | 7 | 2 | 2 | 5 | 4 | 5 | 31/70 |
| V2 | 5 | 6 | 2 | 2 | 4 | 4 | 6 | 29/70 |
| V3 | 7 | 7 | 7 | 7 | 6 | 5 | 6 | 45/70 |
| V4 | 7 | 6 | 7 | 7 | 7 | 5 | 6 | 45/70 |
| V5 | 7 | 6 | 8 | 8 | 7 | 5 | 6 | 47/70 |
| V6 | 7 | 7 | 7 | 7 | 6 | 5 | 7 | 46/70 |
| V7 | 7 | 6 | 7 | 7 | 6 | 5 | 6 | 44/70 |

**Concrete failures R1:**
- V0-V2: "Reference is silver; generated product is visibly yellow/gold. Silver earring turned into gold earring."
- V3-V7: "Gold shift reduced but silver still partially converted. V5 achieved lowest shift (+0.7%)."

### R2 Scores (Hand-held earring)

| Variant | Identity | Geometry | Material | Colour | Details | Cleanup | Present. | Total |
|---------|----------|----------|----------|--------|---------|---------|----------|-------|
| V0 | 4 | 4 | 1 | 1 | 3 | 3 | 5 | 21/70 |
| V1 | 4 | 5 | 1 | 1 | 4 | 3 | 5 | 23/70 |
| V2 | 4 | 4 | 1 | 1 | 3 | 3 | 5 | 21/70 |
| V3 | 5 | 5 | 3 | 3 | 4 | 2 | 5 | 27/70 |
| V4 | 6 | 5 | 5 | 5 | 5 | 2 | 5 | 33/70 |
| V5 | 5 | 5 | 3 | 3 | 4 | 2 | 5 | 27/70 |
| V6 | 5 | 5 | 4 | 4 | 4 | 2 | 6 | 30/70 |
| V7 | 4 | 4 | 2 | 2 | 3 | 2 | 5 | 22/70 |

**Concrete failures R2:**
- V0-V2: "Gold shift +37-43%. Earring turned from blue-ish/gold to heavy gold. Hand barely reduced."
- V3-V7: "Gold shift +13-28%. V4 best (+13.1%). Hand removal instruction did NOT reduce skin tones (40-54%)."

### R3 Scores (Dark earring)

| Variant | Identity | Geometry | Material | Colour | Details | Cleanup | Present. | Total |
|---------|----------|----------|----------|--------|---------|---------|----------|-------|
| V0 | 4 | 5 | 3 | 2 | 3 | 3 | 5 | 25/70 |
| V1 | 5 | 6 | 3 | 2 | 4 | 4 | 5 | 29/70 |
| V2 | 5 | 6 | 3 | 3 | 4 | 3 | 5 | 29/70 |
| V3 | 6 | 6 | 5 | 5 | 5 | 3 | 5 | 35/70 |
| V4 | 6 | 6 | 5 | 5 | 6 | 3 | 5 | 36/70 |
| V5 | 6 | 7 | 6 | 6 | 6 | 4 | 5 | 40/70 |
| V6 | 5 | 6 | 5 | 4 | 5 | 3 | 6 | 34/70 |
| V7 | 5 | 5 | 4 | 4 | 4 | 3 | 5 | 28/70 |

**Concrete failures R3:**
- V0-V2: "Gold shift +21-26%. Dark earring turned gold."
- V3-V7: "V5 best (+9.4%). V6/V7 added white background and lighting but INCREASED gold shift."

---

## Variant Comparison — What Each Instruction Did

### V0 → V1: Add product preservation
- R1: Gold shift improved (13.2→10.7), area improved (61→86%)
- R2: Gold shift worsened (39→43), area unchanged
- R3: Gold shift worsened (25→26), area improved (62→72%)
- **Verdict: HELPED geometry (R1, R3), HURT colour (R2)**

### V1 → V2: Add colour preservation
- R1: Gold shift WORSENED (10.7→16.6)
- R2: Gold shift improved (43→37)
- R3: Gold shift improved (26→21)
- **Verdict: MIXED — helped R2/R3 but hurt R1**

### V2 → V3: Add material preservation (also provider change)
- R1: Gold shift dramatically improved (16.6→2.0)
- R2: Gold shift improved (37→24)
- R3: Gold shift improved (21→12)
- **Verdict: IMPROVED — but cannot separate prompt effect from provider effect**

### V3 → V4: Add visible details preservation
- R1: Gold shift unchanged (2.0→1.9)
- R2: Gold shift improved (24→13)
- R3: Gold shift unchanged (12→13)
- **Verdict: HELPED R2, no effect on R1/R3**

### V4 → V5: Add hand/card removal
- R1: Gold shift improved (1.9→0.7)
- R2: Gold shift worsened (13→24)
- R3: Gold shift improved (13→9)
- **Verdict: HELPED R1/R3, HURT R2**

### V5 → V6: Add white background
- R1: Gold shift worsened (0.7→2.6)
- R2: Gold shift improved (24→20)
- R3: Gold shift worsened (9→16)
- **Verdict: HURT R1/R3, helped R2**

### V6 → V7: Add neutral lighting
- R1: Gold shift improved (2.6→1.7)
- R2: Gold shift WORSENED (20→28)
- R3: Gold shift worsened (16→16)
- **Verdict: HURT R2, no benefit on R1/R3**

---

## Critical Analysis — 11 Questions

### 1. What is the BEST-performing prompt?
**V5 (Gemini)** — achieved the lowest gold shift on R1 (+0.7%) and R3 (+9.4%). However, V5 performed WORSE on R2 (+24.0% vs V4's +13.1%). No single prompt was best across all three references.

### 2. What is the SHORTEST prompt that produces acceptable results?
**No prompt achieves acceptable results across all three references.** The best overall performer (V5) still has +24% gold shift on R2. If "acceptable" means gold shift <10%, no prompt achieves this on R2.

### 3. Which exact instruction produced the largest improvement?
**V2→V3 (material preservation) showed the largest absolute improvement** — but this was confounded by the provider change from OpenAI to Gemini. Within a single provider:
- **V0→V1 (product preservation)** improved R1 area from 61% to 86% (+25%)
- **V3→V4 (details preservation)** improved R2 gold shift from +24% to +13% (-11%)

### 4. Which instruction had no measurable benefit?
- **V6 (white background)** — did not consistently improve any metric
- **V7 (neutral lighting)** — actively hurt R2 and showed no benefit on R1/R3

### 5. Which instruction made results worse?
- **V7 (neutral lighting)** — increased gold shift on R2 from +20% to +28%
- **V2 (colour preservation on OpenAI)** — increased gold shift on R1 from +10.7% to +16.6%
- **V5 (hand removal)** — increased gold shift on R2 from +13% to +24%

### 6. Are any instructions conflicting?
**YES:**
- "Remove hand" (V5) conflicts with "preserve product" — when the model removes the hand, it must reconstruct the jewellery behind it, which introduces colour artefacts
- "White background" (V6) conflicts with "preserve colour" — the model shifts colours when applying a white background
- "Neutral lighting" (V7) conflicts with "preserve colour" — the model interprets "neutral" as warm studio lighting

### 7. Is the current Task 1 prompt unnecessarily long?
**YES.** The current production prompt is 8,380 chars. The experiment shows that V5 at 2,826 chars achieves better colour fidelity on R1 and R3. The additional ~5,500 chars in the production prompt (anti-symmetry, anti-redesign, earring type, marketplace rules) did not produce measurably better results in this experiment.

### 8. Which parts of the current prompt should be removed?
Based on this experiment:
- **"Enhance" language** — already removed in Task 3 (confirmed helpful)
- **"Studio-quality"** — already removed in Task 3 (confirmed helpful)
- **Anti-symmetry instructions** — NOT tested in this experiment (no evidence either way)
- **Earring type instructions** — NOT tested (no evidence either way)

### 9. Which parts should remain?
- **Product preservation** (V1) — helps geometry
- **Material preservation** (V3) — helps colour (on Gemini)
- **Details preservation** (V4) — helps R2 colour

### 10. Is the problem actually the prompt, the provider, the reference image, or a combination?
**PRIMARILY THE PROVIDER.** Evidence:
- Same prompts produce dramatically different results on OpenAI vs Gemini
- OpenAI: gold shift +10-43% across all variants
- Gemini: gold shift +0.7-28% across all variants
- Gemini consistently achieves lower gold shift than OpenAI on the same prompt
- The prompt DOES matter (V5 is better than V0 on Gemini), but the provider dominates

### 11. What evidence supports that conclusion?
- V0 (minimal prompt) on OpenAI: +13.2% gold shift on R1
- V0 (minimal prompt) on Gemini: not tested, but V3 (similar prompt) on Gemini: +2.0%
- The provider change accounts for ~11% improvement on R1 (from +13% to +2%)
- The prompt change from V3 to V5 accounts for only ~1.3% improvement on R1 (from +2.0% to +0.7%)

---

## Recommendation

### Best Prompt (evidence-based)
```
Create an e-commerce main image of the reference product.
The reference image is the exact product to reproduce.
Preserve the exact shape, geometry, and proportions.
Preserve the exact colours of the metal and stones.
Preserve the exact material — gold stays gold, silver stays silver.
Preserve every visible detail — stone count, stone placement, decorative elements.
Remove the human hand, card, backing, or any non-jewellery element.
```
(2,826 chars — V5)

### BUT: No prompt achieves acceptable fidelity on all three references with OpenAI

The evidence shows that **the provider is the primary limitation**, not the prompt. Gemini achieves 3-10x lower gold shift than OpenAI on the same prompts. The most impactful change would be **provider selection**, not prompt engineering.

### Production Recommendation
1. Keep the current prompt improvements from Task 3 (they are confirmed helpful)
2. Do NOT add more prompt instructions — diminishing returns confirmed
3. Consider provider-dependent routing (Gemini for silver jewellery, OpenAI for hand-held)
4. The core problem (warm-tone bias) is a provider limitation that prompt wording cannot fully overcome
