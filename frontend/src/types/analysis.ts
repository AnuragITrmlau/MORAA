// ============================================================
// analysis.ts — Analysis Result Type Definitions
// MORAA GemVision
// ============================================================

// ─── Auto-Detection Categories ─────────────────────────────

export const ANALYSIS_CATEGORIES = [
  "Jewellery",
  "Electronics",
  "Vehicle",
  "Document",
  "Food",
  "Medicine",
  "Animal",
  "Plant",
  "Furniture",
  "Fashion",
  "Artwork",
  "Luxury Item",
  "Unknown",
] as const;

export type AnalysisCategory = (typeof ANALYSIS_CATEGORIES)[number];

// ─── Jewellery-Specific Types ──────────────────────────────

export const JEWELLERY_TYPES = [
  "Ring",
  "Necklace",
  "Pendant",
  "Bracelet",
  "Bangle",
  "Chain",
  "Coin",
  "Earring",
  "Brocade",
  "Unknown",
] as const;

export type JewelleryType = (typeof JEWELLERY_TYPES)[number];

export const METAL_TYPES = [
  "Gold",
  "Silver",
  "Platinum",
  "Rose Gold",
  "White Gold",
  "Unknown",
] as const;

export type MetalType = (typeof METAL_TYPES)[number];

export const GEMSTONE_TYPES = [
  "Diamond",
  "Ruby",
  "Emerald",
  "Sapphire",
  "Pearl",
  "Moissanite",
  "Opal",
  "Topaz",
  "Unknown",
] as const;

export type GemstoneType = (typeof GEMSTONE_TYPES)[number];

export interface JewelleryAnalysisResult {
  category: "Jewellery";
  jewelleryType: JewelleryType;
  metalDetection: MetalType[];
  gemstoneDetection: GemstoneType[];
  craftsmanship: string;
  designStyle: string;
  visibleDamage: string;
  hallmarkVisibility: string;
  surfaceFinish: string;
  stoneSetting: string;
  estimatedQuality: string;
  luxuryLevel: string;
  visualObservations: string;
  recommendations: string;
  confidenceScore: number;
  // ── Jewellery Scale & Reference Accuracy (JSR) — additive ──
  // Help the image model understand real-world jewellery proportions.
  sizeCategory: string; // "small" | "medium" | "large"
  relativeScale: string; // size compared to human anatomy (e.g. small stud, delicate chain)
  wearPosition: string; // natural wearing location (earlobe, finger, neckline, wrist)
  proportionNotes: string; // realistic fitting information
  avoidGenerationErrors: string[]; // e.g. oversized/tiny/unrealistically placed
}

// ─── General Analysis Types ────────────────────────────────

export interface GeneralAnalysisResult {
  category: Exclude<AnalysisCategory, "Jewellery">;
  objectName: string;
  detectedObjects: string[];
  primaryMaterial: string;
  estimatedCondition: string;
  color: string;
  shape: string;
  brand: string | null;
  textDetected: string | null;
  usage: string;
  description: string;
  observations: string;
  recommendations: string;
  confidenceScore: number;
}

// ─── Unified Analysis Response ─────────────────────────────

export type AnalysisResult = JewelleryAnalysisResult | GeneralAnalysisResult;

export interface AnalysisMetadata {
  requestId: string;
  executionTimeMs: number;
  model: string;
  promptTokens: number;
  completionTokens: number;
  timestamp: string;
}

export interface AnalysisResponse {
  success: boolean;
  data: AnalysisResult | null;
  metadata: AnalysisMetadata;
  error?: {
    code: string;
    message: string;
  };
}

// ─── Request Types ─────────────────────────────────────────

export interface ImageAnalysisRequest {
  imageBase64: string;
  mimeType: string;
  customPrompt?: string;
}

// ─── Frontend-friendly display types ───────────────────────

export interface AnalysisDisplayData {
  analysis: AnalysisResult;
  metadata: AnalysisMetadata;
  thumbnailUrl: string;
}

export function isJewelleryAnalysis(
  result: AnalysisResult
): result is JewelleryAnalysisResult {
  return result.category === "Jewellery";
}

export function isGeneralAnalysis(
  result: AnalysisResult
): result is GeneralAnalysisResult {
  return result.category !== "Jewellery";
}
