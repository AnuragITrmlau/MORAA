// ============================================================
// earring-macro-shot.service.ts — Earring Macro Shot Prompt Service
// MORAA GemVision — Prompt 7
// ============================================================
// Calls the backend's /api/earring-macro-shot/prompt endpoint
// to get the single authoritative macro shot prompt.
//
// The returned prompt is then sent to /api/generate-image along
// with the reference image for actual image generation.
// ============================================================

import { generateRequestId, logger } from "@/lib/logger";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type EarringType = "Hoop" | "Stud" | "Dangle";

interface MacroShotPromptRequest {
  earringType?: EarringType;
}

interface MacroShotPromptResponse {
  success: boolean;
  prompt?: string;
  earring_type?: string;
  error?: string;
}

/**
 * Generate the single authoritative earring macro shot prompt (Prompt 7).
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
 * - Macro photography requirement
 * - Detail visibility rules
 * - Framing, focus, and lighting rules
 * - Anti-beautification / anti-reconstruction rules
 * - Reference priority hierarchy
 *
 * The returned prompt should be sent to /api/generate-image with
 * the reference image.
 */
export async function generateMacroShotPrompt(
  request: MacroShotPromptRequest = {},
): Promise<string> {
  const requestId = generateRequestId();
  const startTime = Date.now();

  logger.info("Macro shot prompt requested", {
    requestId,
    earringType: request.earringType || "generic",
  });

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/earring-macro-shot/prompt`,
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
        `Macro shot prompt endpoint returned ${response.status}: ${errorText}`,
      );
    }

    const result: MacroShotPromptResponse = await response.json();

    if (!result.success || !result.prompt) {
      throw new Error(
        result.error || "Macro shot prompt generation failed",
      );
    }

    logger.info("Macro shot prompt generated", {
      requestId,
      earringType: request.earringType || "generic",
      promptLength: result.prompt.length,
      timeMs: Date.now() - startTime,
    });

    return result.prompt;
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : String(error);
    logger.error("Macro shot prompt generation failed", {
      requestId,
      error: errMsg,
      timeMs: Date.now() - startTime,
    });
    throw error;
  }
}
