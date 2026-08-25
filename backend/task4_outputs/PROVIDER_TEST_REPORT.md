# Task 4 — Image provider root-cause investigation

Date: 2026-08-25  
Scope: investigation only. No protected production or frontend files were changed.

## Current paths, verified from code

### Gemini

- **Configured model:** `gemini-3.1-flash-image` (`GEMINI_IMAGE_MODEL` default). The live controlled call confirmed this model in its result.
- **SDK and operation:** `google-genai`; `client.models.generate_content(...)` is called in a thread.
- **Request:** `GenerateContentConfig(response_modalities=["IMAGE", "TEXT"], image_config=ImageConfig(aspect_ratio=...))`; with a reference, contents are `[REFERENCE_IMAGE_ANCHOR, Part.from_bytes(reference bytes, MIME type), prompt]`.
- **Reference handling:** multimodal text-and-image input. It is not an inpainting/mask workflow and is not supplied as a separately parameterized denoise/img2img control.
- **Controls actually used:** aspect ratio and requested response modalities only. No seed, mask, selected region, reference strength, denoise value, or image preservation control is used.
- **Provider capability:** Google documents `gemini-3.1-flash-image` as supporting image editing from image-and-text input. That is an image-to-image generative edit, not an API promise to preserve exact geometry. Google’s current examples use the Interactions API; this implementation uses `generate_content`, so it also does not follow the current documented request surface for editing.

### OpenAI

- **Configured model:** `gpt-image-1` (`OPENAI_IMAGE_MODEL` default). It is primary; Gemini is recoverable-failure fallback.
- **SDK and operation:** `openai.AsyncOpenAI`; with a reference and an editing-capable configured model, `client.images.edit(...)` is invoked.
- **Reference handling:** reference bytes are uploaded as a temporary file in the edit request. This is a real Images edits operation, not multimodal text context.
- **Parameters:** `model`, `image`, prompt prefixed by `OPENAI_IDENTITY_ANCHOR`, `size`, and `quality="high"`. No mask is uploaded. No `input_fidelity` is supplied; `quality` is an output-quality setting, not a guarantee of source fidelity.
- **Provider capability:** OpenAI documents that the edits endpoint edits existing images, uses images as references, and supports mask-based partial replacement. Therefore the route is technically better aligned to an edit than Gemini’s current request, but exact jewellery retention remains unverified and is not guaranteed merely by using the endpoint.

## Controlled real-image test

Reference: `Earring Examples/ex.jpeg`  
Prompt: the exact five-sentence minimal prompt specified in Task 4.  
Execution: unchanged `ImageGenerationManager`, forced provider, 4:5 context; the manager also appended its existing reference-priority block. Artifacts: `minimal_provider_test_results.json`, `minimal_ex_gemini.png`.

| Provider | Result | Visual evaluation |
|---|---|---|
| Gemini | Success, `gemini-3.1-flash-image`, 17.70 s | Background/card distractions were removed and the broad chandelier-earring concept, gold metal, clear stones and magenta beads remain recognizable. It is **not** the exact pair: upper stones become distinctly blue vs peach, the lower bead count/placement and connectors are reconstructed, detail density changes, and the pair is more regular/symmetrical. Product identity, geometry, proportions, stones, beads, connectors, and intentional differences therefore fail the exact-fidelity criterion. Occupancy and white cleanup are good. |
| OpenAI | No output | The actual `images.edit` branch was entered, then returned `429 credit_balance_exhausted`. There is no OpenAI image to inspect and no comparative visual claim. |

This assessment is visual, not based solely on pixel statistics. A successful Gemini HTTP request is not classified as success for the product requirement.

## Root-cause classification: F — combination

1. **Primary technical cause: generative reference handling/provider limitation.** The Gemini path is capable of image-and-text editing, but it asks a generative model to recreate an e-commerce image from a single cluttered photo. The observable reconstruction of stones, bead layout and connectors is exactly the failure mode that makes it unsuitable for “same SKU” fidelity.
2. **Missing edit controls compound it.** The implementation has no mask or restricted replacement region, no denoise/reference-strength setting, no seed, and no verification/retry gate. The model must regenerate the entire composition while also removing the card/background.
3. **API-operation mismatch with the precision requirement.** It is not wrong to call Gemini’s mixed-image generation as an image edit, but it is the wrong *class of operation* for a deterministic requirement: “remove only photographic distractions while retaining every product pixel/feature.” The current Google docs demonstrate image editing through Interactions; the project remains on `generate_content`, which gives no current documented precision-control surface.
4. **Prompt structure is not the primary cause.** The specified short prompt still fails after avoiding the prior 1,821–2,905-character variants. The manager’s added priority block and provider anchor did not prevent reconstruction. Prompt length/order may affect results, but no wording can supply absent region- or fidelity controls.
5. **Input limits matter but do not excuse the result.** A single casual photo has occlusion, perspective and lighting ambiguity. It makes exact reconstruction harder; it does not change the requirement or make a visually plausible replacement acceptable.

## Requirement fit and recommendation

The requirement is source-of-truth product presentation, not “inspired-by” generation. Gemini’s present path does **not** meet it. OpenAI’s current path is structurally an edit path and therefore is the next sensible candidate to test after credits are available, but it is not yet evidenced as capable and should not be promoted on endpoint name alone.

Recommended next architecture to evaluate, without implementing it now: a **hybrid deterministic pipeline**—segment/retain original jewellery pixels and use deterministic background/hand cleanup where feasible; reserve generative editing for explicitly masked, non-product regions; then apply visual/product-fidelity acceptance checks. In parallel, fund and run a controlled OpenAI edit test and, if its current API supports it for the selected model, evaluate mask and input-fidelity behavior. If either model must regenerate the jewellery itself, reject that output for e-commerce main-image use.

## Documentation used

- [Google Gemini image generation and editing](https://ai.google.dev/gemini-api/docs/image-generation)
- [OpenAI image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
- [OpenAI Images API reference](https://developers.openai.com/api/reference/resources/images)

## Regression results

- `python -m pytest --tb=short -q` with the ambient environment: **failed collection** because `backend/.env` supplies `DEBUG=release`, while `Settings.DEBUG` is a boolean. This was not changed.
- With process-only `DEBUG=false`: **107 passed**, 16 existing Pydantic/deprecation warnings.
- `npx tsc --noEmit` from `frontend`: **passed, 0 TypeScript errors**. (An earlier invocation from `backend` was invalid because that directory has no TypeScript project; it did not modify anything.)

Confidence: **high** that Gemini’s current live path does not satisfy exact jewellery preservation; **high** on code-path classification; **medium** on OpenAI fidelity suitability because live OpenAI output was blocked by exhausted credits.
