"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useUIStore } from "@/stores/ui-store";
import { analyzeImageWithGeminiAPI } from "@/services/gemini-analysis.service";
import UnifiedUploadCard from "@/components/UnifiedUploadCard";
import PreviewCard from "@/components/PreviewCard";
import PromptGenerationPanel from "@/components/PromptGenerationPanel";
import {
  Sparkles,
  ArrowUp,
  Loader2,
  Gem,
  History,
  ChevronRight,
  AlertTriangle,
  X,
  ImageIcon,
} from "lucide-react";

export default function NewAnalysisPage() {
  const { upload, isAnalyzing, setIsAnalyzing, geminiAnalysis, setGeminiAnalysis, uploadMode, multiUpload } = useUIStore();
  const [mounted, setMounted] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);
  const [imageData, setImageData] = useState<{ base64: string; mimeType: string } | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Convert file to base64 for prompt generation panel
  useEffect(() => {
    const file = upload.file;
    if (!file) {
      setImageData(null);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      const base64 = result.replace(/^data:image\/\w+;base64,/, "");
      setImageData({ base64, mimeType: file.type });
    };
    reader.readAsDataURL(file);
  }, [upload.file]);

  const handleAnalyze = useCallback(async () => {
    if (isAnalyzing) {
      return;
    }

    setIsAnalyzing(true);
    setGeminiAnalysis(null);
    setAnalyzeError(null);

    try {
      if (uploadMode === "single") {
        if (!upload.file) {
          setIsAnalyzing(false);
          return;
        }
        const response = await analyzeImageWithGeminiAPI(upload.file);
        setGeminiAnalysis(response);
      } else {
        // Multi-image mode: send all images via batch upload to backend
        if (multiUpload.images.length === 0) {
          setAnalyzeError("Please upload at least one image.");
          setIsAnalyzing(false);
          return;
        }

        // Use the first image for analysis via existing Gemini route
        // (Group analysis with backend API is available as beta feature)
        const response = await analyzeImageWithGeminiAPI(multiUpload.images[0].file);
        setGeminiAnalysis(response);
      }
      setIsAnalyzing(false);
    } catch (err: any) {
      setAnalyzeError(err.message || "Analysis failed. Please try again.");
      setIsAnalyzing(false);
    }
  }, [upload.file, isAnalyzing, setIsAnalyzing, setGeminiAnalysis, uploadMode, multiUpload.images]);

  const canAnalyze = uploadMode === "single"
    ? !!upload.previewUrl && upload.status !== "error"
    : multiUpload.images.length > 0;

  const hasGeminiResult = geminiAnalysis && !isAnalyzing;

  return (
    <div className="flex gap-8">
      <div className="flex-1 min-w-0 max-w-4xl">
        {/* Breadcrumb */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.3 }}
          className="flex items-center gap-2 text-xs mb-8"
          style={{ color: "var(--theme-text-secondary)" }}
        >
          <span className="font-semibold" style={{ color: "var(--theme-text)" }}>Dashboard</span>
          <ChevronRight size={10} style={{ opacity: 0.3 }} />
          <span>New Analysis</span>
        </motion.div>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.4, delay: 0.05, ease: [0.16, 1, 0.3, 1] }}
          className="mb-10"
        >
          <h1 className="text-3xl font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>New Analysis</h1>
          <p className="mt-2 text-sm" style={{ color: "var(--theme-text-secondary)" }}>
            Upload any image — MORAA GemVision will auto-detect the category and generate a detailed AI analysis.
          </p>
        </motion.div>


        {/* Upload Area */}
        <motion.div
          key={uploadMode}
          initial={{ opacity: 0, y: 16 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.4, delay: 0.12, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <UnifiedUploadCard />
            <AnimatePresence mode="wait">
              {upload.previewUrl ? (
                <motion.div
                  key="preview"
                  initial={{ opacity: 0, scale: 0.96 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.96 }}
                  transition={{ duration: 0.35 }}
                >
                  <PreviewCard />
                </motion.div>
              ) : (
                <div className="hidden lg:flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center min-h-[320px] backdrop-blur-sm" style={{ borderColor: "var(--theme-border)", backgroundColor: "var(--theme-glass)" }}>
                  <div className="relative mb-4">
                    <div className="absolute -inset-4 bg-[#3B82F6] opacity-[0.04] blur-2xl rounded-full" />
                    <Gem size={40} className="relative" style={{ color: "var(--theme-text-secondary)", opacity: 0.3 }} />
                  </div>
                  <p className="text-sm font-medium" style={{ color: "var(--theme-text-secondary)", opacity: 0.5 }}>Preview will appear here</p>
                </div>
              )}
            </AnimatePresence>
          </div>

          {/* Analyze Button */}
          <AnimatePresence mode="wait">
            {canAnalyze && (
              <motion.div
                key="analyze-btn"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 12 }}
                className="mt-10 flex justify-center"
              >
                <motion.button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  whileHover={!isAnalyzing ? { scale: 1.03 } : {}}
                  whileTap={!isAnalyzing ? { scale: 0.97 } : {}}
                  className="group relative flex items-center gap-3 rounded-2xl px-10 py-3.5 text-base font-semibold text-white overflow-hidden transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-[0_8px_32px_rgba(59,130,246,0.25)]"
                  style={{
                    background: isAnalyzing 
                      ? 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)'
                      : 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
                  }}
                >
                  <span className="absolute inset-0 rounded-2xl pointer-events-none" style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.12) 0%, transparent 50%)' }} />
                  <span className="absolute inset-0 rounded-2xl pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-500" style={{ background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent)', transform: 'skewX(-20deg)' }} />
                  <span className="absolute -inset-2 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" style={{ background: 'radial-gradient(ellipse at center, rgba(59,130,246,0.35) 0%, transparent 70%)', filter: 'blur(24px)' }} />

                  <span className="relative z-10 flex items-center gap-3">
                    {isAnalyzing ? (
                      <>
                        <Loader2 size={20} className="animate-spin" />
                        <span>Analyzing{uploadMode === "multi" ? " all images" : ""}...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles size={20} className="transition-all duration-300 group-hover:rotate-12 group-hover:scale-110" />
                        <span>{uploadMode === "multi" ? "Analyse All Images" : "Analyse Image"}</span>
                        <ArrowUp size={16} className="transition-all duration-300 group-hover:translate-y-[-3px]" />
                      </>
                    )}
                  </span>
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Analysis Error — Compact, professional alert */}
        <AnimatePresence>
          {analyzeError && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8, scale: 0.96 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className="mt-6 flex items-start gap-2.5 rounded-xl border border-red-500/15 bg-red-500/6 px-4 py-3"
            >
              <AlertTriangle size={14} className="text-red-400 shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-red-400/90">Analysis Failed</p>
                <p className="text-xs text-red-400/60 mt-0.5 leading-relaxed">{analyzeError}</p>
              </div>
              <button
                onClick={() => setAnalyzeError(null)}
                className="shrink-0 w-5 h-5 flex items-center justify-center rounded-full text-red-400/50 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200"
                aria-label="Dismiss error"
              >
                <X size={12} />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading */}
        <AnimatePresence mode="wait">
          {isAnalyzing && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-16"
            >
              <div className="relative">
                <div className="h-20 w-20 rounded-full border-[3px] animate-spin shadow-[0_0_40px_rgba(59,130,246,0.1)]" style={{ borderColor: "var(--theme-border)", borderTopColor: "#3B82F6" }} />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Gem size={24} className="text-[#3B82F6]" />
                </div>
              </div>
              <p className="mt-6 text-base font-medium" style={{ color: "var(--theme-text-secondary)" }}>Understanding Product...</p>
              <p className="mt-2 text-sm" style={{ color: "var(--theme-text-secondary)", opacity: 0.6 }}>Analyzing materials, design, and market positioning</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <AnimatePresence mode="wait">
          {hasGeminiResult && (
            <motion.section
              key="result"
              initial={{ opacity: 0, y: 32 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              className="mt-8"
            >
              {/* Prompt Generation Panel */}
              {imageData && (
                <div className="mt-10">
                  <PromptGenerationPanel
                    analysisResult={geminiAnalysis?.data || null}
                    imageBase64={imageData.base64}
                    mimeType={imageData.mimeType}
                    file={upload.file || undefined}
                  />
                </div>
              )}
            </motion.section>
          )}
        </AnimatePresence>
      </div>

      {/* Right Sidebar */}
      <aside className="hidden lg:block w-[280px] shrink-0">
        <div className="sticky top-[76px] space-y-5">
          <div className="rounded-2xl glass-card p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg neumorphic">
                <History size={13} className="text-[#3B82F6]" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text)" }}>Previous Uploads</span>
            </div>
            <div className="flex flex-col items-center py-6 text-center">
              <div className="relative mb-3">
                <div className="absolute -inset-3 bg-[#3B82F6] opacity-[0.04] blur-xl rounded-full" />
                <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-[#3B82F6]/5 border border-[#3B82F6]/10">
                  <ImageIcon size={18} style={{ color: "var(--theme-text-secondary)", opacity: 0.5 }} />
                </div>
              </div>
              <p className="text-sm font-medium" style={{ color: "var(--theme-text-secondary)" }}>No uploads yet</p>
              <p className="text-xs mt-1 leading-relaxed max-w-[160px]" style={{ color: "var(--theme-text-secondary)", opacity: 0.55 }}>
                Your upload history will appear after your first analysis
              </p>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
