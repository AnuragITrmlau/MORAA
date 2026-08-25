// Analysis Service - Connects to FastAPI backend
// Backend: http://localhost:8000

import type { AnalysisResult, ComparisonInfo, ProcessingEnhancement } from "@/types";
import { getLastUploadResponse } from "./upload.service";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AnalysisResponse {
  analysisResult: AnalysisResult;
  comparisonInfo: ComparisonInfo;
}

export async function analyzeProduct(imageId?: string): Promise<AnalysisResponse> {
  // Use provided imageId or fall back to the last uploaded image's ID
  const uploadResponse = getLastUploadResponse();
  const effectiveImageId =
    imageId && imageId !== "img-001"
      ? imageId
      : uploadResponse?.id;

  if (!effectiveImageId) {
    throw new Error("No image available for analysis. Please upload an image first.");
  }

  // Start analysis
  const analysisResponse = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: effectiveImageId }),
  });

  if (!analysisResponse.ok) {
    const error = await analysisResponse.json().catch(() => ({ detail: "Analysis failed to start" }));
    throw new Error(error.detail || "Analysis failed to start");
  }

  const processingData = await analysisResponse.json();
  const analysisId = processingData.analysisId;
  const requestId = processingData.requestId ?? "";

  // Poll for results
  const maxAttempts = 30;
  const pollInterval = 1000;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    await new Promise((resolve) => setTimeout(resolve, pollInterval));

    const resultResponse = await fetch(
      `${API_BASE_URL}/api/analyze/${analysisId}`
    );

    if (resultResponse.status === 202) {
      // Still processing, continue polling
      continue;
    }

    if (resultResponse.status === 422) {
      throw new Error("Analysis failed");
    }

    if (!resultResponse.ok) {
      const error = await resultResponse.json().catch(() => ({ detail: "Failed to get analysis" }));
      throw new Error(error.detail || "Failed to get analysis");
    }

    const result = await resultResponse.json();

    const analysisResult: AnalysisResult = {
      id: result.id,
      productId: result.productId,
      material: result.material,
      goldPurity: result.goldPurity,
      weight: result.weight,
      category: result.category,
      estimatedPrice: result.estimatedPrice,
      confidence: result.confidence,
      gemstones: result.gemstones || [],
      style: result.style,
      era: result.era,
      condition: result.condition,
      summary: result.summary,
      analyzedAt: result.analyzedAt,
    };

    // Build comparison info from the full API response
    const responseRequestId = result.requestId ?? result.request_id ?? requestId;
    const imageReference = result.imageReference ?? result.image_reference ?? uploadResponse?.url ?? "";
    // The processed image URL is the same as the original since the AI
    // performs analysis only (not pixel modification). Both images come
    // from the same request_id for faithful traceability.
    const originalImageUrl = uploadResponse?.url ? `${API_BASE_URL}${uploadResponse.url}` : "";
    const processedImageUrl = imageReference.startsWith("http") ? imageReference : `${API_BASE_URL}${imageReference}`;

    const defaultEnhancements: ProcessingEnhancement[] = [
      { name: "Material Analysis", status: "completed" },
      { name: "Gemstone Detection", status: "completed" },
      { name: "Style Classification", status: "completed" },
      { name: "Quality Assessment", status: "completed" },
    ];

    const comparisonInfo: ComparisonInfo = {
      requestId: responseRequestId,
      originalImageUrl,
      processedImageUrl,
      version: result.versionNumber ?? result.version_number ?? 1,
      processingTime: result.processingTime ?? result.processing_time ?? 0,
      enhancements: defaultEnhancements,
    };

    return { analysisResult, comparisonInfo };
  }

  throw new Error("Analysis timed out. Please try again.");
}

export async function getAnalysisHistory(): Promise<AnalysisResult[]> {
  const response = await fetch(`${API_BASE_URL}/api/analyses`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to fetch history" }));
    throw new Error(error.detail || "Failed to fetch history");
  }

  const analyses = await response.json();
  return analyses.map((result: any) => ({
    id: result.id,
    productId: result.productId,
    material: result.material,
    goldPurity: result.goldPurity,
    weight: result.weight,
    category: result.category,
    estimatedPrice: result.estimatedPrice,
    confidence: result.confidence,
    gemstones: result.gemstones || [],
    style: result.style,
    era: result.era,
    condition: result.condition,
    summary: result.summary,
    analyzedAt: result.analyzedAt,
  }));
}
