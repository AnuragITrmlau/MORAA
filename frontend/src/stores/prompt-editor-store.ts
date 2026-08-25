// ============================================================
// prompt-editor-store.ts — Editable Prompt Templates Store
// MORAA GemVision
// ============================================================
// Session-only persistence for user-edited prompt templates.
// Custom templates live in memory + sessionStorage (survives
// page navigation within the session, never touches disk).
// A `null`/absent entry means "use the built-in default".
// ============================================================

import { create } from "zustand";
import type { PromptCategory } from "@/types/prompts";

const STORAGE_KEY = "moraa.gemvision.prompt-templates.v1";

/** Map of category → custom template text. Missing keys fall back to defaults. */
export type PromptTemplatesMap = Partial<Record<PromptCategory, string>>;

interface PromptEditorState {
  /** Only categories the user has customized are present. */
  customTemplates: PromptTemplatesMap;
  isHydrated: boolean;
  hydrate: () => void;
  saveTemplates: (templates: PromptTemplatesMap) => void;
  clearTemplates: () => void;
}

function readStoredTemplates(): PromptTemplatesMap {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as PromptTemplatesMap;
    }
  } catch {
    // Corrupt storage — fall back to defaults
  }
  return {};
}

export const usePromptEditorStore = create<PromptEditorState>((set, get) => ({
  customTemplates: {},
  isHydrated: false,

  hydrate: () => {
    if (typeof window === "undefined" || get().isHydrated) return;
    set({ customTemplates: readStoredTemplates(), isHydrated: true });
  },

  saveTemplates: (templates) => {
    set({ customTemplates: templates, isHydrated: true });
    if (typeof window !== "undefined") {
      try {
        if (Object.keys(templates).length === 0) {
          window.sessionStorage.removeItem(STORAGE_KEY);
        } else {
          window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
        }
      } catch {
        // sessionStorage unavailable — in-memory only
      }
    }
  },

  clearTemplates: () => {
    set({ customTemplates: {}, isHydrated: true });
    if (typeof window !== "undefined") {
      try {
        window.sessionStorage.removeItem(STORAGE_KEY);
      } catch {
        // ignore
      }
    }
  },
}));

// Hydrate once at module load on the client so prompt generation
// always sees the latest custom templates without extra ceremony.
if (typeof window !== "undefined") {
  usePromptEditorStore.getState().hydrate();
}
