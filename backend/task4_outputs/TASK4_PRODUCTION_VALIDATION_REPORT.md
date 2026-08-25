# TASK 4 — PRODUCTION RE-VALIDATION AFTER PROMPT FIXES

**Date:** 2026-08-25
**Tester:** Buffy (Codebuff Agent)
**Pipeline:** build_earring_ecommerce_prompt → /api/generate-image → ImageGenerationManager → OpenAI gpt-image-1

---

## 1. Executive Verdict

# **C. PARTIAL IMPROVEMENT**

The prompt fixes materially improved ONE of three test cases (R2) but did NOT improve R1 and showed no meaningful improvement on R3. The core problem — OpenAI gpt-image-1's warm-tone bias on jewellery — remains unresolved for the majority of test cases.

---

## 2. Production Pipeline Used

```
build_earring_ecommerce_prompt(earring_type=None)  [8,380 chars]
  → /api/generate-image
  → ImageGenerationManager
  → REFERENCE_PRIORITY_BLOCK skipped (marker present)
  → Amazon India marketplace block appended
  → aspect_ratio overridden to 1:1
  → OpenAI IDENTITY_ANCHOR prepended
  → OpenAI gpt-image-1 /v1/images/edits (reference-aware)
  → quality="high", size="1024x1024"
```

---

## 3. Reference Images Tested

| Ref | File | Dimensions | Content |
|-----|------|-----------|---------|
| R1 | ex.jpeg | 1200×1600 | Silver earring on surface/card |
| R2 | Ex1.jpeg | 960×1280 | Earring held by hand |
| R3 | example 1.jpeg | 960×1280 | Dark earring with coloured elements |

---

## 4. Task 2 vs Task 4 Scores

### Colour Shift (Gold % change from reference)

| Test | Reference | Task 2 | Task 4 | Change | Status |
|------|-----------|--------|--------|--------|--------|
| R1 (ex) | 0.1% | 6.5% (+6.4) | 8.8% (+8.7) | **+2.3% worse** | REGRESSED |
| R2 (Ex1) | 1.1% | 37.2% (+36.1) | 22.1% (+21.0) | **-15.1% better** | IMPROVED |
| R3 (example1) | 1.5% | 21.4% (+19.9) | 23.0% (+21.5) | **+1.5% worse** | UNCHANGED |

### Silver Preservation (% of product area)

| Test | Reference | Task 2 | Task 4 | Change | Status |
|------|-----------|--------|--------|--------|--------|
| R1 (ex) | 76.5% | 15.4% | 17.2% | +1.8% | UNCHANGED |
| R2 (Ex1) | 3.4% | 0.7% | 25.3% | **+24.6%** | IMPROVED |
| R3 (example1) | 1.9% | 0.4% | 1.5% | +1.1% | UNCHANGED |

### Skin/Hand Tones (% of product area)

| Test | Reference | Task 2 | Task 4 | Change | Status |
|------|-----------|--------|--------|--------|--------|
| R1 (ex) | 3.8% | 19.0% | 18.7% | -0.3% | UNCHANGED |
| R2 (Ex1) | 27.6% | 32.4% | 19.3% | **-13.1%** | IMPROVED |
| R3 (example1) | 11.3% | 22.0% | 21.1% | -0.9% | UNCHANGED |

### Product Area (% of frame)

| Test | Task 2 | Task 4 | Change | Amazon Target |
|------|--------|--------|--------|---------------|
| R1 (ex) | 70.1% | 64.1% | -6.0% | 85% |
| R2 (Ex1) | 59.4% | 71.9% | **+12.5%** | 85% |
| R3 (example1) | 68.7% | 67.8% | -0.9% | 85% |

---

## 5. Visual Fidelity Inspection

### R1 — ex.jpeg (Silver earring on surface/card)

**A. Is it clearly the SAME jewellery product?**
PARTIAL — The overall earring shape is similar but the model has interpreted the silver earring as having warmer tones. The output looks like a "similar" earring rather than the exact same one.

**B-G. Geometry/stone/connector changes?**
Cannot fully verify individual stone details at 1024×1024. The overall silhouette appears preserved but the material colour is wrong.

**H. Did silver remain silver?**
NO — Silver reference (76.5%) → Output has only 17.2% silver tones. Gold tones increased from 0.1% to 8.8%.

**I. Coloured stones?**
Not confidently identifiable at this resolution.

**J. Asymmetry preserved?**
Partially — the output shows some asymmetry but the reference's specific asymmetric details are not clearly reproduced.

**K. Hand removed?**
N/A — R1 reference has no hand, only a surface/card. Card appears removed.

**L. Card/backing removed?**
YES — the surface/card from the reference is replaced with white background.

**M. Product shape preserved?**
PARTIAL — overall shape similar but material colour shifted.

**N. Model beautified/redesigned?**
PARTIAL — the warm-tone shift could be considered a form of "beautification" (making the earring look warmer/more golden).

**O. Suitable as e-commerce main image?**
PARTIAL — clean background and centering are good, but the material colour is wrong for a silver earring.

### R2 — Ex1.jpeg (Earring held by hand)

**A. Is it clearly the SAME jewellery product?**
YES — the earring shape, structure, and overall design appear to match the reference much better than Task 2.

**B-G. Geometry/stone/connector changes?**
The overall earring geometry appears preserved. The gold tones in the output are more consistent with what the earring likely IS (gold earring on blue background in reference).

**H. Did silver/gold remain correct?**
MUCH IMPROVED — Task 2 had 37.2% gold (vs 1.1% reference), Task 4 has 22.1% gold. While still elevated, the improvement is significant. The reference's blue-ish tones may have been background, not the earring itself.

**I. Coloured stones?**
Not confidently identifiable at this resolution.

**J. Asymmetry preserved?**
YES — the output shows appropriate asymmetry consistent with the reference.

**K. Hand removed?**
SIGNIFICANTLY IMPROVED — skin tones dropped from 32.4% to 19.3%. The hand is substantially removed.

**L. Card/backing removed?**
N/A — R2 reference has no card.

**M. Product shape preserved?**
YES — the earring geometry appears faithful to the reference.

**N. Model beautified/redesigned?**
MINIMAL — the output looks like a clean version of the reference earring.

**O. Suitable as e-commerce main image?**
YES — clean white background, good product occupancy (71.9%), hand removed, earring clearly visible.

### R3 — example 1.jpeg (Dark earring with coloured elements)

**A. Is it clearly the SAME jewellery product?**
PARTIAL — the dark earring structure is present but the specific details are hard to verify.

**B-G. Geometry/stone/connector changes?**
The overall darker tones are partially preserved. Green and red elements are visible in the output.

**H. Did materials remain correct?**
PARTIAL — gold shift is +21.5% (similar to Task 2's +19.9%). The prompt fix did not help here.

**I. Coloured stones?**
Partially preserved — green and red tones visible.

**J. Asymmetry preserved?**
Partially — the output shows some asymmetry.

**K. Hand removed?**
PARTIAL — skin tones dropped slightly from 22.0% to 21.1%.

**L. Card/backing removed?**
N/A — R3 reference has minimal card.

**M. Product shape preserved?**
PARTIAL — overall shape similar.

**N. Model beautified/redesigned?**
PARTIAL — some warm-tone shift present.

**O. Suitable as e-commerce main image?**
PARTIAL — clean background but material colour is not fully accurate.

---

## 6. Colour Shift Analysis

### R1: Previous → New → Assessment

| Metric | Task 2 | Task 4 | Change |
|--------|--------|--------|--------|
| Gold shift | +6.4% | +8.7% | **+2.3% WORSE** |
| Silver | 15.4% | 17.2% | +1.8% (marginal) |
| Skin | 19.0% | 18.7% | -0.3% (unchanged) |
| **Verdict** | | | **REGRESSED** |

### R2: Previous → New → Assessment

| Metric | Task 2 | Task 4 | Change |
|--------|--------|--------|--------|
| Gold shift | +36.1% | +21.0% | **-15.1% BETTER** |
| Silver | 0.7% | 25.3% | **+24.6% BETTER** |
| Skin | 32.4% | 19.3% | **-13.1% BETTER** |
| **Verdict** | | | **IMPROVED** |

### R3: Previous → New → Assessment

| Metric | Task 2 | Task 4 | Change |
|--------|--------|--------|--------|
| Gold shift | +19.9% | +21.5% | +1.5% (unchanged) |
| Silver | 0.4% | 1.5% | +1.1% (marginal) |
| Skin | 22.0% | 21.1% | -0.9% (unchanged) |
| **Verdict** | | | **UNCHANGED** |

---

## 7. Product Identity Analysis

| Reference | Identity Result | Major Changes | Severity |
|-----------|-----------------|---------------|----------|
| R1 (ex) | **PARTIAL** | Silver→gold colour shift, warm-tone bias | HIGH — wrong material colour |
| R2 (Ex1) | **PASS** | Hand removed, earring geometry preserved, gold tones present | LOW — good fidelity |
| R3 (example1) | **PARTIAL** | Dark tones partially preserved, gold shift present | MEDIUM — material colour shifted |

---

## 8. Hand/Card/Background Cleanup

| Test | Task 2 Skin% | Task 4 Skin% | Improvement | Hand Fully Removed? |
|------|-------------|-------------|-------------|---------------------|
| R1 (ex) | 19.0% | 18.7% | -0.3% | N/A (no hand in ref) |
| R2 (Ex1) | 32.4% | 19.3% | **-13.1%** | NO — 19.3% remains |
| R3 (example1) | 22.0% | 21.1% | -0.9% | NO — 21.1% remains |

**Honest assessment:** Hand removal improved significantly on R2 but is still incomplete. On R3, it is essentially unchanged. The prompt anti-reconstruction rule helped on R2 but did not transfer to R3.

---

## 9. Resolution

| Item | Value |
|------|-------|
| Reference R1 | 1200×1600 |
| Reference R2 | 960×1280 |
| Reference R3 | 960×1280 |
| Generated output | **1024×1024** |
| Provider max | 1024×1024 |
| Amazon target | 2000×2000 |

**RESOLUTION = UNRESOLVED PROVIDER LIMITATION**

---

## 10. What Actually Improved

1. **R2 gold shift reduced by 15.1%** — from +36.1% to +21.0%. This is the most significant improvement.
2. **R2 silver preservation improved dramatically** — from 0.7% to 25.3%. The silver/grey tones are now present in the output.
3. **R2 hand removal improved** — skin tones dropped from 32.4% to 19.3%.
4. **R2 product area improved** — from 59.4% to 71.9%, closer to the Amazon 85% target.
5. **R2 overall is now a usable e-commerce image** — clean background, good product visibility, hand substantially removed.

## 11. What Did NOT Improve

1. **R1 gold shift got WORSE** — from +6.4% to +8.7%. The prompt fix did NOT help the silver earring case.
2. **R1 silver preservation did not improve** — 15.4% vs 17.2% (marginal).
3. **R3 is essentially unchanged** — all metrics are within 1-2% of Task 2.
4. **Hand removal on R3 is unchanged** — 22.0% vs 21.1%.
5. **No test case achieved the Amazon 85% product occupancy target** — R1 at 64.1%, R2 at 71.9%, R3 at 67.8%.
6. **Resolution remains 1024×1024** — no improvement.

## 12. Provider Limitations (Still Present)

| Limitation | Impact |
|-----------|--------|
| gpt-image-1 warm-tone bias | Causes silver→gold shift on R1 despite explicit prompt instructions |
| 1024×1024 max output | Cannot meet Amazon 2000×2000 target |
| Imperfect hand removal | Skin tones persist at 19-21% even with anti-reconstruction rules |
| Non-deterministic output | Same prompt + same reference can produce different results on re-run |

## 13. Prompt Limitations (Still Present)

| Limitation | Impact |
|-----------|--------|
| Cannot force colour fidelity on all cases | R1 shows the model can still shift colours despite COLOUR_LOCK |
| Anti-reconstruction not universal | Helped R2 but not R3 |
| Prompt length may dilute instructions | 8,380 chars may cause the model to de-prioritize later instructions |

## 14. Regression Test Results

| Test Suite | Result |
|-----------|--------|
| Backend (pytest) | **107/107 passed** |
| Frontend (tsc --noEmit) | **Zero errors** |

## 15. Whether Another Prompt Change Is Justified

**NO — not at this time.**

Reasoning:
- The prompt fix helped ONE of THREE cases (R2) by a significant margin
- The remaining failures (R1, R3) appear to be provider-level biases that prompt wording cannot reliably overcome
- Further prompt changes risk:
  - Over-engineering the prompt (diminishing returns)
  - Breaking the R2 improvement
  - Adding complexity without measurable benefit
- The evidence suggests the next step should be provider comparison (testing Gemini on the same images) rather than more prompt iteration

## 16. Files Modified

**One file modified:** `backend/app/services/earring_ecommerce_prompt.py`
- 4 changes applied (enhance removal, studio-quality replacement, colour lock addition, anti-reconstruction)
- No other production files modified

## 17. Regression Tests

```
Backend: 107/107 passed, 16 warnings (Pydantic deprecation only)
Frontend: TypeScript compilation — zero errors
```
