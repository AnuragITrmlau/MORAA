// ============================================================
// prompt-generation.service.ts — Local Prompt Template Engine
// MORAA GemVision
// ============================================================
// ZERO Gemini API calls. Takes the ALREADY-EXISTING Gemini
// Analysis result and maps it to the 8 promotional prompt
// categories using deterministic template strings.
//
// Token consumption: ZERO (no API calls)
// ============================================================

import type {
  AnalysisResult,
  JewelleryAnalysisResult,
  GeneralAnalysisResult,
} from "@/types/analysis";
import type {
  PromptCategory,
  WorkflowAnalysisData,
  PromptGenerateResponse,
  PromptGenerationState,
} from "@/types/prompts";
import { PROMPT_CATEGORIES } from "@/types/prompts";
import { usePromptEditorStore } from "@/stores/prompt-editor-store";
import { logger, generateRequestId } from "@/lib/logger";

// ============================================================
// Mapper: AnalysisResult → WorkflowAnalysisData (11-field n8n format)
// ============================================================

function mapAnalysisToWorkflowData(analysis: AnalysisResult): WorkflowAnalysisData {
  if (analysis.category === "Jewellery") {
    return mapJewelleryAnalysis(analysis as JewelleryAnalysisResult);
  }
  return mapGeneralAnalysis(analysis as GeneralAnalysisResult);
}

function mapJewelleryAnalysis(j: JewelleryAnalysisResult): WorkflowAnalysisData {
  const metals = j.metalDetection.join(", ");
  const gemstones = (j.gemstoneDetection as string[]).filter(g => g !== "None Detected" && g !== "Unknown");
  const gemStr = gemstones.length > 0 ? gemstones.join(", ") : "precious stones";
  const metalPurityHint = j.hallmarkVisibility?.includes("18") ? "18K" :
    j.hallmarkVisibility?.includes("22") ? "22K" :
    j.hallmarkVisibility?.includes("24") || j.hallmarkVisibility?.includes("999") ? "24K" :
    j.hallmarkVisibility?.includes("925") ? "925 Sterling Silver" : metals;

  // Product Identity: e.g. "18K Gold Diamond Ring"
  const hasGemstones = j.gemstoneDetection.length > 0 && String(j.gemstoneDetection[0]) !== "None Detected";
  const productIdentity = `${metalPurityHint} ${metals} ${j.jewelleryType}${hasGemstones ? ` with ${gemStr}` : ""}`;

  // Material Properties
  const materialProperties = `${metals}. ${j.surfaceFinish ? `Finish: ${j.surfaceFinish}. ` : ""}${j.stoneSetting ? `Setting: ${j.stoneSetting}. ` : ""}${j.hallmarkVisibility ? `Hallmarks: ${j.hallmarkVisibility}.` : ""}`;

  // Scale and Proportion — enriched with Jewellery Scale & Reference
  // Accuracy (JSR) fields so the image model knows real-world sizing.
  const sizeHint = (j.estimatedQuality || "").toLowerCase().includes("premium") || (j.luxuryLevel || "").toLowerCase().includes("high") ? "substantial, weighty" : "elegantly proportioned";
  const scaleParts: string[] = [];
  if (j.sizeCategory) scaleParts.push(`Size category: ${j.sizeCategory}`);
  if (j.relativeScale) scaleParts.push(`Relative scale: ${j.relativeScale}`);
  if (j.wearPosition) scaleParts.push(`Natural wear position: ${j.wearPosition}`);
  if (j.proportionNotes) scaleParts.push(`Proportion notes: ${j.proportionNotes}`);
  const scaleAndProportion = `A ${sizeHint} ${j.jewelleryType.toLowerCase()} piece. ${scaleParts.length > 0 ? `${scaleParts.join(". ")}. ` : ""}Maintain the exact original size and proportions — do not enlarge, shrink, or exaggerate the jewellery. Designed for balanced ergonomics and comfortable daily wear.`;

  // Design Style
  const designStyle = j.designStyle || `${j.surfaceFinish || "Polished"} Contemporary design`;

  // Visual Craftsmanship
  const visualCraftsmanship = `${j.craftsmanship || "Premium"} craftsmanship. ${j.visualObservations || "Clean lines and precise execution."}`;

  // Target Demographic
  const demoMap: Record<string, string> = {
    "High Luxury": "Ultra-high-net-worth individuals, C-suite executives, discerning collectors seeking investment-grade pieces",
    "Mid Luxury": "Affluent professionals, senior executives, established entrepreneurs aged 35-60",
    "Accessible Luxury": "Career professionals, managers, urban millennials aged 28-45 with disposable income",
    "Mass Market": "Everyday consumers, gift buyers, young professionals aged 22-35",
    "Economy": "Budget-conscious consumers, first-time buyers, casual gift seekers",
  };
  const targetDemographic = demoMap[j.luxuryLevel] || demoMap["Accessible Luxury"];

  // Psychographics
  const psychoMap: Record<string, string> = {
    "High Luxury": "Value exclusivity, heritage, and craftsmanship. Purchasing decisions are driven by rarity, investment potential, and social status signaling.",
    "Mid Luxury": "Appreciate quality and design. Seek products that reflect their success and taste without being ostentatious. Value brand reputation and enduring style.",
    "Accessible Luxury": "Aspirational buyers who reward themselves with quality. Motivated by self-expression, gifting occasions, and social validation on digital platforms.",
    "Mass Market": "Practical, trend-aware consumers who prioritize value and versatility. Decisions influenced by recommendations and social proof.",
    "Economy": "Value-driven, occasion-motivated buyers. Seek meaningful gifts and personal treats within budget constraints.",
  };
  const psychographics = psychoMap[j.luxuryLevel] || psychoMap["Accessible Luxury"];

  // Functional Utility
  const utilityMap: Record<string, string> = {
    "Ring": "Finger adornment, personal expression, milestone marking (engagement, wedding, anniversary), or everyday elegance",
    "Necklace": "Neckline enhancement, pendant display, layering piece for both casual and formal occasions",
    "Pendant": "Focal point for necklaces, symbolic or personalized messaging, versatile day-to-night wear",
    "Bracelet": "Wrist accent, stackable fashion piece, subtle sophistication for professional and social settings",
    "Bangle": "Stackable wrist adornment, traditional and contemporary versatility, statement or minimalist wear",
    "Chain": "Neck or wrist foundational piece, pendant carrier, standalone minimalist accessory",
    "Earring": "Facial framing, style accentuation, from subtle studs to statement drops for all occasions",
    "Coin": "Collectible or investment-grade piece, cultural heirloom, wearable asset",
    "Brocade": "Textile embellishment, ceremonial wear, traditional craftsmanship showcase",
    "Cufflinks": "Formal attire accent, professional polish, sartorial detail for cuffed shirts",
    "Watch": "Timekeeping, status statement, mechanical appreciation, daily utility with heritage value",
  };
  const functionalUtility = utilityMap[j.jewelleryType] || `Personal adornment and lifestyle enhancement piece`;

  // Lifestyle Branding
  const brandingMap: Record<string, string> = {
    "High Luxury": "A pinnacle of personal achievement, worn as a signature of discernment and success. The piece elevates any ensemble from merely stylish to memorably distinctive.",
    "Mid Luxury": "Refined taste made tangible. This piece communicates quiet confidence and an appreciation for quality craftsmanship in every detail.",
    "Accessible Luxury": "Everyday elegance for the modern individual. A piece that transitions seamlessly from boardroom to dinner, adding polish to life's moments.",
    "Mass Market": "Versatile style for the contemporary lifestyle. Designed to complement daily routines while adding a touch of refinement.",
    "Economy": "Affordable elegance for life's meaningful moments. Proof that style and quality need not be mutually exclusive.",
  };
  const lifestyleBranding = brandingMap[j.luxuryLevel] || brandingMap["Accessible Luxury"];

  // Indian Festive Context
  const festiveHint = j.metalDetection.some(m => m.includes("Gold")) ?
    "Gold is particularly auspicious during Diwali, Akshaya Tritiya, and wedding seasons" :
    "Versatile for all festive occasions including Diwali gifting, wedding celebrations, and corporate festive gifting";
  const indianFestiveContext = `Highly suitable for the Indian festive and gifting market. ${festiveHint}. ${j.designStyle?.toLowerCase().includes("traditional") || j.designStyle?.toLowerCase().includes("vintage") ? "Traditional designs resonate strongly during festive seasons." : "Contemporary designs appeal to modern festive gifting preferences."}`;

  // Market Readiness
  const conf = j.confidenceScore || 0.85;
  const quality = j.estimatedQuality || "Premium";
  const marketReadiness = `Confidence score: ${(conf * 100).toFixed(0)}%. Quality assessment: ${quality}. Strong commercial viability in the Indian corporate gifting and premium retail markets.`;

  return {
    productIdentity,
    materialProperties,
    scaleAndProportion,
    designStyle,
    visualCraftsmanship,
    targetDemographic,
    psychographics,
    functionalUtility,
    lifestyleBranding,
    indianFestiveContext,
    marketReadiness,
  };
}

function mapGeneralAnalysis(g: GeneralAnalysisResult): WorkflowAnalysisData {
  const productIdentity = g.objectName || g.detectedObjects?.[0] || g.category || "Product";
  const materialProperties = `${g.primaryMaterial || "Premium material"}. ${g.color ? `Color: ${g.color}.` : ""} ${g.shape ? `Shape: ${g.shape}.` : ""}`;
  const scaleAndProportion = g.description ? `${g.description.slice(0, 120)}. Standard dimensions for this category.` : "Standard proportions suitable for its category.";
  const designStyle = g.shape || g.description?.split(".")[0] || "Contemporary design";
  const visualCraftsmanship = `${g.estimatedCondition || "Good"} condition. ${g.observations || "Well-executed construction with attention to detail."}`;
  const targetDemographic = `Users interested in ${g.usage || "premium lifestyle products"}. ${g.brand ? `Brand-conscious consumers looking for ${g.brand}.` : "Value-conscious buyers seeking quality and utility."}`;
  const psychographics = `Value-driven consumers who appreciate ${g.description?.toLowerCase().includes("premium") ? "luxury and craftsmanship" : "quality and functionality"}. Motivated by ${g.usage || "practical utility and aesthetic appeal"}.`;
  const functionalUtility = g.usage || `${g.category} for everyday use and enjoyment`;
  const lifestyleBranding = `${g.description?.split(".")[0] || `${productIdentity} - a premium ${g.category} piece`}. Designed for the modern lifestyle.`;
  const indianFestiveContext = `Suitable for gifting during Indian festive seasons including Diwali, New Year, and corporate milestones. ${g.brand ? `Brand recognition: ${g.brand}.` : ""} Versatile appeal for a wide demographic.`;
  const conf = g.confidenceScore || 0.8;
  const marketReadiness = `Confidence score: ${(conf * 100).toFixed(0)}%. Condition: ${g.estimatedCondition || "Good"}. Market-ready with strong appeal for the Indian gifting and retail market.`;

  return {
    productIdentity,
    materialProperties,
    scaleAndProportion,
    designStyle,
    visualCraftsmanship,
    targetDemographic,
    psychographics,
    functionalUtility,
    lifestyleBranding,
    indianFestiveContext,
    marketReadiness,
  };
}

// ============================================================
// Prompt Template Engine
// Each category is a deterministic template using mapped data.
// ============================================================

const esc = (v: string) => v.replace(/"/g, '\\"').replace(/\n/g, " ");

function generateProfessionalShot(wa: WorkflowAnalysisData): string {
  return `Professional product photography. ${esc(wa.productIdentity)} presented in a premium studio setting. Scene concept: ${esc(wa.designStyle)} aesthetic with ${esc(wa.materialProperties)}. Background: clean, minimal surface complementing the product's material qualities. Studio lighting with controlled shadows highlighting texture and craftsmanship. Composition: hero angle at 45 degrees, product centered with balanced negative space for text overlay. Color palette: complementary tones derived from ${esc(wa.lifestyleBranding)}. Camera: 50mm f/2.8 macro lens, shallow depth of field for product isolation. High resolution, sharp focus on product details. No text, no watermarks, no human models. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.`;
}

function generateUseCaseShot(wa: WorkflowAnalysisData): string {
  return `Lifestyle product-in-use photography. A person naturally using ${esc(wa.productIdentity)} in an authentic everyday setting. The subject, aligned with ${esc(wa.targetDemographic)}, is shown engaging with the product in a genuine moment of use. Scene: a realistic environment matching the product's functional context — ${esc(wa.functionalUtility)}. The product is the clear focal point: sharp focus, well-lit, positioned prominently. Natural lighting (soft window light or golden hour). Framing shows only necessary body parts (hands, wrist, neck) to keep focus on the product. 1-3 minimal props for context. Camera: 50mm f/2.2, natural depth of field. Warm, authentic color grading. No product obscured, no motion blur, no stock-photo stiffness. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.`;
}

function generateIngredientStory(wa: WorkflowAnalysisData): string {
  return `Craft and provenance storytelling photography. ${esc(wa.productIdentity)} shown alongside its raw material origin story. Foreground: the finished product in sharpest focus, hero lighting. Background (softly blurred): the raw materials and craft process that created it — ${esc(wa.materialProperties)}. The visual narrative says "this became that" through a deliberate compositional link (shared lighting, color echo, or diagonal line). Process elements occupy no more than 40% of visual weight. Setting: authentic workspace (workbench, artisan table, craft studio). Tools of the trade visible but secondary. Warm, earthy, handmade color palette — workshop ambers, natural material tones. Single warm directional light (workshop window or work-lamp). Camera: 85mm f/2.0 macro-capable, shallow depth of field. No human hands unless essential and then blurred/secondary. No text or watermarks. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.`;
}

function generateFestive(wa: WorkflowAnalysisData): string {
  return `Indian festive campaign photography. ${esc(wa.productIdentity)} within the vibrant atmosphere of an Indian festival, aligned with ${esc(wa.indianFestiveContext)}. A model matching ${esc(wa.targetDemographic)} is shown in a candid festive moment — mid-laugh, mid-gesture, or mid-celebration — wearing or holding the product naturally. The product is well-lit and clearly visible but not dominant; the festive energy leads, the product supports. Environment: secular festive setting (decorated courtyard, twinkling-light terrace, rangoli-lined doorway). Non-religious festive props: diyas (decorative only), string lights, marigold garlands, color powder. Vibrant festival-appropriate palette. Lighting matched to the festival's natural mood. Candid, slightly off-center composition. Camera: 50mm f/2.0 for natural depth. STRICT CONSTRAINT: NO religious idols, deities, murtis, altars, or temple interiors anywhere in frame. No text, no watermarks. No more than 2 people in frame. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.`;
}

function generateTransformation(wa: WorkflowAnalysisData): string {
  return `Before/after emotional transformation photography. A clean split-frame composition (50/50 vertical divide, soft gradient transition) showing the SAME model in two emotional states, separated only by the presence of ${esc(wa.productIdentity)}. BEFORE half (left): cooler, flatter lighting; model's expression neutral or subdued — shoulders slightly dropped, eyes half-lidded, muted posture. Product not present. AFTER half (right): warmer, richer lighting; model's expression bright and confident — shoulders open, eyes engaged, genuine smile. Product visibly in use/worn/held. Model's appearance, outfit, hairstyle, and framing remain IDENTICAL across both halves — only expression, posture, and energy change. Environment is the same in both halves. BEFORE palette: muted, slightly cool. AFTER palette: vibrant, warm, product-complementary. Camera: 50mm f/2.5, consistent framing. No text, no labels, no arrows, no dividing lines. No theatrical expressions — the contrast should feel subtle and real. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.`;
}

function generateScaleReference(wa: WorkflowAnalysisData): string {
  return `Scale accuracy product photography. ${esc(wa.productIdentity)} shown alongside a single familiar reference object for true size comparison — eliminating buyer uncertainty. The reference is chosen to match ${esc(wa.scaleAndProportion)}: for small items, held between clean, unadorned fingers; for handheld items, resting naturally in an open palm; for tabletop items, placed next to a standard coffee mug or smartphone. GEOMETRICALLY ACCURATE proportions — no artistic size exaggeration or minimization. Product and reference on the same focal plane at the same distance from camera. Background: clean, minimal, softly neutral (light grey or soft white). Even, shadow-minimal e-commerce lighting. Eye-level or slight 3/4 top-down angle. Camera: 50mm at f/8 for full sharpness across both elements. Neutral, true-to-life color accuracy. No text, no measurement labels, no rulers, no grid overlays. Only one reference object. Aspect ratio 4:5 or 1:1. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.`;
}

function generateComplementaryShot(wa: WorkflowAnalysisData): string {
  return `Lifestyle still-life pairing photography. ${esc(wa.productIdentity)} positioned alongside its most natural real-world companion item, reflecting ${esc(wa.lifestyleBranding)}. The product is the clear primary subject (roughly 60/40 visual weight), occupying the stronger compositional third in sharper focus and brighter light. The companion item sits behind or beside the product, slightly softer in focus, natural and incidental — not perfectly arranged. Surface: a real, textural setting appropriate to the moment (sunlit wooden table, marble counter, linen desk). Soft, natural-feeling directional light (window light) that clearly favors the product. Three-quarter or slight top-down angle reading as an authentic lifestyle moment. No human model by default. Color palette: complementary, not competing with the product. Camera: 50mm f/2.8, shallow-to-moderate depth of field. No second unit or variant of the product as companion. Only one companion item. No text or watermarks. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.`;
}

function generateUgcStyle(wa: WorkflowAnalysisData): string {
  return `User-generated content style photography. ${esc(wa.productIdentity)} photographed casually on a smartphone by an everyday customer who just received it. NOT a professional photo — this should feel authentically unstaged. Setting: a real everyday location appropriate to ${esc(wa.targetDemographic)} (kitchen counter, study desk, café table, bedroom windowsill). ONLY natural daylight — NO studio lighting, no softboxes, no artificial fill. Smartphone camera simulation: slightly compressed dynamic range, mild oversharpening, natural color rendering. Imperfect composition: off-center framing, product slightly tilted, shot from natural standing/sitting eye-level. 1-3 authentic environmental elements (coffee mug, phone charger, keys, book) — real-life clutter, not styled props. Product remains the clear subject — foreground, well-lit, in focus. Background has natural texture and minor imperfections. Natural, slightly inconsistent color temperature. Phone-camera depth of field (mostly sharp, slight edge softness). Aspect ratio 1:1 (social post-native). No studio lighting, no professional color grading, no text, no filters. The image must NOT look like a professional advertisement. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.`;
}

// ============================================================
// Editable Prompt Templates (Prompt Editor)
// ============================================================
// The strings below power the Prompt Editor UI: they mirror the
// built-in generators using `{{field}}` placeholders (instead of
// JS interpolation) and are rendered with renderPromptTemplate.
//
// PIPELINE ORDER (deliberate, do not change):
//   1. Analysis comes from the existing Gemini analysis API (untouched).
//   2. Prompts are FIRST generated from that analysis result using the
//      built-in generators above (the existing prompt-generation flow).
//   3. Only THEN are the Prompt Editor's saved templates applied as a
//      downstream overlay — re-wording individual categories that the
//      user explicitly edited, still using the SAME analysis-derived
//      workflow data. Unedited categories keep built-in output
//      byte-for-byte. The Image Analysis → Prompt Generation pipeline
//      is never replaced or bypassed.
// ============================================================

/** All workflow fields available as `{{placeholder}}` in custom templates. */
export const PROMPT_TEMPLATE_FIELDS: (keyof WorkflowAnalysisData)[] = [
  "productIdentity",
  "materialProperties",
  "scaleAndProportion",
  "designStyle",
  "visualCraftsmanship",
  "targetDemographic",
  "psychographics",
  "functionalUtility",
  "lifestyleBranding",
  "indianFestiveContext",
  "marketReadiness",
];

/** Default template text shown in the Prompt Editor ({{field}} syntax). */
export const DEFAULT_PROMPT_TEMPLATES: Record<PromptCategory, string> = {
  professionalShot:
    "Professional product photography. {{productIdentity}} presented in a premium studio setting. Scene concept: {{designStyle}} aesthetic with {{materialProperties}}. Background: clean, minimal surface complementing the product's material qualities. Studio lighting with controlled shadows highlighting texture and craftsmanship. Composition: hero angle at 45 degrees, product centered with balanced negative space for text overlay. Color palette: complementary tones derived from {{lifestyleBranding}}. Camera: 50mm f/2.8 macro lens, shallow depth of field for product isolation. High resolution, sharp focus on product details. No text, no watermarks, no human models. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.",
  useCaseShot:
    "Lifestyle product-in-use photography. A person naturally using {{productIdentity}} in an authentic everyday setting. The subject, aligned with {{targetDemographic}}, is shown engaging with the product in a genuine moment of use. Scene: a realistic environment matching the product's functional context — {{functionalUtility}}. The product is the clear focal point: sharp focus, well-lit, positioned prominently. Natural lighting (soft window light or golden hour). Framing shows only necessary body parts (hands, wrist, neck) to keep focus on the product. 1-3 minimal props for context. Camera: 50mm f/2.2, natural depth of field. Warm, authentic color grading. No product obscured, no motion blur, no stock-photo stiffness. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.",
  ingredientStory:
    `Craft and provenance storytelling photography. {{productIdentity}} shown alongside its raw material origin story. Foreground: the finished product in sharpest focus, hero lighting. Background (softly blurred): the raw materials and craft process that created it — {{materialProperties}}. The visual narrative says "this became that" through a deliberate compositional link (shared lighting, color echo, or diagonal line). Process elements occupy no more than 40% of visual weight. Setting: authentic workspace (workbench, artisan table, craft studio). Tools of the trade visible but secondary. Warm, earthy, handmade color palette — workshop ambers, natural material tones. Single warm directional light (workshop window or work-lamp). Camera: 85mm f/2.0 macro-capable, shallow depth of field. No human hands unless essential and then blurred/secondary. No text or watermarks. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.`,
  festive:
    "Indian festive campaign photography. {{productIdentity}} within the vibrant atmosphere of an Indian festival, aligned with {{indianFestiveContext}}. A model matching {{targetDemographic}} is shown in a candid festive moment — mid-laugh, mid-gesture, or mid-celebration — wearing or holding the product naturally. The product is well-lit and clearly visible but not dominant; the festive energy leads, the product supports. Environment: secular festive setting (decorated courtyard, twinkling-light terrace, rangoli-lined doorway). Non-religious festive props: diyas (decorative only), string lights, marigold garlands, color powder. Vibrant festival-appropriate palette. Lighting matched to the festival's natural mood. Candid, slightly off-center composition. Camera: 50mm f/2.0 for natural depth. STRICT CONSTRAINT: NO religious idols, deities, murtis, altars, or temple interiors anywhere in frame. No text, no watermarks. No more than 2 people in frame. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.",
  transformation:
    "Before/after emotional transformation photography. A clean split-frame composition (50/50 vertical divide, soft gradient transition) showing the SAME model in two emotional states, separated only by the presence of {{productIdentity}}. BEFORE half (left): cooler, flatter lighting; model's expression neutral or subdued — shoulders slightly dropped, eyes half-lidded, muted posture. Product not present. AFTER half (right): warmer, richer lighting; model's expression bright and confident — shoulders open, eyes engaged, genuine smile. Product visibly in use/worn/held. Model's appearance, outfit, hairstyle, and framing remain IDENTICAL across both halves — only expression, posture, and energy change. Environment is the same in both halves. BEFORE palette: muted, slightly cool. AFTER palette: vibrant, warm, product-complementary. Camera: 50mm f/2.5, consistent framing. No text, no labels, no arrows, no dividing lines. No theatrical expressions — the contrast should feel subtle and real. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.",
  scaleReference:
    "Scale accuracy product photography. {{productIdentity}} shown alongside a single familiar reference object for true size comparison — eliminating buyer uncertainty. The reference is chosen to match {{scaleAndProportion}}: for small items, held between clean, unadorned fingers; for handheld items, resting naturally in an open palm; for tabletop items, placed next to a standard coffee mug or smartphone. GEOMETRICALLY ACCURATE proportions — no artistic size exaggeration or minimization. Product and reference on the same focal plane at the same distance from camera. Background: clean, minimal, softly neutral (light grey or soft white). Even, shadow-minimal e-commerce lighting. Eye-level or slight 3/4 top-down angle. Camera: 50mm at f/8 for full sharpness across both elements. Neutral, true-to-life color accuracy. No text, no measurement labels, no rulers, no grid overlays. Only one reference object. Aspect ratio 4:5 or 1:1. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.",
  complementaryShot:
    "Lifestyle still-life pairing photography. {{productIdentity}} positioned alongside its most natural real-world companion item, reflecting {{lifestyleBranding}}. The product is the clear primary subject (roughly 60/40 visual weight), occupying the stronger compositional third in sharper focus and brighter light. The companion item sits behind or beside the product, slightly softer in focus, natural and incidental — not perfectly arranged. Surface: a real, textural setting appropriate to the moment (sunlit wooden table, marble counter, linen desk). Soft, natural-feeling directional light (window light) that clearly favors the product. Three-quarter or slight top-down angle reading as an authentic lifestyle moment. No human model by default. Color palette: complementary, not competing with the product. Camera: 50mm f/2.8, shallow-to-moderate depth of field. No second unit or variant of the product as companion. Only one companion item. No text or watermarks. Aspect ratio 4:5. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.",
  ugcStyle:
    "User-generated content style photography. {{productIdentity}} photographed casually on a smartphone by an everyday customer who just received it. NOT a professional photo — this should feel authentically unstaged. Setting: a real everyday location appropriate to {{targetDemographic}} (kitchen counter, study desk, café table, bedroom windowsill). ONLY natural daylight — NO studio lighting, no softboxes, no artificial fill. Smartphone camera simulation: slightly compressed dynamic range, mild oversharpening, natural color rendering. Imperfect composition: off-center framing, product slightly tilted, shot from natural standing/sitting eye-level. 1-3 authentic environmental elements (coffee mug, phone charger, keys, book) — real-life clutter, not styled props. Product remains the clear subject — foreground, well-lit, in focus. Background has natural texture and minor imperfections. Natural, slightly inconsistent color temperature. Phone-camera depth of field (mostly sharp, slight edge softness). Aspect ratio 1:1 (social post-native). No studio lighting, no professional color grading, no text, no filters. The image must NOT look like a professional advertisement. DO NOT CHANGE THE LOOK OF THE PRODUCT, you may change the angle but not the look and feel of the product.",
};

/**
 * Render a user-edited template, substituting every `{{field}}`
 * placeholder with the escaped workflow value (same escaping the
 * built-in generators use).
 */
export function renderPromptTemplate(
  template: string,
  wa: WorkflowAnalysisData
): string {
  return template.replace(/\{\{\s*([a-zA-Z]+)\s*\}\}/g, (match, field: string) => {
    const key = field as keyof WorkflowAnalysisData;
    const value = wa[key];
    return value !== undefined && value !== null ? esc(String(value)) : match;
  });
}

/** Custom template for a category, or null when the built-in default applies. */
function getCustomTemplate(category: PromptCategory): string | null {
  if (typeof window === "undefined") return null;
  return usePromptEditorStore.getState().customTemplates[category] ?? null;
}

// ============================================================
// Main Public Service
// ============================================================

/**
 * Generate all 8 promotional prompts from an ALREADY-EXISTING
 * Gemini Analysis result.
 *
 * ZERO Gemini API calls. Uses deterministic template strings.
 * Token consumption: 0 (local computation only).
 */
export function generatePromptsFromAnalysis(
  analysis: AnalysisResult,
): PromptGenerateResponse {
  const requestId = generateRequestId();
  const startTime = Date.now();

  try {
    // Step 1: Map existing analysis data to n8n workflow format
    const workflowData = mapAnalysisToWorkflowData(analysis);

    // Step 2: Generate all 8 prompts using the existing local template
    // engine, then apply Prompt Editor customizations downstream (the
    // analysis → prompt-generation pipeline is unchanged).
    const prompts = generatePromptsFromWorkflowData(workflowData);

    const generationTimeMs = Date.now() - startTime;

    logger.info("Local prompt generation completed", {
      requestId,
      generationTimeMs,
      promptCount: Object.keys(prompts).length,
      tokensConsumed: 0,
      source: "local-template-engine",
    });

    return {
      success: true,
      data: {
        workflowAnalysis: workflowData,
        prompts,
        generationTimeMs,
      },
    };
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : String(error);
    const generationTimeMs = Date.now() - startTime;

    logger.error("Local prompt generation failed", {
      requestId,
      generationTimeMs,
      error: errMsg,
    });

    return {
      success: false,
      data: null,
      error: {
        code: "LOCAL_PROMPT_GENERATION_FAILED",
        message: errMsg,
      },
    };
  }
}

/**
 * Generate all 8 promotional prompts from WorkflowAnalysisData
 * (useful when the mapping was already done).
 *
 * PIPELINE ORDER: the 8 prompts are generated FIRST with the built-in
 * generators (existing flow). The Prompt Editor's saved templates are then
 * applied as a POST-GENERATION overlay, re-wording only the categories the
 * user explicitly edited using the same analysis-derived workflow data.
 */
export function generatePromptsFromWorkflowData(
  workflowData: WorkflowAnalysisData,
): Record<PromptCategory, string> {
  // Step 1 — EXISTING GENERATION (unchanged): all 8 prompts from the
  // analysis-derived workflow data via the built-in generators.
  const prompts: Record<PromptCategory, string> = {
    professionalShot: generateProfessionalShot(workflowData),
    useCaseShot: generateUseCaseShot(workflowData),
    ingredientStory: generateIngredientStory(workflowData),
    festive: generateFestive(workflowData),
    transformation: generateTransformation(workflowData),
    scaleReference: generateScaleReference(workflowData),
    complementaryShot: generateComplementaryShot(workflowData),
    ugcStyle: generateUgcStyle(workflowData),
  };

  // Step 2 — PROMPT EDITOR OVERLAY (downstream of generation): apply the
  // user's saved templates only to the categories they edited. Unedited
  // categories keep the built-in output byte-for-byte. This never replaces
  // the Image Analysis → Prompt Generation pipeline.
  for (const category of PROMPT_CATEGORIES) {
    const custom = getCustomTemplate(category);
    if (custom !== null && custom.trim().length > 0) {
      prompts[category] = renderPromptTemplate(custom, workflowData);
    }
  }

  return prompts;
}

export { mapAnalysisToWorkflowData };
