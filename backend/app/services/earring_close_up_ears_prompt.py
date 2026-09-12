"""Close Up Ears prompt foundation for earring e-commerce photography.

This module is intentionally independent from the Prompt 1 earring main-image
builder. It defines the presentation-only Prompt 2 workflow: the uploaded
product reference is worn naturally on a woman's ear in a tight close-up.

Product fidelity is the highest priority. The jewellery must be preserved
exactly — geometry, negative spaces, bead clusters, gemstones, connectors,
hanging elements, and component count.
"""

REFERENCE_PRIORITY_MARKER = "REFERENCE IMAGE PRIORITY: MAXIMUM"


def build_close_up_ars_prompt() -> str:  # noqa: misspelling kept for backwards compat
    """Build the isolated Prompt 2 Close Up Ears image-generation prompt.

    The uploaded reference image is the sole source of product identity. This
    prompt requests only a change of wearing context and composition; it does
    not describe, reconstruct, or redesign product details from text.
    """
    return build_close_up_ears_prompt()


def build_close_up_ears_prompt() -> str:
    """Build the isolated Prompt 2 Close Up Ears image-generation prompt.

    The uploaded reference image is the sole source of product identity. This
    prompt requests only a change of wearing context and composition; it does
    not describe, reconstruct, or redesign product details from text.

    Architecture::

        PROMPT 1 OUTPUT (e-commerce product image)
              ↓
        This prompt (Close Up Ears)
              ↓
        + REFERENCE IMAGE (Prompt 1 output preferred, raw upload fallback)
              ↓
        IMAGE GENERATION
              ↓
        On-ear close-up with exact jewellery preserved
    """
    parts = [
        # ── 1:1 VISUAL PRESERVATION LOCK (NON-NEGOTIABLE) ──────────────
        "CRITICAL: The earrings in the output MUST be an exact 1:1 physical "
        "replica of the earrings provided in the reference image. Retain "
        "exact stone count, stone shapes (e.g., baguette, marquise, pear, "
        "round), prong setting structure, metal tone, and earring "
        "silhouette. DO NOT alter the core jewelry design or invent "
        "alternate motifs.",

        # ── INPUT EXTRACTION (remove packaging / distractions) ────────
        "Remove all retail packaging, polybags, display cards, plastic "
        "film, and human fingers. Extract the jewelry piece with pristine "
        "studio fidelity.",

        # ── TASK ──────────────────────────────────────────────────────
        "TASK: Close Up Ears.\n"
        "Generate ONE realistic, premium e-commerce photograph showing the "
        "exact earring from the uploaded reference image naturally worn on a "
        "woman's ear in an extreme macro close-up.\n"
        "This is an ON-EAR PRESENTATION task — the image MUST contain a "
        "visible human ear with the earring attached.\n"
        "This is NOT a standalone product image. This is NOT a white-background "
        "catalogue shot. This is NOT a floating jewellery render.",

        # ── REFERENCE PRIORITY ────────────────────────────────────────
        REFERENCE_PRIORITY_MARKER,

        # ── PRODUCT FIDELITY — STRUCTURAL (HIGHEST PRIORITY) ─────────
        "PRODUCT FIDELITY — STRUCTURAL — HIGHEST PRIORITY (NON-NEGOTIABLE):\n"
        "The uploaded reference image is the sole authoritative source for "
        "the jewellery product. You are placing the EXACT jewellery from the "
        "reference onto a woman's ear. You are NOT creating new jewellery.\n"
        "\n"
        "Preserve EXACTLY as shown in the reference:\n"
        "• Overall silhouette and outline — reproduce the exact visible shape.\n"
        "• Geometry — the exact form, curves, angles, and structural lines.\n"
        "• Proportions — the exact length-to-width ratio and relative sizing "
        "of every component.\n"
        "• Stone positions — preserve every visible stone's exact location, "
        "spacing, and spatial relationship to the metal structure.\n"
        "• Stone shapes — preserve the exact visible stone shapes (baguette, "
        "round, teardrop, marquise, etc.). Do NOT round rectangular stones. "
        "Do NOT change cut styles.\n"
        "• Stone colours — preserve every stone's exact colour without "
        "oversaturation or substitution.\n"
        "• Metal appearance — preserve the exact metal colour, finish, "
        "texture, and surface quality.\n"
        "• Connector relationships — preserve every visible link, loop, "
        "jump ring, wire, and structural connection between components.\n"
        "• Hanging elements — preserve every visible dangling bead, "
        "pearl, chain, teardrop, and decorative element.\n"
        "• Component count — preserve the exact number of every type of "
        "visible component.\n"
        "\n"
        "Do not add, remove, substitute, merge, split, recolour, resize, or "
        "invent any jewellery component. If any product detail is unclear or "
        "partly hidden in the reference, do not fabricate a different detail. "
        "If presentation conflicts with product fidelity, PRESERVE PRODUCT "
        "FIDELITY. The jewellery is never modified for composition reasons.",

        # ── NEGATIVE SPACE — HARD REQUIREMENT ────────────────────────
        "NEGATIVE SPACE — HARD REQUIREMENT (NON-NEGOTIABLE):\n"
        "The reference jewellery contains intentional OPEN / EMPTY areas. "
        "These are structural features, not gaps to fill.\n"
        "\n"
        "You MUST preserve every open/hollow region:\n"
        "• Hollow crescent or open wireframe structures must remain hollow.\n"
        "• Open centres of circular or geometric frames must remain empty.\n"
        "• Spaces between hanging elements must remain separate.\n"
        "• Gaps between bead clusters must remain visible.\n"
        "• Openwork, filigree, or cut-out patterns must stay open.\n"
        "\n"
        "DO NOT fill any internal void with:\n"
        "• Gold or metal material\n"
        "• Skin or flesh tone\n"
        "• Background colour\n"
        "• Gemstone material\n"
        "• Decorative texture or pattern\n"
        "• Shadow or shading\n"
        "\n"
        "The empty space IS part of the jewellery geometry. Filling it "
        "changes the product identity.",

        # ── BEAD / PEARL CLUSTER PRESERVATION ────────────────────────
        "BEAD AND PEARL CLUSTER PRESERVATION (NON-NEGOTIABLE):\n"
        "If the reference jewellery contains bead clusters, pearl groups, "
        "or dangling bead arrangements:\n"
        "\n"
        "• Each individual bead/pearl must remain visually "
        "distinguishable — no merging, fusing, or melting.\n"
        "• Bead clusters must retain their individual separation — gaps "
        "between beads are part of the design.\n"
        "• Large faceted teardrop drops must remain individually "
        "identifiable — each drop is a separate component.\n"
        "• Hanging bead arrangements must preserve the exact count and "
        "relative positioning.\n"
        "• Bead sizes must match the reference — do not enlarge small "
        "beads or shrink large ones.\n"
        "• Natural gravity may affect POSITION in the scene, but must "
        "NOT alter the PRODUCT STRUCTURE.\n"
        "\n"
        "DO NOT allow:\n"
        "• Fused beads that merge into a single mass\n"
        "• Melted or blob-like bead clusters\n"
        "• Missing drops that were present in the reference\n"
        "• Invented drops that were not in the reference\n"
        "• Random bead blobs replacing structured clusters",

        # ── TOP STUD / EAR ATTACHMENT ────────────────────────────────
        "TOP STUD / EAR ATTACHMENT (CRITICAL):\n"
        "Preserve the exact top stud, cluster, or attachment point from "
        "the reference. It must remain:\n"
        "• Clearly visible and sharply defined\n"
        "• Structurally intact — exact shape, exact stone placement\n"
        "• Correctly positioned at the ear piercing point\n"
        "• Physically attached through the earlobe piercing\n"
        "\n"
        "The stud should appear naturally threaded through the piercing "
        "hole — not floating beside the ear, not merged into skin, not "
        "blurred into the background.\n"
        "\n"
        "DO NOT:\n"
        "• Blur the stud into skin texture\n"
        "• Merge it into the earlobe surface\n"
        "• Turn it into a generic round stud\n"
        "• Change its shape or geometry\n"
        "• Remove its central stone or decorative elements",

        # ── ON-EAR COMPOSITION (CRITICAL) ─────────────────────────────
        "ON-EAR COMPOSITION (CRITICAL — THIS IS THE PRIMARY REQUIREMENT):\n"
        "The image MUST show a clearly visible human ear with the exact "
        "reference earring naturally attached to the earlobe.\n"
        "• The ear must be the dominant structural element in the frame.\n"
        "• The earring must be visibly pierced through or hooked onto the "
        "earlobe in a realistic, anatomically correct manner.\n"
        "• Show realistic attachment: the post, hook, or wire must pass "
        "through the piercing hole or wrap around the earlobe naturally.\n"
        "• Maintain natural gravity — dangle earrings must hang downward; "
        "studs must sit flush; hoops must arc naturally.\n"
        "• The earring must be proportional to the ear — correct scale, "
        "correct distance from the lobe, correct visual weight.\n"
        "• Hair should be tucked behind or away from the ear to keep the "
        "earring fully visible.\n"
        "• Skin texture must be natural with realistic pores, tone, and "
        "subsurface scattering.\n"
        "• The ear and earring must occupy the majority of the frame.",

        # ── MACRO PHOTOGRAPHY ─────────────────────────────────────────
        "MACRO PHOTOGRAPHY STYLE:\n"
        "Use an extreme macro close-up perspective — as if shot with an "
        "85-100mm macro lens at approximately f/4 depth of field.\n"
        "• The earring and earlobe must be tack-sharp with visible metal "
        "reflections, gemstone facets, and surface detail.\n"
        "• Shallow depth of field is acceptable for background blur, but "
        "IMPORTANT: do not let shallow depth of field blur any jewellery "
        "component — all earring elements must remain sharp and inspectable.\n"
        "• Partial side profile is acceptable. Full face is NOT required "
        "and should be cropped out or kept non-identifiable.\n"
        "• The complete earring must be fully within the frame — no clipping "
        "of hooks, drops, or dangling elements.",

        # ── BACKGROUND ────────────────────────────────────────────────
        "BACKGROUND:\n"
        "Use a soft, neutral, out-of-focus studio background — warm grey, "
        "soft beige, or gentle gradient. The background must be secondary "
        "and non-distracting.\n"
        "Do NOT use a pure white background. Do NOT use a flat solid colour. "
        "The presence of a human ear makes this a portrait/lifestyle "
        "composition, not a product-only catalogue shot.",

        # ── E-COMMERCE PRESENTATION ───────────────────────────────────
        "E-COMMERCE PRESENTATION:\n"
        "Professional studio-quality lighting with soft, even illumination "
        "on the ear and earring. Natural skin texture. Sharp jewellery "
        "detail. Realistic depth and perspective. Subtle realistic shadows "
        "from the earring onto the earlobe. No props, flowers, fabric, "
        "decorative objects, heavy makeup, text, logos, watermarks, or "
        "additional jewellery. The ear and the exact reference earring are "
        "the dominant visual elements.",

        # ── MANDATORY NEGATIVE CONSTRAINTS ────────────────────────────
        "DO NOT produce any of the following:\n"
        "• Isolated product on a plain background — this is an on-ear image.\n"
        "• Plain white background — this is a portrait composition.\n"
        "• Floating earring with no ear — the earring MUST be attached to "
        "a visible human ear.\n"
        "• Product-only image without any person — a human ear is mandatory.\n"
        "• Still life or catalogue-style product display.\n"
        "• Jewellery displayed beside the ear rather than worn on it.\n"
        "• Detached or dislocated jewellery.\n"
        "• Redesigned or alternative jewellery — only the exact reference "
        "product.\n"
        "• Added or missing components — preserve exact component count.\n"
        "• Changed gemstone cuts, colours, or sizes.\n"
        "• Changed bead shapes, sizes, or arrangement.\n"
        "• Filled negative space — hollow areas must remain hollow.\n"
        "• Fused or merged bead clusters — every bead must be separate.\n"
        "• Blurred or deformed jewellery geometry.\n"
        "• Melted or blob-like jewellery rendering.\n"
        "• Additional jewellery items on the ear or nearby.\n"
        "• Full-face portrait — the ear and earring must dominate, face "
        "should be cropped or minimal.",

        # ── FINAL OUTPUT ──────────────────────────────────────────────
        "FINAL OUTPUT: Return ONE realistic Close Up Ears e-commerce image "
        "showing a woman's ear with the exact reference earring naturally "
        "worn. The result must look like professional macro jewellery "
        "photography — a premium earring-on-ear lifestyle shot that "
        "retains the EXACT identity, geometry, negative spaces, bead "
        "clusters, gemstones, connectors, and visible construction of the "
        "uploaded reference earring.",
    ]
    return "\n\n".join(parts)
