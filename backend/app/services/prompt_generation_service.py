"""Prompt generation service — local template engine.

ZERO Gemini API calls. Takes the ALREADY-EXISTING Gemini Analysis result
(from the database) and maps it to the 8 promotional prompt categories
using deterministic template strings.

Phase 1 and Phase 2 (Gemini calls) have been REMOVED.
Token consumption: ZERO (no API calls).

Reuses the n8n workflow's 8 prompt category structure and intent,
but generates prompts client-side / server-side using templates.
"""

import time
from typing import Any, Dict, Optional

from app.utils.logger import logger

# ── Helpers ─────────────────────────────────────────────────


def _esc(v: str) -> str:
    return v.replace('"', '\\"').replace("\n", " ")


def _build_workflow_analysis(analysis: Dict[str, Any]) -> Dict[str, str]:
    """Map existing DB analysis record to n8n 11-field workflow format."""
    material = _esc(str(analysis.get("material", "")))
    gold_purity = _esc(str(analysis.get("gold_purity", "")))
    category = _esc(str(analysis.get("category", "")))
    style = _esc(str(analysis.get("style", "")))
    era = _esc(str(analysis.get("era", "")))
    condition = _esc(str(analysis.get("condition", "")))
    summary = _esc(str(analysis.get("summary", "")))
    weight = analysis.get("weight", 0) or 0
    estimated_price = analysis.get("estimated_price", 0) or 0
    confidence = analysis.get("confidence", 0) or 0.85
    gemstones_raw = analysis.get("gemstones", "")

    # Parse gemstones
    import json
    gemstones = []
    if gemstones_raw:
        try:
            gemstones = json.loads(gemstones_raw) if isinstance(gemstones_raw, str) else gemstones_raw
        except (json.JSONDecodeError, TypeError):
            gemstones = []
    gem_str = ", ".join(str(g) for g in gemstones[:3] if g != "None Detected" and g != "Unknown")

    # Product Identity
    purity_hint = f"{gold_purity} " if gold_purity else ""
    gem_hint = f" with {gem_str}" if gem_str else ""
    product_identity = f"{purity_hint}{material} {category}{gem_hint}".strip()

    # Material Properties
    material_properties = f"{material}. {gold_purity}. Style: {style}. Era: {era}. Condition: {condition}."

    # Scale and Proportion
    weight_hint = f"Estimated weight: {weight}g. " if weight else ""
    scale_and_proportion = f"{weight_hint}Designed with balanced proportions and ergonomic consideration for its category."

    # Design Style
    design_style = f"{style} {era}".strip() or "Contemporary"

    # Visual Craftsmanship
    visual_craftsmanship = f"Execution: {condition or 'Excellent'}. {summary or 'Well-crafted piece with attention to detail.'}"

    # Target Demographic
    target_demographic = _get_demographic(material, gold_purity, estimated_price)

    # Psychographics
    psychographics = _get_psychographics(estimated_price, style)

    # Functional Utility
    functional_utility = _get_utility(category)

    # Lifestyle Branding
    lifestyle_branding = _get_branding(estimated_price, material)

    # Indian Festive Context
    indian_festive_context = _get_festive_context(material, style, gold_purity)

    # Market Readiness
    market_readiness = (
        f"Confidence score: {confidence * 100:.0f}%. "
        f"Condition: {condition or 'Excellent'}. "
        f"{'Positioned in the premium segment.' if estimated_price > 500 else 'Competitively positioned for the gifting market.'} "
        f"Strong commercial viability in the Indian corporate gifting and premium retail markets."
    )

    return {
        "productIdentity": product_identity,
        "materialProperties": material_properties,
        "scaleAndProportion": scale_and_proportion,
        "designStyle": design_style,
        "visualCraftsmanship": visual_craftsmanship,
        "targetDemographic": target_demographic,
        "psychographics": psychographics,
        "functionalUtility": functional_utility,
        "lifestyleBranding": lifestyle_branding,
        "indianFestiveContext": indian_festive_context,
        "marketReadiness": market_readiness,
    }


def _get_demographic(material: str, purity: str, price: float) -> str:
    if price > 5000 or "gold" in material.lower():
        return "Affluent professionals, senior executives, established entrepreneurs aged 35-60 with a refined appreciation for quality"
    if price > 1000 or "silver" in material.lower():
        return "Career professionals, managers, urban millennials aged 28-45 with disposable income"
    return "Everyday consumers, gift buyers, young professionals aged 22-35 seeking quality and value"


def _get_psychographics(price: float, style: str) -> str:
    if price > 5000:
        return "Value exclusivity, heritage, and craftsmanship. Purchasing decisions driven by rarity, investment potential, and status signaling."
    if price > 1000:
        return "Appreciate quality and design. Seek products that reflect their success and taste. Value brand reputation and enduring style."
    return "Practical, trend-aware consumers who prioritize value and versatility. Decisions influenced by recommendations and social proof."


def _get_utility(category: str) -> str:
    cat_lower = category.lower()
    if "ring" in cat_lower:
        return "Finger adornment, personal expression, milestone marking, and everyday elegance"
    if "necklace" in cat_lower or "pendant" in cat_lower or "chain" in cat_lower:
        return "Neckline enhancement, pendant display, layering piece for both casual and formal occasions"
    if "earring" in cat_lower:
        return "Facial framing, style accentuation, from subtle studs to statement drops for all occasions"
    if "bracelet" in cat_lower or "bangle" in cat_lower:
        return "Wrist accent, stackable fashion piece, subtle sophistication for professional and social settings"
    if "watch" in cat_lower:
        return "Timekeeping, status statement, daily utility with heritage value"
    return "Personal adornment, style enhancement, and lifestyle complement"


def _get_branding(price: float, material: str) -> str:
    if price > 5000 or "gold" in material.lower():
        return "A signature of discernment and success. Elevates any ensemble from merely stylish to memorably distinctive."
    if price > 1000:
        return "Refined taste made tangible. Communicates quiet confidence and appreciation for quality craftsmanship."
    return "Everyday elegance. Transitions seamlessly from professional to social settings, adding polish to life's moments."


def _get_festive_context(material: str, style: str, purity: str) -> str:
    is_gold = "gold" in material.lower() or "k" in purity
    is_traditional = any(s in style.lower() for s in ["traditional", "vintage", "classic", "antique", "temple", "jadtar"])
    festive_note = "Gold is particularly auspicious during Diwali, Akshaya Tritiya, and wedding seasons" if is_gold else "Versatile for all festive occasions including Diwali gifting, weddings, and corporate celebrations"
    style_note = "Traditional designs resonate strongly during festive seasons." if is_traditional else "Contemporary designs appeal to modern festive gifting preferences."
    return f"Highly suitable for the Indian festive and gifting market. {festive_note}. {style_note}"


# ── Prompt Template Functions ─────────────────────────────


# --- Product Preservation Constraints --------------------------
# The canonical fidelity constraints are defined in app.ai.product_fidelity
# (single source of truth).  Import here for backward compatibility so that
# any external code referencing this modules PRODUCT_PRESERVATION_CONSTRAINTS
# continues to work unchanged.
from app.ai.product_fidelity import (
    PRODUCT_PRESERVATION_CONSTRAINTS,
)


def _generate_professional_shot(wa: Dict[str, str]) -> str:
    return (
        f"Professional product photography. {_esc(wa['productIdentity'])} presented in a premium studio setting. "
        f"Scene concept: {_esc(wa['designStyle'])} aesthetic with {_esc(wa['materialProperties'])}. "
        f"Background: clean, minimal surface complementing the product's material qualities. "
        f"Studio lighting with controlled shadows highlighting texture and craftsmanship. "
        f"Composition: hero angle at 45 degrees, product centered with balanced negative space for text overlay. "
        f"Color palette: complementary tones derived from {_esc(wa['lifestyleBranding'])}. "
        f"Camera: 50mm f/2.8 macro lens, shallow depth of field for product isolation. "
        f"High resolution, sharp focus on product details. No text, no watermarks, no human models. "
        f"Aspect ratio 4:5. "
        f"{PRODUCT_PRESERVATION_CONSTRAINTS}"
    )


def _generate_use_case_shot(wa: Dict[str, str]) -> str:
    return (
        f"Lifestyle product-in-use photography. A person naturally using {_esc(wa['productIdentity'])} "
        f"in an authentic everyday setting. The subject, aligned with {_esc(wa['targetDemographic'])}, "
        f"is shown engaging with the product in a genuine moment of use. "
        f"Scene: a realistic environment matching the product's functional context. "
        f"The product is the clear focal point: sharp focus, well-lit, positioned prominently. "
        f"Natural lighting (soft window light or golden hour). Framing shows only necessary body parts "
        f"to keep focus on the product. 1-3 minimal props for context. Camera: 50mm f/2.2, natural depth of field. "
        f"Warm, authentic color grading. No product obscured, no motion blur, no stock-photo stiffness. "
        f"Aspect ratio 4:5. "
        f"{PRODUCT_PRESERVATION_CONSTRAINTS}"
    )


def _generate_ingredient_story(wa: Dict[str, str]) -> str:
    return (
        f"Craft and provenance storytelling photography. {_esc(wa['productIdentity'])} shown alongside its "
        f"raw material origin story. Foreground: the finished product in sharpest focus, hero lighting. "
        f"Background (softly blurred): the raw materials and craft process that created it. "
        f"The visual narrative implies 'this became that' through a deliberate compositional link "
        f"(shared lighting, color echo, or diagonal line). Process elements occupy no more than 40% of visual weight. "
        f"Setting: authentic workspace (workbench, artisan table, craft studio). "
        f"Warm, earthy, handmade color palette. Single warm directional light (workshop window or work-lamp). "
        f"Camera: 85mm f/2.0 macro-capable, shallow depth of field. No human hands unless essential and blurred. "
        f"No text or watermarks. Aspect ratio 4:5. "
        f"{PRODUCT_PRESERVATION_CONSTRAINTS}"
    )


def _generate_festive(wa: Dict[str, str]) -> str:
    return (
        f"Indian festive campaign photography. {_esc(wa['productIdentity'])} within the vibrant atmosphere "
        f"of an Indian festival, aligned with {_esc(wa['indianFestiveContext'])}. "
        f"A model matching {_esc(wa['targetDemographic'])} is shown in a candid festive moment — "
        f"mid-laugh, mid-gesture, or mid-celebration — wearing or holding the product naturally. "
        f"The product is well-lit and clearly visible but not dominant. "
        f"Environment: secular festive setting (decorated courtyard, twinkling-light terrace, rangoli-lined doorway). "
        f"Non-religious festive props only: diyas (decorative), string lights, marigold garlands, color powder. "
        f"Vibrant festival-appropriate palette. Candid, slightly off-center composition. Camera: 50mm f/2.0. "
        f"STRICT CONSTRAINT: NO religious idols, deities, murtis, altars, or temple interiors anywhere. "
        f"No text, no watermarks. No more than 2 people in frame. Aspect ratio 4:5. "
        f"{PRODUCT_PRESERVATION_CONSTRAINTS}"
    )


def _generate_transformation(wa: Dict[str, str]) -> str:
    return (
        f"Before/after emotional transformation photography. A clean split-frame composition (50/50 vertical divide, "
        f"soft gradient transition) showing the SAME model in two emotional states, separated only by the presence "
        f"of {_esc(wa['productIdentity'])}. BEFORE half (left): cooler, flatter lighting; model's expression neutral "
        f"or subdued. Product not present. AFTER half (right): warmer, richer lighting; model's expression bright "
        f"and confident. Product visibly in use/worn/held. Model's appearance, outfit, hairstyle, and framing "
        f"are IDENTICAL across both halves — only expression, posture, and energy change. "
        f"Environment is the same in both halves. Camera: 50mm f/2.5, consistent framing. "
        f"No text, no labels, no arrows. Before palette: muted, cool. After palette: vibrant, warm. "
        f"No theatrical expressions — subtle and real. Aspect ratio 4:5. "
        f"{PRODUCT_PRESERVATION_CONSTRAINTS}"
    )


def _generate_scale_reference(wa: Dict[str, str]) -> str:
    return (
        f"Scale accuracy product photography. {_esc(wa['productIdentity'])} shown alongside a single familiar "
        f"reference object for true size comparison. GEOMETRICALLY ACCURATE proportions — no artistic size "
        f"exaggeration or minimization. Product and reference on the same focal plane. "
        f"Background: clean, minimal, softly neutral (light grey or soft white). "
        f"Even, shadow-minimal e-commerce lighting. Eye-level or slight 3/4 top-down angle. "
        f"Camera: 50mm at f/8 for full sharpness across both elements. Neutral, true-to-life color accuracy. "
        f"No text, no measurement labels, no rulers, no grid overlays. Only one reference object. "
        f"Aspect ratio 4:5 or 1:1. "
        f"{PRODUCT_PRESERVATION_CONSTRAINTS}"
    )


def _generate_complementary_shot(wa: Dict[str, str]) -> str:
    return (
        f"Lifestyle still-life pairing photography. {_esc(wa['productIdentity'])} positioned alongside its "
        f"most natural real-world companion item. The product is the clear primary subject (roughly 60/40 "
        f"visual weight), in sharper focus and brighter light. The companion item sits behind or beside, "
        f"slightly softer in focus, natural and incidental. Surface: a real, textural setting (sunlit wooden "
        f"table, marble counter, linen desk). Soft, natural-feeling directional light favoring the product. "
        f"Three-quarter or slight top-down angle. No human model by default. Color palette complementary "
        f"to the product. Camera: 50mm f/2.8, shallow-to-moderate depth of field. "
        f"No second unit or variant of the product. Only one companion item. No text or watermarks. "
        f"Aspect ratio 4:5. "
        f"{PRODUCT_PRESERVATION_CONSTRAINTS}"
    )


def _generate_ugc_style(wa: Dict[str, str]) -> str:
    return (
        f"User-generated content style photography. {_esc(wa['productIdentity'])} photographed casually "
        f"on a smartphone by an everyday customer. NOT a professional photo. "
        f"Setting: a real everyday location (kitchen counter, study desk, café table, bedroom windowsill). "
        f"ONLY natural daylight — NO studio lighting, no softboxes, no artificial fill. "
        f"Smartphone camera simulation: slightly compressed dynamic range, mild oversharpening. "
        f"Imperfect composition: off-center framing, product slightly tilted. 1-3 authentic environmental "
        f"elements (coffee mug, phone charger, keys, book) — real-life clutter, not styled props. "
        f"Product remains the clear subject — foreground, well-lit, in focus. "
        f"Natural, slightly inconsistent color temperature. Phone-camera depth of field. "
        f"Aspect ratio 1:1 (social post-native). No studio lighting, no professional color grading, "
        f"no text, no filters. Must NOT look like a professional advertisement. "
        f"{PRODUCT_PRESERVATION_CONSTRAINTS}"
    )


# ── Main Service ────────────────────────────────────────────


class PromptGenerationService:
    """Generates promotional prompts from an existing analysis result.

    Uses deterministic template strings — ZERO Gemini API calls.
    Takes the already-existing analysis data from the database,
    maps it to the n8n 11-field workflow format, then generates
    all 8 prompt categories using template functions.

    Token consumption: ZERO (no API calls).
    """

    async def generate_prompts(
        self,
        analysis_data: Dict[str, Any],
        description: str = "",
        request_id: str = "unknown",
    ) -> Dict[str, Any]:
        """Run prompt generation using existing analysis data.

        Args:
            analysis_data: Dict of analysis fields from the DB record.
            description: Optional consumer-provided description.
            request_id: Traceability ID.

        Returns:
            Dict with success status, workflow analysis, and generated prompts.
        """
        start_time = time.time()
        logger.info(
            f"PromptGenerationService (local engine) starting "
            f"request_id={request_id}"
        )

        try:
            # Step 1: Map existing analysis data to n8n workflow format
            workflow_data = _build_workflow_analysis(analysis_data)

            logger.info(
                f"Mapped to workflow format: Product={workflow_data.get('productIdentity', '')[:60]} "
                f"request_id={request_id}"
            )

            # Step 2: Generate all 8 prompts using local template functions
            prompts = {
                "professionalShot": _generate_professional_shot(workflow_data),
                "useCaseShot": _generate_use_case_shot(workflow_data),
                "ingredientStory": _generate_ingredient_story(workflow_data),
                "festive": _generate_festive(workflow_data),
                "transformation": _generate_transformation(workflow_data),
                "scaleReference": _generate_scale_reference(workflow_data),
                "complementaryShot": _generate_complementary_shot(workflow_data),
                "ugcStyle": _generate_ugc_style(workflow_data),
            }

            elapsed = (time.time() - start_time) * 1000
            logger.info(
                f"Prompt generation completed: 8 prompts "
                f"request_id={request_id} time={elapsed:.0f}ms "
                f"tokens_consumed=0 (local engine)"
            )

            return {
                "success": True,
                "workflow_analysis": workflow_data,
                "prompts": prompts,
                "generation_time_ms": elapsed,
            }

        except Exception as e:
            logger.error(f"Prompt generation failed: {e} request_id={request_id}")
            return {
                "success": False,
                "error": f"Prompt generation failed: {str(e)}",
                "generation_time_ms": (time.time() - start_time) * 1000,
            }
