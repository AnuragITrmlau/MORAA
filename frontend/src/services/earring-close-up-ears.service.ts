// Isolated Prompt 2 — Close Up Ears prompt service.

import { generateRequestId, logger } from "@/lib/logger";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface CloseUpEarsPromptResponse {
  success: boolean;
  prompt?: string;
  earring_type?: "Dangle";
  error?: string;
}

/**
 * Fetch the isolated Prompt 2 Close Up Ears prompt.
 *
 * Send the returned prompt to the existing image-generation service together
 * with Image #2 as the sole referenceImage and `image/webp` as its MIME type.
 */
export async function generateCloseUpEarsPrompt(): Promise<string> {
  const requestId = generateRequestId();
  const startTime = Date.now();

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/earring-close-up-ears/prompt`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ earring_type: "Dangle" }),
      },
    );

    if (!response.ok) {
      throw new Error(
        `Close Up Ears prompt endpoint returned ${response.status}.`,
      );
    }

    const result: CloseUpEarsPromptResponse = await response.json();
    if (!result.success || !result.prompt) {
      throw new Error(result.error || "Close Up Ears prompt generation failed.");
    }

    logger.info("Close Up Ears prompt generated", {
      requestId,
      promptLength: result.prompt.length,
      timeMs: Date.now() - startTime,
    });
    return result.prompt;
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error("Close Up Ears prompt generation failed", {
      requestId,
      error: errorMessage,
      timeMs: Date.now() - startTime,
    });
    throw error;
  }
}
