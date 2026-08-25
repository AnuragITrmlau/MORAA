// ============================================================
// backend-prompt.service.ts - Backend Prompt Generation Service
// MORAA GemVision
// ============================================================
// Uploads the image to the FastAPI backend, then calls the
// backend /api/prompts/generate endpoint using the returned
// image_id. Completely replaces the direct Gemini route call.
// ============================================================

import { logger, generateRequestId } from "@/lib/logger";
import type {
  PromptGenerateResponse,
  PromptCategory,
  WorkflowAnalysisData,
} from "@/types/prompts";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface BackendUploadResponse {
  id: string;
  requestId: string;
  filename: string;
  url: string;
  size: number;
  mimeType: string;
  uploadedAt: string;
}

/**
 * Upload an image file to the backend and return the image_id.
 */
async function uploadImageToBackend(file: File): Promise<BackendUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail || "Upload failed");
  }

  const raw = await response.json();
  return {
    id: raw.id ?? raw.image_id,
    requestId: raw.requestId ?? raw.request_id ?? "",
    filename: raw.filename ?? raw.original_filename ?? "",
    url: raw.url ?? raw.image_url ?? "",
    size: raw.size ?? raw.file_size ?? 0,
    mimeType: raw.mimeType ?? raw.mime_type ?? "",
    uploadedAt: raw.uploadedAt ?? raw.uploaded_at ?? new Date().toISOString(),
  };
}

/**
 * Generate promotional prompts by uploading to the backend and
 * calling the backend /api/prompts/generate endpoint.
 *
 * Flow: Upload file to backend, get image_id, then call backend prompt generation.
 */
export async function generatePromptsViaBackend(
  file: File,
  description?: string
): Promise<PromptGenerateResponse> {
  const requestId = generateRequestId();
  const startTime = Date.now();

  logger.info("Backend prompt generation started", { requestId, filename: file.name });

  try {
    // Step 1: Upload image to backend
    logger.info("Step 1: Uploading image to backend", { requestId });
    const uploadResult = await uploadImageToBackend(file);
    logger.info("Step 1 complete: Image uploaded", {
      requestId,
      imageId: uploadResult.id,
    });

    // Step 2: Call backend prompt generation
    logger.info("Step 2: Calling backend /api/prompts/generate", {
      requestId,
      imageId: uploadResult.id,
    });

    const response = await fetch(`${API_BASE_URL}/api/prompts/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_id: uploadResult.id,
        description: description ?? "",
      }),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unknown error");
      throw new Error("Backend prompt generation failed: " + errorText);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || "Backend prompt generation failed");
    }

    const generationTimeMs = Date.now() - startTime;

    logger.info("Backend prompt generation completed", {
      requestId,
      generationTimeMs,
      imageId: uploadResult.id,
    });

    // Map backend response to frontend PromptGenerateResponse format
    const wa = result.workflowAnalysis ?? result.workflow_analysis ?? {};
    const workflowAnalysis: WorkflowAnalysisData = {
      productIdentity: String(wa.productIdentity ?? wa.ProductIdentity ?? ""),
      materialProperties: String(wa.materialProperties ?? wa.MaterialProperties ?? ""),
      scaleAndProportion: String(wa.scaleAndProportion ?? wa["Scale and Proportion"] ?? ""),
      designStyle: String(wa.designStyle ?? wa.DesignStyle ?? ""),
      visualCraftsmanship: String(wa.visualCraftsmanship ?? wa.VisualCraftsmanship ?? ""),
      targetDemographic: String(wa.targetDemographic ?? wa.TargetDemographic ?? ""),
      psychographics: String(wa.psychographics ?? wa.Psychographics ?? ""),
      functionalUtility: String(wa.functionalUtility ?? wa.FunctionalUtility ?? ""),
      lifestyleBranding: String(wa.lifestyleBranding ?? wa.LifestyleBranding ?? ""),
      indianFestiveContext: String(wa.indianFestiveContext ?? wa.IndianFestiveContext ?? ""),
      marketReadiness: String(wa.marketReadiness ?? wa.MarketReadiness ?? ""),
    };

    const prompts = result.prompts as Record<PromptCategory, string>;

    return {
      success: true,
      data: {
        workflowAnalysis,
        prompts,
        generationTimeMs,
      },
    };
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : String(error);
    const generationTimeMs = Date.now() - startTime;

    logger.error("Backend prompt generation failed", {
      requestId,
      generationTimeMs,
      error: errMsg,
    });

    return {
      success: false,
      data: null,
      error: {
        code: "BACKEND_PROMPT_FAILED",
        message: errMsg,
      },
    };
  }
}
