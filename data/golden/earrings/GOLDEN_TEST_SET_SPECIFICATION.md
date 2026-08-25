# Golden Test Set Specification — Real Earring References

> **Phase 4C — Preparation Only**  
> **Status: SPECIFICATION COMPLETE, NO EXECUTION**  
> **Date: 2026-08-24**  
> **Reason: No genuine earring reference images exist in the repository**

---

## Purpose

This document defines the required golden test set for validating real-world earring
fidelity in the GemVision AI image generation pipeline. It is a **specification only** —
no tests are executed until real earring reference images are provided and approved.

---

## Repository Inspection Results

### A. Dedicated test-data directory

- `data/` exists at project root — **empty**
- `backend/data/` contains only `moraa_gemvision.db` (SQLite database)
- No dedicated test-data directory for golden references existed before this phase

### B. Test fixtures convention

- Backend tests: `backend/tests/` using Python `unittest` (5 test files, 107 tests)
- Root-level E2E scripts: `api_gen_test.py`, `api_analyze_test.py` (standalone, hardcoded to `test_ring.png`)
- `test_ring.png` at root: synthetic ring image created by `make_test_image.py`
- No convention for storing golden reference images

### C. api_gen_test.py external reference-image path

- Currently **hardcodes** `test_ring.png`:
  ```python
  with open("test_ring.png", "rb") as f:
      b64 = base64.b64encode(f.read()).decode("utf-8")
  ```
- **Cannot** accept an external reference-image path without modification
- A separate test-only script can be created safely (outside production path)

### D. Separate test-only script safety

- Yes, a separate script can be created at `data/golden/` or `tests/golden/`
- This does not modify any production code
- The existing `api_gen_test.py` remains untouched

### E. Generated artifacts

Root-level generated images (NOT reference images — these are outputs):
- `generated_ring.png` — output from `api_gen_test.py`
- `golden_test_openai.png` — generated output
- `golden_test_gemini.png` — generated output  
- `golden_test_A_amazon_openai.png` — generated output

These are **generated outputs**, not references. They should remain where they are
(no action required per safety rules).

### F. backend/app/uploads earring references

- 9 uploaded images in UUID-named subdirectories
- Filenames: `test_image.jpg`, `Screenshot_2026-07-27_162606.png`, `hhhh.jpg`, `23.jpg`, `test-image.png`
- File sizes range from 825 bytes to 328,380 bytes
- Database analysis record: only 1 analysis with **no category** (None)
- **No evidence any of these are earring references**
- **Verdict: ZERO genuine earring references found**

---

## Golden Test Set Specification

### Test Cases

| Test ID | Product Type | Visual Characteristics | Main Fidelity Risks | Required Reference Image | Expected Provider Tests | Manual QA Criteria |
|---------|-------------|----------------------|--------------------|-----------------------|----------------------|-------------------|
| G1 | Simple stud | Small, round stone on short post. Minimal metal visible. Clean geometry. | Stone shape roundness, post visibility, scale accuracy | `G1_simple_stud.png` | A, B, C, D, E | Stone is round and centered; post is short and straight; metal colour matches |
| G2 | Stone-heavy | Multiple stones (5+), cluster or pave setting. Complex light reflections. | Stone count accuracy, setting pattern, light scatter fidelity | `G2_stone_heavy.png` | A, B, C, D, E | Correct stone count; setting pattern preserved; no stones added/removed |
| G3 | Dangling | Drop or chandelier style. Elongated vertical form. Movement implied. | Length proportions, dangling element count, attachment mechanism | `G3_dangling.png` | A, B, C, D, E | Length proportional; dangling elements match; hook/attachment visible |
| G4 | Intricate / filigree | Fine metalwork patterns, cut-outs, granulation. High detail density. | Pattern preservation, fine detail loss, metalwork accuracy | `G4_intricate_filigree.png` | A, B, C, D, E | Filigree patterns intact; cut-outs preserved; no detail smoothing |
| G5 | Asymmetric | Deliberately uneven design. Different left/right elements. | Asymmetry preservation, left-right distinction, intentional imbalance | `G5_asymmetric.png` | A, B, C, D, E | Left/right differences preserved; asymmetry not "corrected"; intentional imbalance maintained |
| G6 | Thin hook/post | Lever-back, fish-hook, or thin wire mechanism. Fragile appearance. | Hook curvature, thin element preservation, attachment visibility | `G6_thin_hook_post.png` | A, B, C, D, E | Hook curvature matches; thin elements not thickened; attachment mechanism visible |
| G7 | Single-piece | One earring only (not a pair). Asymmetric pair context. | Single vs pair detection, no duplicate generation | `G7_single_piece.png` | A, B, C, D, E | Exactly one earring rendered; no second earring generated; single-piece confirmed |
| G8 | Pair | Two matching earrings. Symmetric presentation. | Pair symmetry, matching elements, spacing | `G8_pair.png` | A, B, C, D, E | Two earrings present; matching design; symmetric spacing |
| G9 | Complex stone arrangement | Mixed stone sizes, multi-row, tiered or graduated pattern. | Stone hierarchy, size gradation, arrangement accuracy | `G9_complex_stone_arrangement.png` | A, B, C, D, E | Stone sizes correctly graduated; arrangement pattern preserved; no stones misplaced |
| G10 | Subtle geometry | Minimal design with precise angles, curves, or proportions. | Geometric precision, subtle detail preservation, proportion accuracy | `G10_subtle_geometry.png` | A, B, C, D, E | Angles and curves match; proportions accurate; subtle details not lost |

### Reference Image Requirements

Each reference image must be:
- **Real photograph** of an actual earring (not synthetic, not AI-generated)
- **Minimum 800×800 pixels** at 72+ DPI
- **Clear, well-lit** with visible product details
- **Single product** centered in frame (for G1–G7, G9–G10) or **pair arranged symmetrically** (for G8)
- **PNG or JPEG** format
- **No watermarks, text, or logos** on the reference image
- **Accurate colour representation** (not heavily filtered)

---

## Future Controlled Test Matrix

Once real earring references are available, execute the following matrix:

| Matrix ID | Provider | Reference Image | Marketplace | Description |
|-----------|----------|----------------|-------------|-------------|
| A | OpenAI (gpt-image-1) | ✅ Yes | Amazon India | Full reference + marketplace presentation |
| B | Gemini | ✅ Yes | Amazon India | Full reference + marketplace presentation |
| C | OpenAI (gpt-image-1) | ✅ Yes | None | Reference-only, no marketplace rules |
| D | Gemini | ✅ Yes | None | Reference-only, no marketplace rules |
| E | OpenAI (gpt-image-1) | ❌ No | None | Text-to-image baseline (no reference) |

**For each test case (G1–G10) × each matrix row (A–E) = 50 total tests.**

### Execution Rules

1. **DO NOT execute** until real earring reference images are provided
2. **DO NOT execute** unless explicitly approved by the project owner
3. **DO NOT create fake/synthetic earring images** as substitutes
4. Each test must be **manually QA'd** against the reference image
5. Results must be logged with provider, generation time, and fidelity notes

---

## How to Populate This Test Set

1. Obtain real earring photographs (10 images matching G1–G10)
2. Place them in `data/golden/earrings/` with filenames matching the spec
3. Update this document with actual file paths and metadata
4. Create a test runner script (separate from production code)
5. Execute the controlled matrix with manual QA
6. Document results in a benchmark report

---

## Safety Constraints (Unchanged)

- PFIE_ENABLED: **False**
- ProductFidelity: **Not populated** (model exists, not used for golden validation)
- REFERENCE_PRIORITY_BLOCK: **Unchanged**
- OPENAI_IDENTITY_ANCHOR: **Unchanged**
- Provider routing: **Unchanged** (OpenAI primary → Gemini fallback)
- No automated fidelity validation: **Manual QA only**
- No retry/rejection logic: **Manual review only**
- No production code modifications: **Zero**

---

## Files in This Directory

```
data/golden/earrings/
├── GOLDEN_TEST_SET_SPECIFICATION.md   ← This file (specification only)
├── G1_simple_stud.png                 ← [NOT YET PROVIDED]
├── G2_stone_heavy.png                 ← [NOT YET PROVIDED]
├── G3_dangling.png                    ← [NOT YET PROVIDED]
├── G4_intricate_filigree.png          ← [NOT YET PROVIDED]
├── G5_asymmetric.png                  ← [NOT YET PROVIDED]
├── G6_thin_hook_post.png              ← [NOT YET PROVIDED]
├── G7_single_piece.png                ← [NOT YET PROVIDED]
├── G8_pair.png                        ← [NOT YET PROVIDED]
├── G9_complex_stone_arrangement.png   ← [NOT YET PROVIDED]
└── G10_subtle_geometry.png            ← [NOT YET PROVIDED]
```
