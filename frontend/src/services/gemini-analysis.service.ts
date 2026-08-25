// ============================================================
// gemini-analysis.service.ts — Frontend Gemini Analysis Service
// MORAA GemVision
// ============================================================
// This service runs in the browser. It is the bridge between
// React components and the server-side /api/gemini/analyze route.
// Internally uses Google Gemini API via the secure Next.js API route.
// ============================================================

import type {
  AnalysisResponse,
  AnalysisResult,
  AnalysisMetadata,
} from "@/types/analysis";

// ─── Constants ─────────────────────────────────────────────

const MAX_IMAGE_DIMENSION = 2048;
const COMPRESSION_QUALITY = 0.75;
const ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"];

// ─── Image Compression (Client-Side) ───────────────────────

/**
 * Compress and resize an image file client-side before uploading.
 * Reduces latency, token usage, and bandwidth for the Gemini API.
 */
function compressImage(file: File): Promise<{ base64: string; mimeType: string }> {
  return new Promise((resolve, reject) => {
    if (!ALLOWED_MIME_TYPES.includes(file.type)) {
      reject(new Error(`Unsupported format: ${file.type}. Please upload JPEG, PNG, or WEBP.`));
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        let { width, height } = img;

        if (width > MAX_IMAGE_DIMENSION || height > MAX_IMAGE_DIMENSION) {
          if (width > height) {
            height = Math.round((height / width) * MAX_IMAGE_DIMENSION);
            width = MAX_IMAGE_DIMENSION;
          } else {
            width = Math.round((width / height) * MAX_IMAGE_DIMENSION);
            height = MAX_IMAGE_DIMENSION;
          }
        }

        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext("2d");
        if (!ctx) {
          const base64 = (reader.result as string).replace(/^data:image\/\w+;base64,/, "");
          resolve({ base64, mimeType: file.type });
          return;
        }

        ctx.fillStyle = "#FFFFFF";
        ctx.fillRect(0, 0, width, height);
        ctx.drawImage(img, 0, 0, width, height);

        const exportType = "image/jpeg";
        const dataUrl = canvas.toDataURL(exportType, COMPRESSION_QUALITY);
        const base64 = dataUrl.replace(/^data:image\/\w+;base64,/, "");

        resolve({ base64, mimeType: exportType });
      };
      img.onerror = () => { reject(new Error("Failed to load image for compression.")); };
      img.src = reader.result as string;
    };
    reader.onerror = () => { reject(new Error("Failed to read file.")); };
    reader.readAsDataURL(file);
  });
}

// ─── API Call ──────────────────────────────────────────────

/**
 * Analyze an image file using the Gemini API via the secure Next.js API route.
 *
 * Flow: File -> Compress -> Base64 -> POST /api/gemini/analyze -> AnalysisResponse
 */
export async function analyzeImageWithGeminiAPI(
  file: File,
  customPrompt?: string
): Promise<AnalysisResponse> {
  const { base64, mimeType } = await compressImage(file);

  const response = await fetch("/api/gemini/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      imageBase64: base64,
      mimeType,
      customPrompt,
    }),
  });

  const result: AnalysisResponse = await response.json();

  if (!response.ok && !result.success) {
    throw new Error(
      result.error?.message || `Analysis failed with status ${response.status}`
    );
  }

  if (!result.success) {
    throw new Error(
      result.error?.message || "Analysis returned an unsuccessful result."
    );
  }

  return result;
}

// ─── Helpers ───────────────────────────────────────────────

export function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    Jewellery: "\uD83D\uDC8D Jewellery",
    Electronics: "\uD83D\uDCF1 Electronics",
    Vehicle: "\uD83D\uDE97 Vehicle",
    Document: "\uD83D\uDCC4 Document",
    Food: "\uD83C\uDF7D\uFE0F Food",
    Medicine: "\uD83D\uDC8A Medicine",
    Animal: "\uD83D\uDC3E Animal",
    Plant: "\uD83C\uDF3F Plant",
    Furniture: "\uD83E\uDE91 Furniture",
    Fashion: "\uD83D\uDC57 Fashion",
    Artwork: "\uD83C\uDFA8 Artwork",
    "Luxury Item": "\uD83D\uDC8E Luxury Item",
    Unknown: "\u2753 Unknown",
  };
  return labels[category] || "\uD83D\uDD0D " + category;
}

export function formatConfidence(score: number): string {
  return `${(score * 100).toFixed(0)}%`;
}

export function getConfidenceColor(score: number): string {
  if (score >= 0.8) return "#22C55E";
  if (score >= 0.5) return "#F59E0B";
  return "#EF4444";
}
