// ============================================================
// earring-ecommerce.service.ts — Earring E-Commerce Prompt Service
// MORAA GemVision
// ============================================================
// Calls the backend's /api/earring-ecommerce/prompt endpoint
// to get the single authoritative earring e-commerce main-image prompt.
//
// The returned prompt is then sent to /api/generate-image along
// with the reference image for actual image generation.
// ============================================================

import { logger, generateRequestId } from "@/lib/logger";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type EarringType = "Hoop" | "Stud" | "Dangle";

interface EarringEcommercePromptRequest {
  earringType?: EarringType;
}

interface EarringEcommercePromptResponse {
  success: boolean;
  prompt?: string;
  earring_type?: string;
  error?: string;
}

/**
 * Generate the single authoritative earring e-commerce main-image prompt.
 *
 * This calls the backend endpoint which returns a complete prompt string
 * including:
 * - Reference image priority marker
 * - Anti-redesign rules
 * - Anti-symmetry / anti-beautification rules
 * - Product identity preservation
 * - Earring type-specific preservation (Hoop/Stud/Dangle)
 * - Material & colour fidelity
 * - Input cleanup rules
 * - Angle preservation
 * - E-commerce presentation rules
 * - Output rule (no card/backing)
 *
 * The returned prompt should be sent to /api/generate-image with
 * the reference image.
 */
export async function generateEarringEcommercePrompt(
  request: EarringEcommercePromptRequest = {},
): Promise<string> {
  const requestId = generateRequestId();
  const startTime = Date.now();

  logger.info("Earring e-commerce prompt requested", {
    requestId,
    earringType: request.earringType || "generic",
  });

  try {
    const response = await fetch(`${API_BASE_URL}/api/earring-ecommerce/prompt`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        earring_type: request.earringType || null,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Earring e-commerce prompt endpoint returned ${response.status}: ${errorText}`,
      );
    }

    const result: EarringEcommercePromptResponse = await response.json();

    if (!result.success || !result.prompt) {
      throw new Error(
        result.error || "Earring e-commerce prompt generation failed",
      );
    }

    logger.info("Earring e-commerce prompt generated", {
      requestId,
      earringType: request.earringType || "generic",
      promptLength: result.prompt.length,
      timeMs: Date.now() - startTime,
    });

    return result.prompt;
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : String(error);
    logger.error("Earring e-commerce prompt generation failed", {
      requestId,
      error: errMsg,
      timeMs: Date.now() - startTime,
    });
    throw error;
  }
}
