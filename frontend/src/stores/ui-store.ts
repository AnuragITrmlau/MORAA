import { create } from "zustand";
import type { UploadState, ComparisonInfo, MultiImageState, MultiImageItem } from "@/types";
import type {
  AnalysisResponse as GeminiAnalysisResponse,
} from "@/types/analysis";

interface UIState {
  // Upload state (single image)
  upload: UploadState;
  setUpload: (upload: Partial<UploadState>) => void;
  resetUpload: () => void;

  // Multi-image upload state
  multiUpload: MultiImageState;
  setMultiUpload: (partial: Partial<MultiImageState>) => void;
  addMultiImage: (item: MultiImageItem) => void;
  removeMultiImage: (id: string) => void;
  reorderMultiImages: (ids: string[]) => void;
  clearMultiUpload: () => void;

  // Upload mode: "single" | "multi"
  uploadMode: "single" | "multi";
  setUploadMode: (mode: "single" | "multi") => void;

  // Analysis state (legacy FastAPI)
  isAnalyzing: boolean;
  setIsAnalyzing: (val: boolean) => void;
  analysisResult: Record<string, string> | null;
  setAnalysisResult: (val: Record<string, string> | null) => void;

  // Gemini analysis state
  geminiAnalysis: GeminiAnalysisResponse | null;
  setGeminiAnalysis: (val: GeminiAnalysisResponse | null) => void;

  // Comparison info (legacy FastAPI)
  comparisonInfo: ComparisonInfo | null;
  setComparisonInfo: (val: ComparisonInfo | null) => void;

  // Navigation
  currentPage: string;
  setCurrentPage: (page: string) => void;

  // Sidebar
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (val: boolean) => void;

  // Reset all
  resetAll: () => void;
}

const initialUpload: UploadState = {
  status: "idle",
  progress: 0,
  file: null,
  previewUrl: null,
  errorMessage: null,
};

const initialMultiUpload: MultiImageState = {
  images: [],
  groupId: null,
  status: "idle",
  errorMessage: null,
};

export const useUIStore = create<UIState>((set) => ({
  upload: initialUpload,
  setUpload: (partial) => set((s) => ({ upload: { ...s.upload, ...partial } })),
  resetUpload: () =>
    set({
      upload: initialUpload,
      analysisResult: null,
      comparisonInfo: null,
      geminiAnalysis: null,
    }),

  // Multi-image
  multiUpload: initialMultiUpload,
  setMultiUpload: (partial) =>
    set((s) => ({ multiUpload: { ...s.multiUpload, ...partial } })),
  addMultiImage: (item) =>
    set((s) => ({
      multiUpload: {
        ...s.multiUpload,
        images: [...s.multiUpload.images, item],
        status: "uploading",
      },
    })),
  removeMultiImage: (id) =>
    set((s) => ({
      multiUpload: {
        ...s.multiUpload,
        images: s.multiUpload.images
          .filter((img) => img.id !== id)
          .map((img, i) => ({ ...img, order: i })),
        status: s.multiUpload.images.length <= 1 ? "idle" : s.multiUpload.status,
      },
    })),
  reorderMultiImages: (ids) =>
    set((s) => {
      const idSet = new Set(ids);
      const existing = s.multiUpload.images.filter((img) => idSet.has(img.id));
      const reordered = ids
        .map((id) => existing.find((img) => img.id === id))
        .filter((img): img is MultiImageItem => img !== undefined)
        .map((img, i) => ({ ...img, order: i }));
      return {
        multiUpload: { ...s.multiUpload, images: reordered },
      };
    }),
  clearMultiUpload: () =>
    set({
      multiUpload: initialMultiUpload,
      geminiAnalysis: null,
    }),

  // Upload mode
  uploadMode: "single",
  setUploadMode: (mode) =>
    set({
      uploadMode: mode,
      // Reset the other mode's state when switching
      ...(mode === "multi"
        ? { upload: initialUpload }
        : { multiUpload: initialMultiUpload }),
    }),

  isAnalyzing: false,
  setIsAnalyzing: (val) => set({ isAnalyzing: val }),

  analysisResult: null,
  setAnalysisResult: (val) => set({ analysisResult: val }),

  geminiAnalysis: null,
  setGeminiAnalysis: (val) => set({ geminiAnalysis: val }),

  comparisonInfo: null,
  setComparisonInfo: (val) => set({ comparisonInfo: val }),

  currentPage: "dashboard",
  setCurrentPage: (page) => {
    set({ currentPage: page });
  },

  sidebarCollapsed: false,
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setSidebarCollapsed: (val) => set({ sidebarCollapsed: val }),

  resetAll: () =>
    set({
      upload: initialUpload,
      multiUpload: initialMultiUpload,
      analysisResult: null,
      comparisonInfo: null,
      geminiAnalysis: null,
      isAnalyzing: false,
    }),
}));
