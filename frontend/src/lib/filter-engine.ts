// ============================================================
// filter-engine.ts — Client-Side Photo Filter Engine
// MORAA GemVision — Post-Generation Filters
// ============================================================
// Pixel-level image processing using Canvas API.
// No external dependencies. No AI API calls.
// All processing is deterministic and instant.
// ============================================================

// --- Filter Definitions ---

export type FilterId =
  | "original"
  | "luxury-glow"
  | "studio-light"
  | "warm-gold"
  | "cool-luxe"
  | "cinematic"
  | "brilliance"
  | "soft-elegance"
  | "vibrant-gem"
  | "black-luxury";

export interface FilterDef {
  id: FilterId;
  label: string;
  emoji: string;
  /** CSS filter string for fast thumbnail previews */
  cssFilter: string;
}

/**
 * Filter definitions with CSS filter strings for thumbnail previews.
 * The main image uses pixel-level processing for higher quality.
 */
export const FILTERS: FilterDef[] = [
  {
    id: "original",
    label: "Original",
    emoji: "✨",
    cssFilter: "none",
  },
  {
    id: "luxury-glow",
    label: "Luxury Glow",
    emoji: "✨",
    cssFilter: "brightness(1.08) contrast(1.04) saturate(1.06)",
  },
  {
    id: "studio-light",
    label: "Studio Light",
    emoji: "💡",
    cssFilter: "brightness(1.10) contrast(1.06) saturate(0.98)",
  },
  {
    id: "warm-gold",
    label: "Warm Gold",
    emoji: "🟡",
    cssFilter: "brightness(1.04) contrast(1.02) saturate(1.10) sepia(0.08)",
  },
  {
    id: "cool-luxe",
    label: "Cool Luxe",
    emoji: "❄️",
    cssFilter: "brightness(1.06) contrast(1.06) saturate(0.94) hue-rotate(-8deg)",
  },
  {
    id: "cinematic",
    label: "Cinematic",
    emoji: "🎬",
    cssFilter: "brightness(0.96) contrast(1.18) saturate(1.08)",
  },
  {
    id: "brilliance",
    label: "Brilliance",
    emoji: "💎",
    cssFilter: "brightness(1.06) contrast(1.10) saturate(1.12)",
  },
  {
    id: "soft-elegance",
    label: "Soft Elegance",
    emoji: "🌙",
    cssFilter: "brightness(1.05) contrast(0.94) saturate(0.96)",
  },
  {
    id: "vibrant-gem",
    label: "Vibrant Gem",
    emoji: "🌈",
    cssFilter: "brightness(1.04) contrast(1.04) saturate(1.30)",
  },
  {
    id: "black-luxury",
    label: "Black Luxury",
    emoji: "🖤",
    cssFilter: "brightness(0.92) contrast(1.22) saturate(1.06)",
  },
];

// --- Pixel-Level Filter Processing ---

/**
 * Clamp a value between 0 and 255.
 */
function clamp(val: number): number {
  return val < 0 ? 0 : val > 255 ? 255 : val;
}

/**
 * Apply pixel-level adjustments to RGBA image data.
 * Operates directly on the Uint8ClampedArray from canvas.getImageData().
 */
function processPixels(
  data: Uint8ClampedArray,
  filterId: FilterId,
): void {
  const len = data.length;

  switch (filterId) {
    case "original":
      // No processing
      return;

    case "luxury-glow":
      // Subtle premium glow: brighten, slight contrast, warm tint, highlight boost
      for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        // Brightness
        r *= 1.07;
        g *= 1.06;
        b *= 1.04;

        // Subtle warm tint in highlights
        const lum = (r + g + b) / 3;
        if (lum > 160) {
          const t = (lum - 160) / 95;
          r += 6 * t;
          g += 2 * t;
          b -= 3 * t;
        }

        // Slight contrast
        const mid = 128;
        r = (r - mid) * 1.04 + mid;
        g = (g - mid) * 1.03 + mid;
        b = (b - mid) * 1.02 + mid;

        // Highlight glow: boost very bright pixels slightly
        if (r > 220) r = clamp(r + 5);
        if (g > 220) g = clamp(g + 4);
        if (b > 220) b = clamp(b + 3);

        data[i] = clamp(r);
        data[i + 1] = clamp(g);
        data[i + 2] = clamp(b);
      }
      break;

    case "studio-light":
      // Clean professional product photography: balanced brightness, clean highlights, neutral
      for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        // Balanced brightness
        r *= 1.10;
        g *= 1.10;
        b *= 1.10;

        // Clean contrast
        const mid = 128;
        r = (r - mid) * 1.06 + mid;
        g = (g - mid) * 1.06 + mid;
        b = (b - mid) * 1.06 + mid;

        // Slightly desaturate shadows for clean look
        const lum = 0.299 * r + 0.587 * g + 0.114 * b;
        if (lum < 80) {
          const t = (80 - lum) / 80;
          r = r + (lum - r) * t * 0.15;
          g = g + (lum - g) * t * 0.15;
          b = b + (lum - b) * t * 0.15;
        }

        // Brighten shadows gently
        if (lum < 60) {
          const boost = (60 - lum) / 60 * 8;
          r += boost;
          g += boost;
          b += boost;
        }

        data[i] = clamp(r);
        data[i + 1] = clamp(g);
        data[i + 2] = clamp(b);
      }
      break;

    case "warm-gold":
      // Warm luxurious golden tone
      for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        const lum = 0.299 * r + 0.587 * g + 0.114 * b;

        // Warm shift: boost red/yellow, slightly reduce blue
        r += 8;
        g += 3;
        b -= 6;

        // More warmth in highlights
        if (lum > 140) {
          const t = (lum - 140) / 115;
          r += 5 * t;
          g += 2 * t;
          b -= 4 * t;
        }

        // Slight saturation boost
        const avg = (r + g + b) / 3;
        r = avg + (r - avg) * 1.08;
        g = avg + (g - avg) * 1.08;
        b = avg + (b - avg) * 1.08;

        // Gentle brightness
        r *= 1.04;
        g *= 1.04;
        b *= 1.03;

        data[i] = clamp(r);
        data[i + 1] = clamp(g);
        data[i + 2] = clamp(b);
      }
      break;

    case "cool-luxe":
      // Sophisticated cool-toned luxury
      for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        const lum = 0.299 * r + 0.587 * g + 0.114 * b;

        // Cool shift: boost blue, slightly reduce warmth
        r -= 4;
        g += 1;
        b += 8;

        // More cool in shadows
        if (lum < 120) {
          const t = (120 - lum) / 120;
          r -= 3 * t;
          b += 5 * t;
        }

        // Clean whites: desaturate highlights slightly
        if (lum > 180) {
          const t = (lum - 180) / 75;
          const avg = (r + g + b) / 3;
          r = r + (avg - r) * t * 0.12;
          g = g + (avg - g) * t * 0.12;
          b = b + (avg - b) * t * 0.12;
        }

        // Contrast
        const mid = 128;
        r = (r - mid) * 1.06 + mid;
        g = (g - mid) * 1.05 + mid;
        b = (b - mid) * 1.07 + mid;

        // Brightness
        r *= 1.05;
        g *= 1.05;
        b *= 1.06;

        data[i] = clamp(r);
        data[i + 1] = clamp(g);
        data[i + 2] = clamp(b);
      }
      break;

    case "cinematic":
      // Premium cinematic: deeper shadows, controlled contrast, highlight preservation
      for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        const lum = 0.299 * r + 0.587 * g + 0.114 * b;

        // Deep shadows: darken darks more
        if (lum < 80) {
          const t = (80 - lum) / 80;
          r *= 1 - t * 0.15;
          g *= 1 - t * 0.12;
          b *= 1 - t * 0.10;
        }

        // Strong contrast
        const mid = 128;
        r = (r - mid) * 1.18 + mid;
        g = (g - mid) * 1.16 + mid;
        b = (b - mid) * 1.14 + mid;

        // Slight cinematic warm/cool split: warm highlights, cool shadows
        if (lum > 140) {
          r += 4;
          g += 1;
          b -= 3;
        } else {
          r -= 2;
          g += 1;
          b += 4;
        }

        // Subtle saturation
        const avg = (r + g + b) / 3;
        r = avg + (r - avg) * 1.08;
        g = avg + (g - avg) * 1.08;
        b = avg + (b - avg) * 1.08;

        // Slight overall darkening for cinematic feel
        r *= 0.97;
        g *= 0.97;
        b *= 0.97;

        data[i] = clamp(r);
        data[i + 1] = clamp(g);
        data[i + 2] = clamp(b);
      }
      break;

    case "brilliance":
      // Jewellery clarity and brilliance: sharpness via contrast, highlight boost
      for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        const lum = 0.299 * r + 0.587 * g + 0.114 * b;

        // Contrast for clarity
        const mid = 128;
        r = (r - mid) * 1.10 + mid;
        g = (g - mid) * 1.10 + mid;
        b = (b - mid) * 1.10 + mid;

        // Highlight enhancement: boost bright areas
        if (lum > 170) {
          const t = (lum - 170) / 85;
          r = clamp(r + 6 * t);
          g = clamp(g + 6 * t);
          b = clamp(b + 6 * t);
        }

        // Slight saturation for gemstone vibrancy
        const avg = (r + g + b) / 3;
        r = avg + (r - avg) * 1.12;
        g = avg + (g - avg) * 1.12;
        b = avg + (b - avg) * 1.12;

        // Brightness
        r *= 1.05;
        g *= 1.05;
        b *= 1.05;

        data[i] = clamp(r);
        data[i + 1] = clamp(g);
        data[i + 2] = clamp(b);
      }
      break;

    case "soft-elegance":
      // Soft, elegant: reduced contrast, softer highlights, gentle lighting
      for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        const lum = 0.299 * r + 0.587 * g + 0.114 * b;

        // Reduce contrast: pull toward midtones
        const mid = 128;
        r = (r - mid) * 0.92 + mid;
        g = (g - mid) * 0.92 + mid;
        b = (b - mid) * 0.92 + mid;

        // Soften highlights: compress very bright values
        if (r > 200) r = 200 + (r - 200) * 0.7;
        if (g > 200) g = 200 + (g - 200) * 0.7;
        if (b > 200) b = 200 + (b - 200) * 0.7;

        // Lift shadows slightly for soft feel
        if (lum < 60) {
          const boost = (60 - lum) / 60 * 10;
          r += boost;
          g += boost;
          b += boost;
        }

        // Slight warm tone
        r += 2;
        g += 1;
        b -= 1;

        // Brightness
        r *= 1.05;
        g *= 1.05;
        b *= 1.04;

        // Slight desaturation for elegance
        const avg = (r + g + b) / 3;
        r = avg + (r - avg) * 0.96;
        g = avg + (g - avg) * 0.96;
        b = avg + (b - avg) * 0.96;

        data[i] = clamp(r);
        data[i + 1] = clamp(g);
        data[i + 2] = clamp(b);
      }
      break;

    case "vibrant-gem":
      // Enhance existing gemstone colours: saturation, vibrancy
      for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        const lum = 0.299 * r + 0.587 * g + 0.114 * b;
        const avg = (r + g + b) / 3;

        // Increase saturation significantly
        const satBoost = 1.30;
        r = avg + (r - avg) * satBoost;
        g = avg + (g - avg) * satBoost;
        b = avg + (b - avg) * satBoost;

        // Enhance the dominant channel for more vibrancy
        const maxC = Math.max(r, g, b);
        if (maxC > 100) {
          const vibrance = 0.08;
          if (r === maxC) r += (r - avg) * vibrance;
          else if (g === maxC) g += (g - avg) * vibrance;
          else b += (b - avg) * vibrance;
        }

        // Slight contrast
        r = (r - 128) * 1.04 + 128;
        g = (g - 128) * 1.04 + 128;
        b = (b - 128) * 1.04 + 128;

        // Brightness
        r *= 1.04;
        g *= 1.04;
        b *= 1.04;

        data[i] = clamp(r);
        data[i + 1] = clamp(g);
        data[i + 2] = clamp(b);
      }
      break;

    case "black-luxury":
      // Dramatic premium: deep blacks, strong contrast, highlight preservation
      for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        const lum = 0.299 * r + 0.587 * g + 0.114 * b;

        // Deep blacks: crush shadows without losing detail
        if (lum < 50) {
          const t = (50 - lum) / 50;
          r *= 1 - t * 0.25;
          g *= 1 - t * 0.25;
          b *= 1 - t * 0.25;
        }

        // Strong contrast
        const mid = 128;
        r = (r - mid) * 1.22 + mid;
        g = (g - mid) * 1.22 + mid;
        b = (b - mid) * 1.22 + mid;

        // Preserve highlights: don't let brights clip
        if (r > 230) r = 230 + (r - 230) * 0.6;
        if (g > 230) g = 230 + (g - 230) * 0.6;
        if (b > 230) b = 230 + (b - 230) * 0.6;

        // Slight saturation boost
        const avg = (r + g + b) / 3;
        r = avg + (r - avg) * 1.06;
        g = avg + (g - avg) * 1.06;
        b = avg + (b - avg) * 1.06;

        // Slight overall darkening for luxury feel
        r *= 0.94;
        g *= 0.94;
        b *= 0.94;

        data[i] = clamp(r);
        data[i + 1] = clamp(g);
        data[i + 2] = clamp(b);
      }
      break;
  }
}

// --- Main Filter Application ---

/**
 * Apply a filter to an image URL and return a new data URL.
 * Uses Canvas API for pixel-level processing.
 *
 * @param imageUrl - Source image URL (http, data URI, or blob URL)
 * @param filterId - The filter to apply
 * @param quality - JPEG quality (0-1), defaults to 0.92
 * @returns Promise resolving to a data URL of the filtered image
 */
export async function applyFilter(
  imageUrl: string,
  filterId: FilterId,
  quality: number = 0.92,
): Promise<string> {
  if (filterId === "original") {
    return imageUrl;
  }

  const img = await loadImage(imageUrl);

  const canvas = document.createElement("canvas");
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;

  const ctx = canvas.getContext("2d");
  if (!ctx) {
    throw new Error("Failed to get canvas 2D context");
  }

  ctx.drawImage(img, 0, 0);

  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  processPixels(imageData.data, filterId);
  ctx.putImageData(imageData, 0, 0);

  return canvas.toDataURL("image/jpeg", quality);
}

/**
 * Apply a filter and return a Blob (for download).
 */
export async function applyFilterAsBlob(
  imageUrl: string,
  filterId: FilterId,
  quality: number = 0.92,
): Promise<Blob> {
  if (filterId === "original") {
    // Fetch original and return as blob
    const response = await fetch(imageUrl);
    return response.blob();
  }

  const img = await loadImage(imageUrl);

  const canvas = document.createElement("canvas");
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;

  const ctx = canvas.getContext("2d");
  if (!ctx) {
    throw new Error("Failed to get canvas 2D context");
  }

  ctx.drawImage(img, 0, 0);

  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  processPixels(imageData.data, filterId);
  ctx.putImageData(imageData, 0, 0);

  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (blob) resolve(blob);
        else reject(new Error("Failed to create image blob"));
      },
      "image/jpeg",
      quality,
    );
  });
}

/**
 * Generate a small thumbnail with a CSS filter applied.
 * Used for filter card previews.
 */
export function getFilterThumbnailStyle(filterId: FilterId): string {
  const filter = FILTERS.find((f) => f.id === filterId);
  return filter?.cssFilter ?? "none";
}

// --- Utility ---

/**
 * Load an image from a URL into an HTMLImageElement.
 */
function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
    img.src = url;
  });
}

/**
 * Get a filter definition by ID.
 */
export function getFilterById(id: FilterId): FilterDef | undefined {
  return FILTERS.find((f) => f.id === id);
}
