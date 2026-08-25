"""Prompt Fusion Intelligence Engine (PFIE) — GemVision V3.

Fuses layers into a single final image-generation prompt:

    Layer 1 — Gemini product facts (authoritative — never invented)
    Layer 2 — ChatGPT creative direction (Luxury Jewellery Creative Director)
    Layer 3 — Product preservation rules (non-negotiable)
    Layer 4 — Jewellery preservation & scale control (non-negotiable)
    Layer 5 — Photography enhancement instructions
    (lifestyle) — wearing-mode instructions + category fitting rules

Pipeline::

    Uploaded Image
        |
    Gemini Vision Analysis  ──►  Product Intelligence JSON (incl. scale facts)
        |
    ChatGPT Prompt Intelligence  (creative direction; template fallback)
        |
    Prompt Fusion Engine  ──►  Reference Image + Final Prompt
        |
    Image Generation

Rules enforced here:
- Gemini only analyzes; it never writes marketing prompts.
- The creative director never invents product details (facts are the only
  permitted product information).
- The preservation block is appended to EVERY fused prompt.
- The jewellery scale-control block (size / proportions / anatomy fitting)
  is appended to EVERY fused prompt when PFIE_SCALE_CONTROL_ENABLED is on.
- Category-based fitting rules (ear-to-earring ratio, finger proportions,
  wrist proportion, collarbone placement) are added for lifestyle/wearing
  mode so jewellery fits naturally on the human body.
- In lifestyle/wearing mode, wearing-specific instructions are appended
  (earrings worn on the ear, ring worn on a hand, etc.) and product cards,
  tags, packaging, text, and "hands holding product" are explicitly removed.
- Callers MUST send the uploaded image as the reference image alongside
  the fused prompt — the prompt itself instructs the model that the
  reference image is the authoritative source.

Zero breaking change: if ChatGPT is disabled, unconfigured, or fails, the
engine falls back to deterministic creative-direction templates (zero
tokens) and always returns a usable fused prompt.
"""

import json
import time
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings
from app.utils.logger import logger
from app.ai.product_fidelity import (
    PRODUCT_PRESERVATION_BLOCK,
    SCALE_CONTROL_BLOCK,
    REFERENCE_IMAGE_INSTRUCTION,
)

# ─── Prompt categories (matches the 8 n8n workflow categories) ─────────
PROMPT_CATEGORIES = {
    "professionalShot",
    "useCaseShot",
    "ingredientStory",
    "festive",
    "transformation",
    "scaleReference",
    "complementaryShot",
    "ugcStyle",
}

PROMPT_CATEGORY_LABELS: Dict[str, str] = {
    "professionalShot": "Professional Studio Shot",
    "useCaseShot": "Use Case / In-Use Shot",
    "ingredientStory": "Ingredient & Provenance Story",
    "festive": "Indian Festive Campaign",
    "transformation": "Before / After Transformation",
    "scaleReference": "Scale Reference Shot",
    "complementaryShot": "Complementary Lifestyle Pairing",
    "ugcStyle": "User-Generated Content Style",
}

# ─── Layer 3 — Product Preservation Block (spec text, verbatim) ────────
# Appended to EVERY fused prompt. The uploaded image is the authoritative
# reference; the model must reproduce the exact product and only improve
# the photography.
# PRODUCT_PRESERVATION_BLOCK imported from app.ai.product_fidelity

# ─── Layer 4 — Jewellery Preservation & Scale Control Block ───────────
# Appended to EVERY fused prompt. Fixes the "oversized / tiny / unrealistically
# placed jewellery" problem by giving the image model explicit real-world scale
# instructions. The uploaded reference image remains the authoritative source.
# SCALE_CONTROL_BLOCK imported from app.ai.product_fidelity

# ─── Category-based fitting rules (Step 4) ────────────────────────────
# Realistic size/ratio guidance per jewellery category so the piece fits the
# human body naturally instead of floating, covering the face, or being
# exaggerated in size.
FITTING_RULES: Dict[str, str] = {
    "Earring": (
        "SCALE & FITTING — EARRINGS: Maintain a realistic ear-to-earring ratio. "
        "The earrings must attach naturally to the earlobe. Do not cover large "
        "parts of the face. Keep realistic length and width relative to the ear."
    ),
    "Necklace": (
        "SCALE & FITTING — NECKLACE: Maintain natural neck placement. Follow the "
        "collarbone anatomy. Do not make the necklace unrealistic in size. It must "
        "sit naturally against the neck and collarbone."
    ),
    "Pendant": (
        "SCALE & FITTING — PENDANT: The pendant must rest naturally at the "
        "collarbone on its chain, in realistic proportion to the neck and chest. "
        "Do not enlarge the pendant or its stones."
    ),
    "Chain": (
        "SCALE & FITTING — CHAIN: The chain must sit naturally around the neck "
        "with realistic link size and drop. Do not thicken the chain or alter "
        "its length."
    ),
    "Ring": (
        "SCALE & FITTING — RING: Maintain realistic finger proportions. The ring "
        "must fit naturally on the finger. Do not enlarge the gemstone size. The "
        "band must sit comfortably around the finger, never floating."
    ),
    "Bracelet": (
        "SCALE & FITTING — BRACELET: Maintain realistic wrist proportion. The "
        "bracelet must wrap naturally around the wrist — not too tight, not "
        "floating, not enlarged."
    ),
    "Bangle": (
        "SCALE & FITTING — BANGLE: Maintain realistic wrist proportion. The bangle "
        "must sit naturally around the wrist with realistic diameter and thickness."
    ),
    "Watch": (
        "SCALE & FITTING — WATCH: Maintain realistic wrist proportion. The case "
        "and strap must fit naturally around the wrist; do not enlarge the dial "
        "or exaggerate the case size."
    ),
    "Coin": (
        "SCALE & FITTING — COIN: Maintain realistic coin-to-body proportion. The "
        "coin pendant must sit naturally at the neckline on its chain."
    ),
    "Cufflinks": (
        "SCALE & FITTING — CUFFLINKS: Maintain realistic cuff proportion. The "
        "cufflinks must fit naturally in the shirt cuff."
    ),
}

GENERIC_FITTING_RULE = (
    "SCALE & FITTING: Maintain realistic jewellery-to-body proportions. The piece "
    "must fit naturally on the human body — never oversized, never tiny, never "
    "unrealistically placed."
)

# ─── Layer 5 — Photography Enhancement Instructions ─────────────────────
ENHANCEMENT_BLOCK = (
    "PHOTOGRAPHY ENHANCEMENT (the ONLY things you may improve):\n"
    "Shoot like a luxury e-commerce campaign: crisp focus on the product, "
    "premium soft lighting, a clean complementary background, true-to-metal "
    "color accuracy, gentle reflections, shallow depth of field, and high "
    "resolution. Elevate the photography — never the product."
)

# ─── Reference-image instruction (IMAGE GENERATION RULE) ────────────────
# The caller always attaches the uploaded image; this tells the model how
# to weight it against the creative text.
# REFERENCE_IMAGE_INSTRUCTION imported from app.ai.product_fidelity

# ─── Layer 2 — ChatGPT Luxury Jewellery Creative Director ───────────────
CREATIVE_DIRECTOR_SYSTEM_PROMPT = (
    "You are the Creative Director of a world-class luxury jewellery "
    "photography studio. You write image-generation prompts that make AI "
    "photography look editorial, commercial, and expensive — while NEVER "
    "altering the product.\n\n"
    "Rules:\n"
    "1. The product facts you are given are 100% authoritative. Never "
    "invent, add, remove, or change any product detail (metal, stones, "
    "shape, placement, craftsmanship). If a fact is missing, omit it — "
    "never fabricate it.\n"
    "2. Your output is CREATIVE DIRECTION ONLY: scene, lighting, camera "
    "style, composition, fashion direction, and lifestyle instructions. "
    "Describe the environment and the photography, never the product design.\n"
    "3. Keep it under 130 words, 4-6 sentences, professional editorial tone.\n"
    "4. Output plain text only — no labels, no headers, no JSON, no "
    "bullet points."
)

STUDIO_MODE_GUIDANCE = (
    "STUDIO MODE: The product is the hero on a clean premium set. No human "
    "models unless the category inherently requires context. Controlled "
    "studio lighting, luxury surfaces, commercial hero-shot composition."
)

LIFESTYLE_MODE_GUIDANCE = (
    "LIFESTYLE / WEARING MODE: The jewellery MUST be worn naturally by a "
    "model in a luxury lifestyle setting. The model must never hold the "
    "jewellery in packaging or on a card. Product cards, price tags, "
    "'Fashion Jewellery' text, packaging, and hands holding the product are "
    "strictly forbidden. The worn jewellery is the clear focal point."
)


# ─── Product facts normalisation ────────────────────────────────────────


def _first_value(data: Dict[str, Any], *keys: str) -> str:
    """Return the first non-empty string value among candidate keys."""
    for key in keys:
        value = data.get(key)
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            cleaned = [str(v) for v in value if str(v).strip()]
            if cleaned:
                return ", ".join(cleaned)
        text = str(value).strip()
        if text and text.lower() not in ("none", "unknown", "n/a", "none detected"):
            return text
    return ""


def _normalise_facts(data: Dict[str, Any]) -> Dict[str, str]:
    """Normalise incoming product intelligence into canonical fact fields.

    Accepts both camelCase and snake_case keys. Missing facts are omitted
    (never invented).
    """
    facts: Dict[str, str] = {}

    mapping = [
        ("category", "category"),
        ("subcategory", "subcategory"),
        ("jewellery_type", "jewelleryType", "jewellery_type"),
        ("metal", "metal", "metalDetection", "metal_detection", "material"),
        ("stones", "stones", "gemstones", "gemstoneDetection", "gemstone_detection"),
        ("stone_placement", "stonePlacement", "stone_placement", "stoneSetting", "stone_setting"),
        ("shape", "shape"),
        ("texture", "texture"),
        ("finish", "finish", "surfaceFinish", "surface_finish"),
        ("craftsmanship", "craftsmanship"),
        ("design_details", "designDetails", "design_details", "visualObservations", "visual_observations"),
        ("wearable_type", "wearableType", "wearable_type"),
        # Jewellery Scale & Reference Accuracy fields (additive — JSR)
        ("size_category", "sizeCategory", "size_category"),
        ("relative_scale", "relativeScale", "relative_scale"),
        ("wear_position", "wearPosition", "wear_position"),
        ("proportion_notes", "proportionNotes", "proportion_notes"),
        ("avoid_generation_errors", "avoidGenerationErrors", "avoid_generation_errors"),
    ]

    for canonical, *candidates in mapping:
        value = _first_value(data, *candidates)
        if value:
            facts[canonical] = value

    return facts


def _build_facts_block(facts: Dict[str, str]) -> str:
    """Layer 1 — structured, authoritative product facts."""
    if not facts:
        return (
            "PRODUCT INTELLIGENCE: The attached reference image contains the "
            "exact product. Reproduce it faithfully; do not invent details."
        )

    labels = {
        "category": "Category",
        "subcategory": "Subcategory",
        "jewellery_type": "Jewellery type",
        "metal": "Metal",
        "stones": "Stones",
        "stone_placement": "Stone placement",
        "shape": "Shape",
        "texture": "Texture",
        "finish": "Finish",
        "craftsmanship": "Craftsmanship",
        "design_details": "Design details",
        "wearable_type": "Wearable type",
        "size_category": "Size category (vs human anatomy)",
        "relative_scale": "Relative scale",
        "wear_position": "Natural wear position",
        "proportion_notes": "Proportion notes",
        "avoid_generation_errors": "Generation errors to avoid",
    }

    lines = ["PRODUCT INTELLIGENCE (AUTHORITATIVE FACTS — DO NOT CHANGE):"]
    for key, label in labels.items():
        if key in facts:
            lines.append(f"- {label}: {facts[key]}")

    return "\n".join(lines)


# ─── Layer 2 — wearing-mode specifics (deterministic, guaranteed) ───────

WEARING_MODE_BLOCKS: Dict[str, str] = {
    "Earring": (
        "WEARING MODE — EARRINGS: The model must be WEARING the earrings: "
        "visible ear with the earrings attached to the earlobe, elegant side "
        "profile, hairstyle suitable for jewellery visibility (pulled back or "
        "swept away), luxury fashion styling. The earrings must be worn — "
        "never held in the hand, never resting on a surface, never in packaging."
    ),
    "Necklace": (
        "WEARING MODE — NECKLACE: The model must be WEARING the necklace: "
        "elegant neck close-up, refined pose, the jewellery area clearly "
        "visible on the neckline, luxury fashion styling. Never held in the "
        "hand, never draped over a card or box."
    ),
    "Pendant": (
        "WEARING MODE — PENDANT: The model must be WEARING the pendant on "
        "its chain: elegant neck close-up, refined pose, the pendant visible "
        "at the collarbone, luxury fashion styling. Never held in the hand."
    ),
    "Chain": (
        "WEARING MODE — CHAIN: The model must be WEARING the chain around "
        "the neck: elegant neck close-up, refined pose, chain clearly visible "
        "against the skin or outfit, luxury fashion styling. Never held."
    ),
    "Ring": (
        "WEARING MODE — RING: The ring must be WORN on a hand: realistic "
        "fingers, premium manicure, elegant hand pose, the ring seated "
        "naturally on the finger. Never floating, never in packaging."
    ),
    "Bracelet": (
        "WEARING MODE — BRACELET: The bracelet must be WORN on the wrist: "
        "elegant hand pose, the bracelet visible around the wrist, luxury "
        "fashion styling. Never held, never in packaging."
    ),
    "Bangle": (
        "WEARING MODE — BANGLE: The bangle must be WORN on the wrist: "
        "elegant hand pose, the bangle visible around the wrist, luxury "
        "fashion styling. Never held, never in packaging."
    ),
    "Watch": (
        "WEARING MODE — WATCH: The watch must be WORN on the wrist: elegant "
        "hand and forearm pose, the watch face clearly visible, luxury "
        "fashion styling. Never held, never in packaging."
    ),
    "Coin": (
        "WEARING MODE — COIN: The coin pendant must be WORN on its chain at "
        "the neckline or displayed on a luxury velvet surface. Never held in "
        "the hand."
    ),
    "Cufflinks": (
        "WEARING MODE — CUFFLINKS: The cufflinks must be WORN in a crisp "
        "shirt cuff: elegant forearm close-up, refined styling. Never held, "
        "never in packaging."
    ),
}

GENERIC_WEARING_BLOCK = (
    "WEARING MODE: The jewellery must be WORN naturally by the model in a "
    "luxury lifestyle setting — it must not be held in the hand, laid on a "
    "card, or shown in packaging."
)

LIFESTYLE_REMOVALS_BLOCK = (
    "LIFESTYLE REMOVALS (strict): Remove jewellery display cards, product labels, "
    "price tags, any text in the image, packaging, hands holding the product, and "
    "all background distractions. No 'Fashion Jewellery' text, no tags, no cards. "
    "The worn jewellery is the only focus — a natural luxury fashion photograph."
)


def _matching_block(
    blocks: Dict[str, str],
    generic: str,
    jewellery_type: str,
    wearable_type: str,
) -> str:
    """Resolve a category-specific block by exact then substring match."""
    block = blocks.get(jewellery_type)
    if not block:
        block = blocks.get(wearable_type)
    if not block:
        for key in blocks:
            if key.lower() in jewellery_type.lower() or key.lower() in wearable_type.lower():
                block = blocks[key]
                break
    return block or generic


def _fitting_rules_block(facts: Dict[str, str]) -> str:
    """Category-based scale & fitting rules (Step 4)."""
    return _matching_block(
        FITTING_RULES,
        GENERIC_FITTING_RULE,
        facts.get("jewellery_type", ""),
        facts.get("wearable_type", ""),
    )


def _build_scale_control_block(facts: Dict[str, str]) -> str:
    """Layer 4 — scale control + analysis-reported errors to avoid."""
    avoid = facts.get("avoid_generation_errors", "")
    if avoid:
        # Cap the injected list so a single oversized field can never dominate
        # the prompt (analysis output is trusted but bounded).
        if len(avoid) > 240:
            avoid = avoid[:237].rstrip() + "..."
        return f"{SCALE_CONTROL_BLOCK}\nAVOID AT ALL COSTS: {avoid}."
    return SCALE_CONTROL_BLOCK


def _wearing_mode_block(facts: Dict[str, str]) -> str:
    """Build the deterministic wearing-mode instructions for lifestyle mode.

    Includes the strict lifestyle removals (no cards, labels, text, packaging,
    hands holding the product) and, when scale control is enabled, the
    category-based fitting rules so the jewellery sits naturally on the body.
    """
    block = _matching_block(
        WEARING_MODE_BLOCKS,
        GENERIC_WEARING_BLOCK,
        facts.get("jewellery_type", ""),
        facts.get("wearable_type", ""),
    )

    parts = [block, LIFESTYLE_REMOVALS_BLOCK]
    if settings.PFIE_SCALE_CONTROL_ENABLED:
        parts.append(_fitting_rules_block(facts))

    return "\n".join(parts)


# ─── Layer 2 — template creative direction (zero-token fallback) ────────


def _creative_direction_via_template(
    category: str,
    mode: str,
    facts: Dict[str, str],
) -> str:
    """Deterministic creative direction used when ChatGPT is unavailable."""
    mode_lead = (
        "Lifestyle/wearing editorial photography: the product is worn "
        "naturally by an elegant model in a luxury setting."
        if mode == "lifestyle"
        else "Professional studio product photography."
    )

    category_direction: Dict[str, str] = {
        "professionalShot": (
            "Scene: clean premium studio set with a minimal surface that "
            "complements the metal tone. Lighting: soft key light with "
            "controlled shadows that trace the craftsmanship. Camera: 50mm "
            "f/2.8 macro lens, shallow depth of field, hero angle at 45 "
            "degrees with balanced negative space. Composition: product "
            "centered, editorial crop. Commercial, high-end e-commerce look."
        ),
        "useCaseShot": (
            "Scene: an authentic luxury everyday setting matching the "
            "product's use. Lighting: soft natural window light or golden "
            "hour. Camera: 50mm f/2.2, natural depth of field. Composition: "
            "only the necessary body parts (ear, neck, hand, wrist) in "
            "frame so the product stays the sharp, well-lit focal point. "
            "Warm, authentic color grading."
        ),
        "ingredientStory": (
            "Scene: an artisan workspace (workbench, craft studio) with the "
            "finished product in hero foreground lighting and softly blurred "
            "raw materials behind. Lighting: single warm directional "
            "workshop light. Camera: 85mm f/2.0 macro-capable, shallow depth "
            "of field. Composition: process elements under 40% of visual "
            "weight, warm earthy palette."
        ),
        "festive": (
            "Scene: a secular Indian festive setting (decorated courtyard, "
            "twinkling terrace, rangoli-lined doorway) with diyas, string "
            "lights and marigolds. Lighting: vibrant festival mood, product "
            "well-lit and clearly visible. Camera: 50mm f/2.0, candid "
            "slightly off-center composition. STRICT: no religious idols, "
            "deities, altars, or temple interiors."
        ),
        "transformation": (
            "Scene: clean split-frame (50/50) with the SAME model in two "
            "emotional states — cooler muted 'before' and warmer vibrant "
            "'after' with the product visibly worn. Camera: 50mm f/2.5, "
            "identical framing, outfit and hairstyle across both halves. "
            "Subtle, real expressions; no labels or arrows."
        ),
        "scaleReference": (
            "Scene: clean minimal neutral background (light grey or soft "
            "white) with the product beside ONE familiar reference object. "
            "Lighting: even, shadow-minimal e-commerce light. Camera: 50mm "
            "at f/8 for full sharpness, eye-level or slight 3/4 top-down. "
            "Geometrically accurate proportions; no rulers or labels."
        ),
        "complementaryShot": (
            "Scene: a real textural surface (sunlit wooden table, marble "
            "counter, linen desk) with the product as the 60/40 primary "
            "subject beside one natural companion item. Lighting: soft "
            "directional window light favoring the product. Camera: 50mm "
            "f/2.8, shallow-to-moderate depth of field, three-quarter or "
            "top-down angle."
        ),
        "ugcStyle": (
            "Scene: a real everyday location (kitchen counter, café table, "
            "bedroom windowsill) with 1-3 authentic clutter elements. "
            "Lighting: ONLY natural daylight — no studio light. Camera: "
            "smartphone simulation with slightly compressed dynamic range, "
            "imperfect off-center framing, natural color temperature. Must "
            "not look like a professional advertisement."
        ),
    }

    direction = category_direction.get(
        category, category_direction["professionalShot"]
    )

    return f"{mode_lead} {direction}"


# ─── Layer 2 — ChatGPT creative direction ───────────────────────────────


async def _creative_direction_via_chatgpt(
    facts: Dict[str, str],
    category: str,
    mode: str,
    aspect_ratio: str,
) -> Tuple[Optional[str], int]:
    """Call ChatGPT (OpenAI chat completions) as the Creative Director.

    Returns ``(direction_text, tokens_consumed)``. Returns ``(None, 0)``
    on any failure so the caller falls back to templates.
    """
    try:
        from openai import AsyncOpenAI
    except ImportError:
        logger.warning("PFIE: openai package not installed — using template fallback")
        return None, 0

    if not settings.OPENAI_API_KEY:
        logger.info("PFIE: OPENAI_API_KEY not configured — using template fallback")
        return None, 0

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        mode_guidance = (
            LIFESTYLE_MODE_GUIDANCE if mode == "lifestyle" else STUDIO_MODE_GUIDANCE
        )
        system_prompt = f"{CREATIVE_DIRECTOR_SYSTEM_PROMPT}\n\n{mode_guidance}"

        scale_keys = (
            "size_category",
            "relative_scale",
            "wear_position",
            "proportion_notes",
            "avoid_generation_errors",
        )
        scale_facts = {k: v for k, v in facts.items() if k in scale_keys}

        user_payload = {
            "campaign_category": PROMPT_CATEGORY_LABELS.get(category, category),
            "mode": mode,
            "aspect_ratio": aspect_ratio,
            "authoritative_product_facts": facts or {"note": "Attached reference image only — describe the scene without inventing product details."},
            "scale_and_fitting": scale_facts
            or {
                "note": "Preserve real-world jewellery proportions — never enlarge, shrink, or redesign the product."
            },
        }

        # AsyncOpenAI's create() is already a coroutine — await directly.
        response = await client.chat.completions.create(
            model=settings.PFIE_CREATIVE_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Create the creative direction for this campaign. "
                        "The product facts are authoritative — never change "
                        "or invent any of them. Only describe scene, "
                        "lighting, camera, composition, fashion direction "
                        "and lifestyle instructions.\n\n"
                        f"{json.dumps(user_payload, ensure_ascii=False)}"
                    ),
                },
            ],
            temperature=settings.PFIE_CREATIVE_TEMPERATURE,
            max_tokens=350,
        )

        direction = response.choices[0].message.content if response.choices else None
        tokens = 0
        if response.usage:
            tokens = int(
                (response.usage.prompt_tokens or 0)
                + (response.usage.completion_tokens or 0)
            )

        if not direction or not direction.strip():
            logger.warning("PFIE: ChatGPT returned empty creative direction")
            return None, tokens

        logger.info(
            f"PFIE: ChatGPT creative direction received "
            f"model={settings.PFIE_CREATIVE_MODEL} tokens={tokens}"
        )
        return direction.strip(), tokens

    except Exception as e:
        logger.warning(
            f"PFIE: ChatGPT creative direction failed ({e}) — "
            f"using template fallback"
        )
        return None, 0


# ─── Fusion engine ──────────────────────────────────────────────────────


class PromptFusionEngine:
    """Fuses product facts + creative direction + preservation + enhancement.

    Usage::

        engine = PromptFusionEngine()
        result = await engine.fuse(
            product_intelligence={...},
            category="professionalShot",
            mode="studio",
            aspect_ratio="4:5",
        )
    """

    async def fuse(
        self,
        product_intelligence: Optional[Dict[str, Any]],
        category: str = "professionalShot",
        mode: str = "studio",
        aspect_ratio: str = "4:5",
        request_id: str = "unknown",
    ) -> Dict[str, Any]:
        """Run the full fusion pipeline and return the final prompt."""
        start_time = time.time()
        category = category if category in PROMPT_CATEGORIES else "professionalShot"
        mode = mode if mode in ("studio", "lifestyle") else "studio"

        facts = _normalise_facts(product_intelligence or {})

        logger.info(
            f"PFIE fusion starting request_id={request_id} "
            f"category={category} mode={mode} "
            f"facts={len(facts)}"
        )

        # ── Layer 2 — creative direction (ChatGPT, template fallback) ──
        source = "template"
        tokens_consumed = 0
        creative_direction = None
        if settings.PFIE_ENABLED:
            creative_direction, tokens_consumed = await _creative_direction_via_chatgpt(
                facts, category, mode, aspect_ratio
            )
            if creative_direction:
                source = "chatgpt"

        if not creative_direction:
            creative_direction = _creative_direction_via_template(
                category, mode, facts
            )

        # ── Assemble layers ───────────────────────────────────────────
        layers: List[Dict[str, str]] = [
            {"name": "product_facts", "content": _build_facts_block(facts)},
            {"name": "creative_direction", "content": creative_direction},
            {"name": "product_preservation", "content": PRODUCT_PRESERVATION_BLOCK},
            {"name": "photography_enhancement", "content": ENHANCEMENT_BLOCK},
        ]

        if settings.PFIE_SCALE_CONTROL_ENABLED:
            layers.insert(
                3,
                {
                    "name": "scale_control",
                    "content": _build_scale_control_block(facts),
                },
            )

        if mode == "lifestyle":
            layers.insert(2, {"name": "wearing_mode", "content": _wearing_mode_block(facts)})

        # ── Fuse into a single prompt ─────────────────────────────────
        fused_parts = [layer["content"] for layer in layers]
        fused_parts.append(REFERENCE_IMAGE_INSTRUCTION)
        fused_parts.append(f"Aspect ratio: {aspect_ratio}.")
        fused_parts.append(f"Mode: {mode.capitalize()}.")

        final_prompt = "\n\n".join(fused_parts)

        elapsed = (time.time() - start_time) * 1000
        logger.info(
            f"PFIE fusion complete request_id={request_id} "
            f"source={source} tokens={tokens_consumed} "
            f"time={elapsed:.0f}ms prompt_len={len(final_prompt)}"
        )

        return {
            "success": True,
            "prompt": final_prompt,
            "layers": layers,
            "source": source,
            "tokens_consumed": tokens_consumed,
            "generation_time_ms": elapsed,
        }


def fusion_health() -> Dict[str, Any]:
    """Health/status info for the fusion engine."""
    return {
        "status": "ready",
        "service": "prompt-fusion-engine",
        "enabled": settings.PFIE_ENABLED,
        "creative_model": settings.PFIE_CREATIVE_MODEL,
        "creative_director": "chatgpt" if settings.OPENAI_API_KEY else "template",
        "layers": [
            "product_facts",
            "creative_direction",
            "wearing_mode",
            "product_preservation",
        ]
        + (["scale_control"] if settings.PFIE_SCALE_CONTROL_ENABLED else [])
        + ["photography_enhancement"],
        "scale_control_enabled": settings.PFIE_SCALE_CONTROL_ENABLED,
    }
