// ============================================================
// route.ts — Secure Next.js API Route for Prompt Generation
// MORAA GemVision
// ============================================================
// Route path: /api/prompts/generate
//
// Takes analysis data (from an already-completed Gemini analysis)
// and generates all 8 promotional prompts using LOCAL templates.
// ZERO Gemini API calls — uses the existing analysis result.
// ============================================================

import { NextRequest, NextResponse } from "next/server";
import { generatePromptsFromAnalysis } from "@/services/prompt-generation.service";
import { logger } from "@/lib/logger";
import type { AnalysisResult } from "@/types/analysis";

// ─── Configuration ─────────────────────────────────────────

export const maxDuration = 30; // Local generation is fast (no API calls)
export const dynamic = "force-dynamic";

// ─── Validation ─────────────────────────────────────────────

function validateBody(body: unknown): body is { analysisResult: AnalysisResult } {
  if (!body || typeof body !== "object") {
    return false;
  }

  const data = body as Record<string, unknown>;

  if (!data.analysisResult || typeof data.analysisResult !== "object") {
    return false;
  }

  const analysis = data.analysisResult as Record<string, unknown>;
  if (typeof analysis.category !== "string") {
    return false;
  }

  return true;
}

// ─── Handlers ───────────────────────────────────────────────

/**
 * POST /api/prompts/generate
 *
 * Accepts:  { analysisResult: AnalysisResult }
 * Returns:  { success, data: { workflowAnalysis, prompts, generationTimeMs }, error? }
 *
 * ZERO Gemini API calls. Uses local template engine.
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const body: unknown = await request.json();

    if (!validateBody(body)) {
      return NextResponse.json(
        {
          success: false,
          data: null,
          error: {
            code: "INVALID_REQUEST",
            message:
              "Invalid request body. Expected { analysisResult: AnalysisResult }.",
          },
        },
        { status: 400 }
      );
    }

    // Call the local prompt generation engine
    // ZERO Gemini API calls. ZERO tokens consumed.
    const result = generatePromptsFromAnalysis(body.analysisResult);

    logger.info("Local prompt generation via API route completed", {
      success: result.success,
      tokensConsumed: 0,
      source: "local-template-engine",
    });

    const statusCode = result.success ? 200 : 422;

    return NextResponse.json(result, { status: statusCode });
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : String(error);

    logger.error("Unhandled error in /api/prompts/generate", {
      error: errMsg,
    });

    return NextResponse.json(
      {
        success: false,
        data: null,
        error: {
          code: "INTERNAL_ERROR",
          message: "An unexpected error occurred during prompt generation.",
        },
      },
      { status: 500 }
    );
  }
}
