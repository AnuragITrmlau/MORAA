// ============================================================
// image-analysis.service.ts — Image Analysis Pipeline
// MORAA GemVision
// ============================================================

import { analyzeImageWithGemini } from "./gemini.service";
import { parseJsonResponse } from "./gemini.service";
import { logger, generateRequestId } from "@/lib/logger";
import type {
  AnalysisResponse,
  AnalysisResult,
  AnalysisMetadata,
  ImageAnalysisRequest,
  JewelleryAnalysisResult,
  GeneralAnalysisResult,
  AnalysisCategory,
} from "@/types/analysis";
import { AppError, InvalidImageError } from "@/lib/errors";

// ─── Professional System Prompt ────────────────────────────

/*
 * Optimized system prompt for Google Gemini.
 * Removed: redundant role definitions, duplicate instructions,
 * unused output fields, verbose field descriptions.
 * Est. ~28% shorter than original.
 */

export const SYSTEM_PROMPT = [
  "You are MORAA GemVision, an image analysis AI. Analyze the image and return ONLY valid JSON. No markdown, no code fences, no extra text.",
  "",
  "DETECT the primary object category from the following list:",
  "- Jewellery, Diamond, Gold, Silver, Gemstone, Luxury Watch",
  "- Electronics, Vehicle, Document, Food, Medicine",
  "- Animal, Plant, Furniture, Fashion, Artwork",
  "- Unknown (if category cannot be determined)",
  "",
  "---",
  "",
  'For JEWELLERY, DIAMOND, GOLD, SILVER, GEMSTONE, or LUXURY WATCH, return this JSON:',
  "{",
  '  "category": "Jewellery" | "Diamond" | "Gold" | "Silver" | "Gemstone" | "Luxury Watch",',
  '  "jewelleryType": "Ring" | "Necklace" | "Pendant" | "Bracelet" | "Bangle" | "Chain" | "Coin" | "Earring" | "Brocade" | "Cufflinks" | "Watch" | "Loose Stone" | "Bar" | "Nugget" | "Other" | "Unknown",',
  '  "metalDetection": ["Gold" | "Silver" | "Platinum" | "Rose Gold" | "White Gold" | "Palladium" | "Titanium" | "Stainless Steel" | "Unknown"],',
  '  "gemstoneDetection": ["Diamond" | "Ruby" | "Emerald" | "Sapphire" | "Pearl" | "Moissanite" | "Opal" | "Topaz" | "Amethyst" | "Garnet" | "Citrine" | "Turquoise" | "Jade" | "Onyx" | "Unknown" | "None Detected"],',
  '  "craftsmanship": "Craftsmanship quality with specific observations",',
  '  "designStyle": "Design style (Victorian, Modern, Classic, Contemporary, etc.)",',
  '  "hallmarkVisibility": "Hallmarks, stamps, engravings, or None visible",',
  '  "surfaceFinish": "Surface finish (Polished, Matte, Brushed, Hammered, etc.)",',
  '  "stoneSetting": "Stone setting (Prong, Bezel, Pavé, Channel, etc. or None)",',
  '  "estimatedQuality": "Overall quality (Museum Quality, Premium, High, Good, Average, Fair, Poor)",',
  '  "luxuryLevel": "Luxury tier (High Luxury, Mid Luxury, Accessible Luxury, Mass Market, Economy)",',
  '  "visualObservations": "Key visual features: color, shape, proportions, distinctive elements",',
  '  "confidenceScore": 0.0 to 1.0',
  '  "sizeCategory": "small | medium | large (jewellery size relative to human anatomy)",',
  '  "relativeScale": "description of jewellery size compared to human anatomy (e.g. small stud ~5mm, delicate chain, chunky statement piece)",',
  '  "wearPosition": "natural wearing location (e.g. earlobe, finger, collarbone, wrist)",',
  '  "proportionNotes": "realistic fitting information for this jewellery on the human body",',
  '  "avoidGenerationErrors": ["oversized jewellery", "tiny jewellery", "unrealistic placement", "exaggerated gemstones", "redesigned details"]',
  "}",
  "",
  "---",
  "",
  'For all OTHER categories, return this JSON:',
  "{",
  '  "category": "detected category string",',
  '  "objectName": "Primary object name",',
  '  "detectedObjects": ["list", "of", "visible", "objects"],',
  '  "brand": "Brand or null if none visible",',
  '  "primaryMaterial": "Primary material (plastic, metal, glass, wood, etc.)",',
  '  "estimatedCondition": "Condition (Mint, Excellent, Good, Fair, Poor, Damaged)",',
  '  "dominantColors": "List of dominant colors",',
  '  "shape": "Overall shape description",',
  '  "usage": "Intended use or function",',
  '  "description": "Objective description of what is visible",',
  '  "observations": "Key analytical observations",',
  '  "confidenceScore": 0.0 to 1.0',
  "}",
  "",
  "Return ONLY valid JSON. No markdown. No code fences.",
].join("\n");

// ─── Validation ─────────────────────────────────────────────

const MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB
const ALLOWED_MIME_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/heic",
  "image/heif",
];

function validateImageRequest(request: ImageAnalysisRequest): void {
  if (!request.imageBase64 || request.imageBase64.length === 0) {
    throw new InvalidImageError("Image data is empty.");
  }

  if (!request.mimeType || !ALLOWED_MIME_TYPES.includes(request.mimeType)) {
    throw new InvalidImageError(
      `Unsupported image format: ${request.mimeType}. Supported formats: JPEG, PNG, WEBP, HEIC, HEIF.`
    );
  }

  // Initial size check (before resize)
  const estimatedBytes = Math.ceil((request.imageBase64.length * 3) / 4);
  if (estimatedBytes > MAX_IMAGE_SIZE_BYTES) {
    throw new InvalidImageError(
      `Image too large. Maximum size is ${MAX_IMAGE_SIZE_BYTES / 1024 / 1024} MB.`
    );
  }
}

// ─── Response Parser ───────────────────────────────────────

export function parseAnalysisResult(raw: Record<string, unknown>): AnalysisResult {
  const category = String(raw.category ?? "");

  if (category === "Jewellery" || category === "Diamond" || category === "Gold" || category === "Silver" || category === "Gemstone" || category === "Luxury Watch") {
    return {
      category: "Jewellery" as const,
      jewelleryType: (raw.jewelleryType as string) as JewelleryAnalysisResult["jewelleryType"] ?? "Unknown",
      metalDetection: (raw.metalDetection as string[]) as JewelleryAnalysisResult["metalDetection"] ?? [],
      gemstoneDetection: (raw.gemstoneDetection as string[]) as JewelleryAnalysisResult["gemstoneDetection"] ?? [],
      craftsmanship: String(raw.craftsmanship ?? ""),
      designStyle: String(raw.designStyle ?? ""),
      visibleDamage: "None visible",
      hallmarkVisibility: String(raw.hallmarkVisibility ?? ""),
      surfaceFinish: String(raw.surfaceFinish ?? ""),
      stoneSetting: String(raw.stoneSetting ?? ""),
      estimatedQuality: String(raw.estimatedQuality ?? ""),
      luxuryLevel: String(raw.luxuryLevel ?? ""),
      visualObservations: String(raw.visualObservations ?? ""),
      recommendations: "",
      confidenceScore: Number(raw.confidenceScore ?? 0),
      // Jewellery Scale & Reference Accuracy (JSR) — additive fields,
      // defaulted so analysis works even if the model omits them.
      sizeCategory: String(raw.sizeCategory ?? ""),
      relativeScale: String(raw.relativeScale ?? ""),
      wearPosition: String(raw.wearPosition ?? ""),
      proportionNotes: String(raw.proportionNotes ?? ""),
      avoidGenerationErrors: Array.isArray(raw.avoidGenerationErrors)
        ? (raw.avoidGenerationErrors as string[])
        : [],
    } as JewelleryAnalysisResult;
  }

  const otherCategory = category as Exclude<AnalysisCategory, "Jewellery">;
  return {
    category: otherCategory ?? ("Unknown" as AnalysisCategory),
    objectName: String(raw.objectName ?? "Unknown"),
    detectedObjects: (raw.detectedObjects as string[]) ?? [],
    primaryMaterial: String(raw.primaryMaterial ?? ""),
    estimatedCondition: String(raw.estimatedCondition ?? ""),
    color: String(raw.dominantColors ?? raw.color ?? ""),
    shape: String(raw.shape ?? ""),
    brand: (raw.brand as string | null) ?? null,
    textDetected: null,
    usage: String(raw.usage ?? ""),
    description: String(raw.description ?? ""),
    observations: String(raw.observations ?? ""),
    recommendations: "",
    confidenceScore: Number(raw.confidenceScore ?? 0),
  } as GeneralAnalysisResult;
}

// ─── Main Public Service ───────────────────────────────────

export async function analyzeImage(request: ImageAnalysisRequest): Promise<AnalysisResponse> {
  const pipelineRequestId = generateRequestId();
  const pipelineStart = Date.now();

  logger.info("Image analysis pipeline started", {
    requestId: pipelineRequestId,
    mimeType: request.mimeType,
    customPrompt: request.customPrompt ? "yes" : "no",
  });

  try {
    // Step 1: Validate
    validateImageRequest(request);

    // Step 2: Build the prompt
    const prompt = request.customPrompt
      ? `${SYSTEM_PROMPT}\n\nAdditional context: ${request.customPrompt}`
      : SYSTEM_PROMPT;

    // Step 3: Call Gemini (via analyzeImageWithGemini which uses @google/genai SDK)
    const geminiResult = await analyzeImageWithGemini(
      prompt,
      request.imageBase64,
      request.mimeType
    );

    // Step 4: Parse the structured response
    const rawJson = parseJsonResponse(geminiResult.text);
    const analysisResult = parseAnalysisResult(rawJson);

    // Step 6: Build metadata
    const executionTimeMs = Date.now() - pipelineStart;
    const metadata: AnalysisMetadata = {
      requestId: pipelineRequestId,
      executionTimeMs,
      model: geminiResult.model,
      promptTokens: geminiResult.promptTokens,
      completionTokens: geminiResult.completionTokens,
      timestamp: new Date().toISOString(),
    };

    logger.info("Image analysis pipeline completed", {
      requestId: pipelineRequestId,
      executionTimeMs,
      category: analysisResult.category,
      confidenceScore: analysisResult.confidenceScore,
    });

    return {
      success: true,
      data: analysisResult,
      metadata,
    };
  } catch (error: unknown) {
    const executionTimeMs = Date.now() - pipelineStart;
    const errMsg = error instanceof Error ? error.message : String(error);
    const errCode = error instanceof AppError
      ? error.code
      : "UNKNOWN";

    logger.error("Image analysis pipeline failed", {
      requestId: pipelineRequestId,
      executionTimeMs,
      error: errMsg,
      code: errCode,
    });

    return {
      success: false,
      data: null,
      metadata: {
        requestId: pipelineRequestId,
        executionTimeMs,
        model: "",
        promptTokens: 0,
        completionTokens: 0,
        timestamp: new Date().toISOString(),
      },
      error: {
        code: errCode,
        message: errMsg,
      },
    };
  }
}
