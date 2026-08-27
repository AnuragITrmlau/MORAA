// ============================================================
// earring-scale-reference.service.ts — Earring Scale Reference Prompt Service
// MORAA GemVision — Prompt 3
// ============================================================
// Calls the backend's /api/earring-scale-reference/prompt endpoint
// to get the single authoritative earring scale-reference prompt.
//
// The returned prompt is then sent to /api/generate-image along
// with the reference image for actual image generation.
// ============================================================

import { generateRequestId, logger } from "@/lib/logger";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type EarringType = "Hoop" | "Stud" | "Dangle";

interface ScaleReferencePromptRequest {
  earringType?: EarringType;
}

interface ScaleReferencePromptResponse {
  success: boolean;
  prompt?: string;
  earring_type?: string;
  error?: string;
}

/**
 * Generate the single authoritative earring scale-reference prompt (Prompt 3).
 *
 * This calls the backend endpoint which returns a complete prompt string
 * including:
 * - Reference image priority marker
 * - Anti-redesign rules
 * - Anti-symmetry / anti-beautification rules
 * - Product identity preservation
 * - Earring type-specific preservation (Hoop/Stud/Dangle)
 * - Material & colour fidelity
 * - Negative space and bead cluster preservation
 * - Scale control (ear adapts to product, not vice versa)
 * - Ear-as-scale-reference instructions
 * - Occlusion & anti-reconstruction rules
 * - Camera, lighting, and e-commerce presentation rules
 *
 * The returned prompt should be sent to /api/generate-image with
 * the reference image.
 */
export async function generateScaleReferencePrompt(
  request: ScaleReferencePromptRequest = {},
): Promise<string> {
  const requestId = generateRequestId();
  const startTime = Date.now();

  logger.info("Scale reference prompt requested", {
    requestId,
    earringType: request.earringType || "generic",
  });

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/earring-scale-reference/prompt`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          earring_type: request.earringType || null,
        }),
      },
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Scale reference prompt endpoint returned ${response.status}: ${errorText}`,
      );
    }

    const result: ScaleReferencePromptResponse = await response.json();

    if (!result.success || !result.prompt) {
      throw new Error(
        result.error || "Scale reference prompt generation failed",
      );
    }

    logger.info("Scale reference prompt generated", {
      requestId,
      earringType: request.earringType || "generic",
      promptLength: result.prompt.length,
      timeMs: Date.now() - startTime,
    });

    return result.prompt;
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : String(error);
    logger.error("Scale reference prompt generation failed", {
      requestId,
      error: errMsg,
      timeMs: Date.now() - startTime,
    });
    throw error;
  }
}
