// ============================================================
// route.ts — Next.js API Route Proxy for Image Generation
// MORAA GemVision
// ============================================================
// Route path: /api/generate-image
//
// Proxies to the backend's /api/generate-image endpoint which
// routes through Gemini (primary) -> OpenAI (fallback) with
// automatic failover for recoverable errors.
// ============================================================

import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/lib/logger";

export const maxDuration = 120;
export const dynamic = "force-dynamic";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface GenerateImageBody {
  prompt: string;
  aspectRatio?: string;
  imageId?: string;
  /**
   * Optional base64-encoded reference image of the original product.
   * Forwarded to the backend so the image model can lock onto the exact
   * jewellery identity (shape, stones, metalwork, proportions).
   */
  referenceImage?: string;
  /**
   * MIME type of the reference image (default: image/jpeg).
   */
  referenceMimeType?: string;
  /**
   * Optional provider to force (e.g. 'openai' or 'gemini').
   * When set, uses ONLY this provider with no automatic fallback.
   */
  forceProvider?: string;
}

function validateBody(body: unknown): body is GenerateImageBody {
  if (!body || typeof body !== "object") return false;
  const data = body as Record<string, unknown>;
  if (typeof data.prompt !== "string" || data.prompt.length === 0) return false;
  return true;
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const body: unknown = await request.json();

    if (!validateBody(body)) {
      return NextResponse.json(
        {
          success: false,
          provider: "none",
          fallback_used: false,
          fallback_reason: null,
          image_url: null,
          generation_time: 0,
          error: "Invalid request. Expected { prompt: string }.",
        },
        { status: 400 },
      );
    }

    logger.info("Proxying image generation to backend", {
      promptLength: body.prompt.length,
      aspectRatio: body.aspectRatio || "4:5",
    });

    const response = await fetch(`${API_BASE_URL}/api/generate-image`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: body.prompt,
        aspect_ratio: body.aspectRatio || "4:5",
        image_id: body.imageId,
        reference_image: body.referenceImage || null,
        reference_mime_type: body.referenceMimeType || "image/jpeg",
        force_provider: body.forceProvider || null,
      }),
    });

    const result = await response.json();

    if (!result.success) {
      logger.error("Backend image generation failed", {
        error: result.error,
        provider: result.provider,
      });
    }

    return NextResponse.json(result, { status: response.ok ? 200 : 422 });
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : String(error);
    logger.error("Image generation proxy error", { error: errMsg });
    return NextResponse.json(
      {
        success: false,
        provider: "none",
        fallback_used: false,
        fallback_reason: null,
        image_url: null,
        generation_time: 0,
        error: "Image generation failed: " + errMsg,
      },
      { status: 500 },
    );
  }
}

export async function GET(): Promise<NextResponse> {
  return NextResponse.json({
    status: "ready",
    service: "image-generation-proxy",
    proxy_to: API_BASE_URL + "/api/generate-image",
    timestamp: new Date().toISOString(),
  });
}
