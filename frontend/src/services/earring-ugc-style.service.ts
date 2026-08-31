// ============================================================
// earring-ugc-style.service.ts — Earring UGC Style Prompt Service
// MORAA GemVision — Prompt 6
// ============================================================
// Calls the backend's /api/earring-ugc-style/prompt endpoint
// to get the single authoritative UGC style prompt.
//
// The returned prompt is then sent to /api/generate-image along
// with the reference image for actual image generation.
// ============================================================

import { generateRequestId, logger } from "@/lib/logger";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type EarringType = "Hoop" | "Stud" | "Dangle";

interface UGCStylePromptRequest {
  earringType?: EarringType;
}

interface UGCStylePromptResponse {
  success: boolean;
  prompt?: string;
  earring_type?: string;
  error?: string;
}

/**
 * Generate the single authoritative earring UGC style prompt (Prompt 6).
 *
 * This calls the backend endpoint which returns a complete prompt string
 * including:
 * - Reference image priority marker
 * - Product fidelity — absolute priority
 * - Anti-redesign rules
 * - Anti-symmetry / anti-beautification rules
 * - Product identity preservation
 * - Earring type-specific preservation (Hoop/Stud/Dangle)
 * - Material & colour fidelity
 * - UGC environment (vanity, unboxing, wooden desk, linen)
 * - Natural window daylight lighting
 * - Smartphone photography aesthetic
 * - Strictly forbidden elements
 *
 * The returned prompt should be sent to /api/generate-image with
 * the reference image.
 */
export async function generateUGCStylePrompt(
  request: UGCStylePromptRequest = {},
): Promise<string> {
  const requestId = generateRequestId();
  const startTime = Date.now();

  logger.info("UGC style prompt requested", {
    requestId,
    earringType: request.earringType || "generic",
  });

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/earring-ugc-style/prompt`,
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
        `UGC style prompt endpoint returned ${response.status}: ${errorText}`,
      );
    }

    const result: UGCStylePromptResponse = await response.json();

    if (!result.success || !result.prompt) {
      throw new Error(
        result.error || "UGC style prompt generation failed",
      );
    }

    logger.info("UGC style prompt generated", {
      requestId,
      earringType: request.earringType || "generic",
      promptLength: result.prompt.length,
      timeMs: Date.now() - startTime,
    });

    return result.prompt;
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : String(error);
    logger.error("UGC style prompt generation failed", {
      requestId,
      error: errMsg,
      timeMs: Date.now() - startTime,
    });
    throw error;
  }
}
