// ============================================================
// promotional-prompts.ts — Clean Visual Prompt Compiler
// MORAA GemVision
// ============================================================
// Compiles clean, visually actionable prompts for the 8
// Promotional image generators. Strips marketing metadata,
// demographic descriptions, and campaign copy.
//
// This module is PROMOTIONAL-ONLY. It does not affect
// Prompt 1 or Prompt 2.
// ============================================================

import type { PromptCategory } from "@/types/prompts";

// ─── Product Fidelity Block ────────────────────────────────
// Appended to every promotional prompt to ensure the
// jewellery product is preserved exactly.

const PRODUCT_FIDELITY_BLOCK = `
PRODUCT FIDELITY — HIGHEST PRIORITY (NON-NEGOTIABLE):
The uploaded reference image is the sole authoritative source for the jewellery product.
Preserve the exact visible earring without redesign, reinterpretation, beautification,
simplification, or creative reconstruction.
Preserve: exact shape, geometry, metal colour, metal finish, gemstone count, gemstone
placement, gemstone cut, stone colours, bead count, bead arrangement, hooks, loops,
connectors, dangling elements, relative proportions, drop length, and component
relationships.
Do not add, remove, substitute, merge, split, recolour, resize, or invent any jewellery
component. If presentation conflicts with product fidelity, preserve product fidelity.`.trim();

// ─── Negative Constraints Block ────────────────────────────
// Common negative constraints for all promotional categories.

const COMMON_NEGATIVE = `
DO NOT:
- Redesign or alter the jewellery in any way
- Add or remove gemstones, beads, or components
- Change metal colour, finish, or material
- Change gemstone cuts, shapes, or colours
- Create generic "similar" jewellery
- Include text, watermarks, or logos
- Use low resolution or oversaturated colours`.trim();

// ─── Clean Visual Prompts ──────────────────────────────────
// Each category has a clean, visually actionable prompt
// with NO marketing metadata, NO demographic descriptions,
// and NO campaign copy.

const CLEAN_VISUAL_PROMPTS: Record<PromptCategory, string> = {
  professionalShot: `Editorial luxury studio jewelry photograph. The exact reference earring is the primary subject, resting elegantly on a minimalist neutral textured stone block. Soft diffused architectural studio lighting with subtle soft shadows. 45-degree hero angle, balanced negative space, high-end jewelry commercial look. Crisp metallic surface and gemstone facets. Clean background, no people, no text. Aspect ratio 4:5.

NEGATIVE: human model, face, hands, clutter, text, watermark, low quality, oversaturated, redesigned jewelry, altered gemstones, missing components.`,

  useCaseShot: `Editorial lifestyle close-up of an elegant woman naturally wearing the exact reference earring on her ear. Side-profile framing focused on the lower jawline, neck and earlobe. Natural realistic skin texture. Soft natural morning window light, subtle warm tones, shallow depth of field. Authentic premium lifestyle photography. Aspect ratio 4:5.

NEGATIVE: distorted jewelry, floating earring, cartoon, oversaturated, full body, studio backdrop, redesigned jewelry, missing components.`,

  ingredientStory: `Fine jewelry workshop storytelling photograph. The exact reference earring is the sharp foreground subject. In the softly blurred background, an artisan jeweler workbench contains delicate gold wire, tweezers and loose uncut gemstones under a warm directional worklamp. Rich amber and wood tones, authentic craft studio aesthetic. Aspect ratio 4:5.

NEGATIVE: deformed tools, messy trash, digital drawings, low resolution, text, watermark, redesigned jewelry, altered gemstones.`,

  festive: `Warm Indian festive lifestyle campaign photograph. An elegant Indian woman captured naturally during a twilight terrace celebration, wearing the exact reference earrings. Warm glowing fairy lights and decorative brass diyas are softly blurred in the background. Candid celebration mood, rich festive colour palette, authentic realistic photography. No religious idols or temple interiors. Aspect ratio 4:5.

NEGATIVE: isolated product, plain white background, religious idols, murtis, temple altars, floating jewelry, distorted anatomy, redesigned jewelry.`,

  transformation: `Editorial split-concept comparison of the same stylish woman. Balanced side-by-side framing: left side has neutral subdued lighting and expression without accessories; right side has warm golden lighting, a genuine radiant smile and the exact reference earrings naturally worn. Clean continuous studio background, realistic seamless mood transition, premium fashion editorial photography. Aspect ratio 4:5.

NEGATIVE: text labels, before-after text, arrows, split lines, caricature, exaggerated facial expression, redesigned jewelry.`,

  scaleReference: `Clean product scale-reference photograph. The exact reference earring rests delicately in an open manicured human palm for realistic size and proportion reference. Soft neutral lighting, clean off-white background, sharp focus across hand and earring, natural skin texture, true-to-life scale. Aspect ratio 4:5.

NEGATIVE: deformed fingers, extra fingers, cartoonish hand, oversized jewelry, text, rulers, grid lines, redesigned jewelry, altered proportions.`,

  complementaryShot: `Curated luxury still-life flat lay. The exact reference earring is the focal piece on a warm sunlit marble vanity tray, naturally paired beside a minimalist glass perfume bottle and fine silk scrunchie. Soft natural daylight casting delicate shadows, modern quiet luxury aesthetic. Visual weight strongly favours the jewellery. Aspect ratio 4:5.

NEGATIVE: multiple earrings, clutter, low quality, harsh shadows, human model, redesigned jewelry, extra jewellery.`,

  ugcStyle: `Authentic customer unboxing smartphone photograph. The exact reference earring rests casually on a cozy wooden café table next to an iced coffee glass and an open notebook. Natural ambient daylight, slightly candid off-centre amateur framing, authentic mobile-camera depth of field, real-world everyday lighting, completely unstaged feel. Aspect ratio 1:1.

NEGATIVE: professional studio lighting, 3D render, digital illustration, commercial backdrop, blurry product, redesigned jewelry, additional jewelry.`,
};

// ─── Duplicate Product Name Normalizer ─────────────────────
// Prevents artifacts like "Rose Gold Rose Gold Earring with Pearl"

function normalizeProductName(name: string): string {
  // Split into words and remove consecutive duplicates
  const words = name.split(/\s+/);
  const normalized: string[] = [];
  for (const word of words) {
    if (normalized.length === 0 || normalized[normalized.length - 1].toLowerCase() !== word.toLowerCase()) {
      normalized.push(word);
    }
  }
  return normalized.join(" ");
}

// ─── Public API ────────────────────────────────────────────

/**
 * Get the clean visual prompt for a promotional category.
 *
 * This returns a visually actionable prompt with:
 * - Clean scene description
 * - Product fidelity instructions
 * - Negative constraints
 * - NO marketing metadata
 * - NO demographic descriptions
 * - NO campaign copy
 *
 * @param category - The promotional prompt category
 * @param productIdentity - The product identity string (will be normalized for duplicates)
 * @returns The clean visual prompt ready for image generation
 */
export function getCleanVisualPrompt(
  category: PromptCategory,
  productIdentity: string,
): string {
  const normalizedName = normalizeProductName(productIdentity);

  // Get the clean base prompt for this category
  const basePrompt = CLEAN_VISUAL_PROMPTS[category];

  // Replace "the exact reference earring" with the actual product name where appropriate
  // but keep "the exact reference earring" as the primary instruction since the
  // image model receives the reference image
  const promptWithProduct = basePrompt.replace(
    /The exact reference earring/g,
    `The exact reference earring (${normalizedName})`,
  );

  // Compose: clean visual prompt + product fidelity + negative constraints
  return [
    promptWithProduct,
    "",
    PRODUCT_FIDELITY_BLOCK,
    "",
    COMMON_NEGATIVE,
  ].join("\n");
}

/**
 * Get the clean visual prompt for image generation, preferring the
 * Prompt 1 clean e-commerce output as the product reference.
 *
 * @param category - The promotional prompt category
 * @param productIdentity - The product identity string
 * @returns The clean visual prompt
 */
export function getPromotionalImagePrompt(
  category: PromptCategory,
  productIdentity: string,
): string {
  return getCleanVisualPrompt(category, productIdentity);
}
