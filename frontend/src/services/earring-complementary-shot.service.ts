// ============================================================
// earring-complementary-shot.service.ts — Earring Complementary Shot Prompt Service
// MORAA GemVision — Prompt 5
// ============================================================
// Calls the backend's /api/earring-complementary-shot/prompt endpoint
// to get the single authoritative complementary shot prompt.
//
// The returned prompt is then sent to /api/generate-image along
// with the reference image for actual image generation.
// ============================================================

import { generateRequestId, logger } from "@/lib/logger";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type EarringType = "Hoop" | "Stud" | "Dangle";

interface ComplementaryShotPromptRequest {
  earringType?: EarringType;
}

interface ComplementaryShotPromptResponse {
  success: boolean;
  prompt?: string;
  earring_type?: string;
  error?: string;
}

/**
 * Generate the single authoritative earring complementary shot prompt (Prompt 5).
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
 * - Staging requirements (editorial surface)
 * - Asymmetric jewellery arrangement
 * - Physical contact & grounding
 * - Camera, lighting, background
 * - Visual hierarchy (90/10 jewellery focus)
 * - Negative space & bead cluster preservation
 * - Strictly forbidden elements
 * - Quality control checklist
 *
 * The returned prompt should be sent to /api/generate-image with
 * the reference image.
 */
export async function generateComplementaryShotPrompt(
  request: ComplementaryShotPromptRequest = {},
): Promise<string> {
  const requestId = generateRequestId();
  const startTime = Date.now();

  logger.info("Complementary shot prompt requested", {
    requestId,
    earringType: request.earringType || "generic",
  });

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/earring-complementary-shot/prompt`,
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
        `Complementary shot prompt endpoint returned ${response.status}: ${errorText}`,
      );
    }

    const result: ComplementaryShotPromptResponse = await response.json();

    if (!result.success || !result.prompt) {
      throw new Error(
        result.error || "Complementary shot prompt generation failed",
      );
    }

    logger.info("Complementary shot prompt generated", {
      requestId,
      earringType: request.earringType || "generic",
      promptLength: result.prompt.length,
      timeMs: Date.now() - startTime,
    });

    return result.prompt;
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : String(error);
    logger.error("Complementary shot prompt generation failed", {
      requestId,
      error: errMsg,
      timeMs: Date.now() - startTime,
    });
    throw error;
  }
}
