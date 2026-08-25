// ============================================================
// prompts.ts — Prompt Generation Type Definitions
// MORAA GemVision
// ============================================================
// Faithfully replicates the n8n "Raw to Promotable" workflow's
// Gemini Vision Analysis output schema and all 8 prompt categories.
// ============================================================

// ─── Workflow Analysis Schema ─────────────────────────────
// This is the exact 11-field JSON schema the n8n workflow's
// Gemini Vision Analysis node extracts from the image.

export interface WorkflowAnalysisData {
  productIdentity: string;
  materialProperties: string;
  scaleAndProportion: string;
  designStyle: string;
  visualCraftsmanship: string;
  targetDemographic: string;
  psychographics: string;
  functionalUtility: string;
  lifestyleBranding: string;
  indianFestiveContext: string;
  marketReadiness: string;
}

// ─── Prompt Categories ────────────────────────────────────
// Exactly matching the 8 prompt generation nodes in the workflow.

export const PROMPT_CATEGORIES = [
  "professionalShot",
  "useCaseShot",
  "ingredientStory",
  "festive",
  "transformation",
  "scaleReference",
  "complementaryShot",
  "ugcStyle",
] as const;

export type PromptCategory = (typeof PROMPT_CATEGORIES)[number];

export const PROMPT_CATEGORY_LABELS: Record<PromptCategory, string> = {
  professionalShot: "Professional Shot",
  useCaseShot: "Use Case Shot",
  ingredientStory: "Craft Story",
  festive: "Festive",
  transformation: "Transformation",
  scaleReference: "Scale Reference",
  complementaryShot: "Complementary Shot",
  ugcStyle: "UGC Style",
};

export const PROMPT_CATEGORY_DESCRIPTIONS: Record<PromptCategory, string> = {
  professionalShot:
    "Premium studio photoshoot — controlled lighting, refined props, editorial composition",
  useCaseShot:
    "Product in authentic use — a real person interacting naturally with the product",
  ingredientStory:
    "Making-of / provenance — finished product + its raw material or craft process",
  festive:
    "Indian festival campaign — product within a festive cultural moment",
  transformation:
    "Before/after emotional shift — split-frame showing product's transformative effect",
  scaleReference:
    "Scale accuracy — product next to a familiar reference object for true size",
  complementaryShot:
    "Lifestyle pairing — product alongside its most natural companion item",
  ugcStyle:
    "User-generated content — casual smartphone shot, authentic everyday setting",
};

// ─── API Types ─────────────────────────────────────────────

export interface PromptGenerateRequest {
  imageBase64: string;
  mimeType: string;
  description?: string;
}

export interface PromptGenerateResponse {
  success: boolean;
  data: {
    workflowAnalysis: WorkflowAnalysisData;
    prompts: Record<PromptCategory, string>;
    generationTimeMs: number;
  } | null;
  error?: {
    code: string;
    message: string;
  };
}

export interface PromptGenerationState {
  status: "idle" | "analyzing" | "generating" | "completed" | "error";
  errorMessage: string | null;
  workflowAnalysis: WorkflowAnalysisData | null;
  prompts: Record<PromptCategory, string> | null;
  generationTimeMs: number;
}
