"""Amazon India — Fashion Jewellery Earrings Main/Product Image Presentation.

Defines presentation-only instructions for the Amazon India marketplace's
main product image for fashion jewellery earrings.

IMPORTANT: This module controls ONLY presentation and compliance:
background, composition, framing, lighting, and exclusion lists.

It MUST NOT redefine or modify:
- stone count, shape, placement, colour
- metal identity, colour, finish
- product geometry, proportions
- attachment mechanism, decorative elements
- product design

Product identity is governed exclusively by the Master Product Fidelity layer.

Rules are separated into:

A. OFFICIAL / MANDATORY
   Rules that align with Amazon India's published style guide for
   main product images.

B. OFFICIAL RECOMMENDATION / BEST PRACTICE
   Guidelines that are recommended best practice but not always
   strictly enforced.

C. GEMVISION INTERNAL TARGET
   Internal quality targets that exceed Amazon's minimum requirements
   for professional-grade output.
"""

from app.ai.marketplaces import MarketPlacePresentation


# ─── Amazon India Fashion Jewellery — Earrings Main Image ───────────────

AMAZON_INDIA_EARRINGS_MAIN_IMAGE = MarketPlacePresentation(
    marketplace_id="amazon_india_fashion_earrings",
    default_aspect_ratio="1:1",
    prompt_block=(
        "AMAZON INDIA — MAIN PRODUCT IMAGE (PRESENTATION ONLY):\n"
        "\n"
        "A. OFFICIAL / MANDATORY:\n"
        "• Pure white background — RGB 255, 255, 255. No gradient, no texture, "
        "no shadow on the background itself.\n"
        "• No human model, mannequin, or body part in the frame. "
        "The earrings must be shown standalone.\n"
        "• No props, packaging, display cards, price tags, or lifestyle "
        "elements in the frame.\n"
        "• No text, logos, watermarks, promotional badges, borders, or "
        "overlays anywhere in the image.\n"
        "• The product must be clearly visible, fully in frame, and sharply "
        "in focus across the entire item.\n"
        "• The image must represent the actual product — not an illustration, "
        "render, or artistic interpretation.\n"
        "\n"
        "B. OFFICIAL RECOMMENDATION / BEST PRACTICE:\n"
        "• Square 1:1 aspect ratio — Amazon's standard format for main product "
        "images.\n"
        "• Product centred in the frame with balanced spacing.\n"
        "• Even, controlled studio lighting — no harsh shadows, no mixed "
        "colour temperatures.\n"
        "• Accurate metal colour representation — true to the reference.\n"
        "• Clean e-commerce packshot style — professional and minimal.\n"
        "\n"
        "C. GEMVISION INTERNAL TARGET:\n"
        "• Target resolution: 2000 × 2000 px.\n"
        "• Strong product occupancy — product should fill the majority of "
        "the frame (recommended above 85% of image area).\n"
        "• Professional studio-quality sharpness and lighting.\n"
        "• Background must be clean, flat white with no visible edges or "
        "vignetting.\n"
        "\n"
        "CRITICAL: This is a PRESENTATION task. The exact jewellery design "
        "from the reference image must remain completely unchanged. Do NOT "
        "add, remove, or alter any product details."
    ),
    metadata={
        "marketplace": "Amazon India",
        "category": "Fashion Jewellery",
        "subcategory": "Earrings",
        "image_type": "Main / Product Image",
        "mandatory_rules_count": 6,
        "recommendation_rules_count": 5,
        "internal_target_rules_count": 4,
    },
)


def get_amazon_india_earrings_presentation() -> MarketPlacePresentation:
    """Return the Amazon India fashion jewellery earrings main image presentation."""
    return AMAZON_INDIA_EARRINGS_MAIN_IMAGE
