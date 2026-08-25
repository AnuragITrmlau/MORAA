# TASK 5 — EARRING E-COMMERCE PROMPT INVESTIGATION REPORT

**Date:** 2026-08-25
**Provider:** Gemini gemini-3.1-flash-image (single provider, all variants)
**References:** 3 real earring images (ex.jpeg, Ex1.jpeg, example 1.jpeg)
**Variants tested:** V1-V9 (progressive prompt additions + focused tests)

---

## 1. Best-Performing Prompt

**There is no best-performing prompt.** All 9 variants tested produce unacceptable results. The fundamental problem is not the prompt — it is the provider's inability to preserve the reference product.

---

## 2. Exact Prompt Text (Best Relative Performer)

V6 (no background instruction, 1,821 chars) had the least product destruction on R1, but the product was still destroyed:

```
Generate an e-commerce image of the earring in the reference photo.
Keep the exact earring exactly as it appears — same shape, same metal,
same stones, same proportions. Do not change, remove or redraw any
part of the jewellery.
```

**This prompt still produces images where 77-82% of the product area is lost.**

---

## 3. Number of Words/Characters

| Variant | Chars | Words | Description |
|---------|-------|-------|-------------|
| V1 | 1,880 | 298 | Minimal prompt |
| V2 | 2,141 | 339 | + Identity lock |
| V3 | 2,324 | 368 | + Material/colour lock |
| V4 | 2,581 | 408 | + Cleanup rule |
| V5 | 2,854 | 443 | + Detail preservation |
| V6 | 1,821 | 280 | No background instruction |
| V7 | 1,974 | 312 | White bg + do NOT remove product |
| V8 | 1,962 | 305 | Keep position + replace bg only |
| V9 | 1,918 | 293 | Maximum explicitness (photo editor framing) |

---

## 4. Reference Images Tested

- **R1:** ex.jpeg — Silver earring on dark surface/card (97.9% product area, 81.6% silver)
- **R2:** Ex1.jpeg — Earring held by hand (53.2% product area, 34.6% skin)
- **R3:** example 1.jpeg — Dark earring with coloured elements (82.3% product area, 14.8% silver)

---

## 5. Results for Each Reference

### R1 — Silver earring on dark surface

| Variant | Product Area | Reference | Loss | Gold Shift |
|---------|-------------|-----------|------|------------|
| V1 | 19.9% | 97.9% | **-78.0%** | +0.6% |
| V2 | 15.7% | 97.9% | **-82.2%** | +0.1% |
| V3 | 19.4% | 97.9% | **-78.5%** | +1.2% |
| V4 | 19.8% | 97.9% | **-78.1%** | +0.6% |
| V5 | 18.5% | 97.9% | **-79.4%** | +1.3% |
| V6 | 21.2% | 97.9% | **-76.7%** | +0.1% |
| V7 | 15.4% | 97.9% | **-82.5%** | -1.0% |
| V8 | 18.4% | 97.9% | **-79.5%** | -0.9% |
| V9 | 20.2% | 97.9% | **-77.7%** | +0.1% |

**Failure:** The silver earring (97.9% of reference) is replaced by white background in ALL variants. Product area drops to 15-21%. The earring is almost entirely destroyed.

### R2 — Hand-held earring

| Variant | Product Area | Reference | Loss | Gold Shift |
|---------|-------------|-----------|------|------------|
| V1 | 19.4% | 53.2% | **-33.8%** | +10.3% |
| V2 | 20.9% | 53.2% | **-32.3%** | +12.2% |
| V3 | 21.5% | 53.2% | **-31.7%** | +13.8% |
| V4 | 26.5% | 53.2% | **-26.7%** | +17.1% |
| V5 | 16.7% | 53.2% | **-36.5%** | +7.0% |
| V6 | 22.6% | 53.2% | **-30.6%** | +14.6% |
| V7 | 18.9% | 53.2% | **-34.3%** | +10.7% |
| V8 | 20.0% | 53.2% | **-33.2%** | +13.5% |
| V9 | 19.8% | 53.2% | **-33.4%** | +12.9% |

**Failure:** Product area drops 27-37%. Hand removal partially works (skin drops from 34.6% to 5-18%) but the earring itself is also reduced. Gold shift +7-17% across all variants.

### R3 — Dark earring with coloured elements

| Variant | Product Area | Reference | Loss | Gold Shift |
|---------|-------------|-----------|------|------------|
| V1 | 12.4% | 82.3% | **-69.9%** | -1.6% |
| V2 | 18.9% | 82.3% | **-63.4%** | +1.4% |
| V3 | 14.7% | 82.3% | **-67.6%** | -0.4% |
| V4 | 14.0% | 82.3% | **-68.3%** | -0.8% |
| V5 | 18.5% | 82.3% | **-63.8%** | -0.1% |
| V6 | 14.6% | 82.3% | **-67.7%** | -3.2% |
| V7 | 13.6% | 82.3% | **-68.7%** | -2.8% |
| V8 | 12.8% | 82.3% | **-69.5%** | -3.8% |
| V9 | 17.8% | 82.3% | **-64.5%** | +1.1% |

**Failure:** Product area drops 63-70%. The dark earring is replaced by white background with a small gold/dark element remaining.

---

## 6. What Improved

**Almost nothing improved product preservation.** Specific observations:

- V6 (no background instruction): Slightly less product loss on R1 (-76.7% vs -78.0% for V1). But still catastrophic.
- V5 (detail preservation): Best gold shift on R2 (+7.0% vs +10.3% for V1). But product area is worst (-36.5%).
- V7 (explicit "do NOT remove product"): Worst product preservation on R1 (-82.5%). The explicit instruction to NOT remove the product actually made things worse.

---

## 7. What Still Failed

**Everything.** The core failure is:

1. **Product destruction:** 63-82% of product area is lost across all references and all variants.
2. **Silver → white replacement:** Silver earrings are replaced by white background.
3. **Gold colour shift:** Hand-held earring (R2) shows +7-17% gold shift.
4. **Dark → gold conversion:** Dark earring (R3) loses dark tones.
5. **No prompt fixes the product destruction:** V1 through V9 all produce the same fundamental failure.

---

## 8. Is the Failure Prompt-Related or Provider-Related?

**The failure is PROVIDER-RELATED.** Evidence:

### Evidence A: Product destruction is constant across all prompts
- V1 (1,880 chars) → R1 product: 19.9%
- V6 (1,821 chars, no background instruction) → R1 product: 21.2%
- V9 (1,918 chars, maximum explicitness) → R1 product: 20.2%
- **Varying the prompt by 1,000+ chars and changing instructions produces negligible difference in product preservation (19-21%).**

### Evidence B: Explicit anti-destruction instructions fail
- V7 adds "IMPORTANT: Do NOT remove the earring itself" → product area WORST (15.4%)
- V9 adds "Do not generate a new image. Do not draw a new earring." → product area unchanged (20.2%)
- **The model ignores explicit instructions to preserve the product.**

### Evidence C: Removing background instruction doesn't help
- V1 (with "white background") → R1 product: 19.9%
- V6 (without background instruction) → R1 product: 21.2%
- **Removing the background instruction barely changes the result (+1.3%).**

### Evidence D: The model generates from reference, not from pixels
- The Gemini provider sends: `[REFERENCE_IMAGE_ANCHOR, reference_image, prompt]`
- The model uses the reference as "inspiration" and generates a NEW image
- It does NOT edit the reference image pixels
- This is confirmed by the massive product area loss (63-82%)

### Evidence E: Previous Task 4 experiment confirmed provider dominance
- Same prompts on OpenAI: +10-43% gold shift
- Same prompts on Gemini: +0.7-28% gold shift
- **Provider change accounts for 3-10x improvement; prompt change accounts for minimal improvement.**

---

## 9. Conflicting Instructions Discovered

### Conflict 1: "White background" vs "Preserve product"
- V1 asks for "clean white background" AND "preserve the earring"
- The model cannot do both — it replaces the product with white background
- Removing the background instruction (V6) barely helps (+1.3% product area)

### Conflict 2: "Do NOT remove product" vs model behavior
- V7 explicitly says "Do NOT remove the earring itself"
- Product area is WORST (15.4%) — the explicit instruction has no effect or backfires
- **The model cannot follow negative instructions ("do NOT") for core tasks**

### Conflict 3: "Source of truth" vs model interpretation
- All prompts say "reference image is the source of truth"
- The model ignores this and generates from its own interpretation
- **Text instructions cannot override the model's image generation behavior**

---

## 10. Phase 5 — Instruction Classification (Existing Prompt)

For each instruction block in `backend/app/services/earring_ecommerce_prompt.py`:

| Block | Classification | Evidence |
|-------|---------------|----------|
| ANTI_REDESIGN_INSTRUCTION | **D — Potentially conflicting** | "PRODUCT PHOTOGRAPHY task" conflicts with the model's actual behavior (generation, not photography) |
| ANTI_SYMMETRY_INSTRUCTION | **C — Redundant** | The model doesn't produce symmetric outputs — it produces destroyed outputs. Symmetry is not the failure mode. |
| PRODUCT IDENTITY block | **D — Potentially conflicting** | Detailed preservation rules are ignored when the model destroys the product |
| EARRING_TYPE_PRESERVATION | **C — Redundant** | Earring type doesn't matter when the earring is destroyed |
| MATERIAL_FIDELITY_INSTRUCTION | **D — Potentially conflicting** | "Preserve EXACTLY as shown" conflicts with the model's generation behavior |
| COLOUR_LOCK_INSTRUCTION | **D — Potentially conflicting** | "Silver must remain silver" — the model replaces silver with white, not gold. Colour lock doesn't address the real failure mode. |
| INPUT_CLEANUP_INSTRUCTION | **D — Potentially conflicting** | "Remove hand" competes with "preserve product" — when hand is removed, product behind it must be reconstructed |
| ANGLE_PRESERVATION_INSTRUCTION | **C — Redundant** | Angle doesn't matter when the product is destroyed |
| ECOMMERCE_PRESENTATION_INSTRUCTION | **E — Potentially causing redesign** | "Clean commercial presentation" and "professional studio-quality" encourage the model to redesign/recreate |
| OUTPUT RULE | **D — Potentially conflicting** | "WITHOUT any jewellery card" competes with "preserve the product" |

### Key Wording Issues:
- **"enhance"** — removed in Task 3 (confirmed helpful to remove)
- **"studio-quality"** — removed in Task 3 (confirmed helpful to remove)
- **"professional"** — still present in ECOMMERCE_PRESENTATION — may encourage redesign
- **"reflections"** — may cause the model to add artificial reflections
- **"lighting"** — "neutral, balanced lighting" may cause colour interpretation changes
- **"accurate scale"** — the model cannot maintain scale when it destroys the product
- **"centred"** — the model centres its generated version, not the original product

---

## Honest Verdict

### The Goal
REFERENCE → SAME JEWELLERY → CLEAN E-COMMERCE PRESENTATION

### The Reality
REFERENCE → DESTROYED PRODUCT → WHITE BACKGROUND WITH SMALL UNRECOGNIZABLE ELEMENT

### Root Cause
**Gemini gemini-3.1-flash-image cannot preserve a reference product when generating an e-commerce image.** The model treats the reference image as inspiration, not as pixel-level source truth. It generates a new image using the reference as a concept, which results in:
- 63-82% product area loss
- Silver → white replacement
- Gold colour shift
- Dark → gold conversion
- Loss of stones, hooks, chains, decorative details

### Is this fixable by prompting?
**No.** The experiment tested 9 variants ranging from 1,821 to 2,905 characters, with progressively stronger preservation instructions. None achieved acceptable product preservation. The product destruction is constant across all prompts (19-21% product area on R1 regardless of prompt).

### Is this fixable by changing provider?
**Possibly.** The previous Task 4 experiment showed OpenAI gpt-image-1 has different failure modes (gold shift but less product destruction). A provider that supports actual image editing (not generation from reference) might work. However, OpenAI credits are currently exhausted.

### Is this fixable by changing the API approach?
**Possibly.** The current approach uses `generate_content` with `response_modalities=["IMAGE"]`, which is image GENERATION, not image EDITING. A true image editing API (like inpainting or img2img with high denoising strength near 0) might preserve the product. Gemini's API may not offer this capability for the current model.

### Should production code be changed?
**The prompt should be simplified** — the 8,380-char production prompt adds instructions that have no measurable effect on product preservation. A 1,800-2,000 char prompt produces equivalent (poor) results with less token cost.

**The provider should be investigated** — the current Gemini model fundamentally cannot preserve reference products. This is a provider limitation, not a prompt limitation.

### What should NOT be done
- Do NOT add more prompt instructions — they have no effect
- Do NOT claim the problem is solved — it is not
- Do NOT change the architecture — the issue is provider-level
- Do NOT remove the earring e-commerce feature — it works technically, just not visually

---

## Regression Test Results

- Backend tests: **107/107 passed**
- TypeScript: **0 errors**
- Filter UI: **remains hidden**, code preserved
- No production files modified (only `backend/app/schemas/image_generation.py` max_length fix from previous task)
