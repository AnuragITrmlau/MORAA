"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useUIStore } from "@/stores/ui-store";
import { analyzeImageWithGeminiAPI } from "@/services/gemini-analysis.service";
import UnifiedUploadCard from "@/components/UnifiedUploadCard";
import PreviewCard from "@/components/PreviewCard";
import {
  Sparkles,
  ArrowUp,
  Loader2,
  Gem,
  Clock,
  Lightbulb,
  Activity,
  ImageIcon,
  AlertTriangle,
  X,
} from "lucide-react";

export default function DashboardPage() {
  const { upload, isAnalyzing, setIsAnalyzing, geminiAnalysis, setGeminiAnalysis, uploadMode, multiUpload } = useUIStore();
  const [mounted, setMounted] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

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
        if (multiUpload.images.length === 0) {
          setAnalyzeError("Please upload at least one image.");
          setIsAnalyzing(false);
          return;
        }
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
      <div className="flex-1 min-w-0">
        {/* ===== Hero Section ===== */}
        <div className="relative mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={mounted ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="relative"
          >
            {/* Premium badge */}
            <div className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-[#3B82F6]/12 to-[#3B82F6]/5 border border-[#3B82F6]/15 px-4 py-1.5 mb-4 neumorphic">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full rounded-full bg-[#3B82F6] opacity-60 animate-ping" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-[#3B82F6] shadow-[0_0_6px_rgba(59,130,246,0.5)]" />
              </span>
              <span className="text-xs font-semibold text-[#3B82F6] tracking-wide">
                Powered by Advanced AI
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight leading-[1.1]" style={{ color: "var(--theme-text)" }}>
              Analyse Your<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#3B82F6] to-[#60A5FA]">Images</span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400"> with AI</span>
            </h1>
            <p className="mt-4 text-base leading-relaxed max-w-2xl" style={{ color: "var(--theme-text-secondary)" }}>
              Upload any image — jewellery, electronics, documents, plants, or anything else. MORAA GemVision auto-detects the category and delivers a detailed AI-powered analysis.
            </p>
          </motion.div>
        </div>

        {/* ===== Upload + Preview Section ===== */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
        >

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
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
                <div className="hidden xl:flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center min-h-[320px] backdrop-blur-sm" style={{ borderColor: "var(--theme-border)", backgroundColor: "var(--theme-glass)" }}>
                  <div className="relative mb-4">
                    <div className="absolute -inset-4 bg-[#3B82F6] opacity-[0.04] blur-2xl rounded-full" />
                    <ImageIcon size={40} className="relative" style={{ color: "var(--theme-text-secondary)" }} />
                  </div>
                  <p className="text-sm font-medium" style={{ color: "var(--theme-text-secondary)" }}>Upload an image to see preview here</p>
                  <p className="text-xs mt-1.5" style={{ color: "var(--theme-text-secondary)" }}>AI will analyse and auto-detect the category</p>
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
                transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
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
        </motion.section>

        {/* ===== Analysis Error — Compact, professional alert ===== */}
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

        {/* ===== Loading State ===== */}
        <AnimatePresence mode="wait">
          {isAnalyzing && !hasGeminiResult && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-16"
            >
              <div className="relative">
                <div className="h-20 w-20 rounded-full border-[3px] border-t-[#3B82F6] animate-spin shadow-[0_0_40px_rgba(59,130,246,0.1)]" style={{ borderColor: "var(--theme-border)" }} />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Gem size={24} className="text-[#3B82F6]" />
                </div>
              </div>
              <p className="mt-6 text-base font-medium" style={{ color: "var(--theme-text-secondary)" }}>Understanding Product...</p>
              <p className="mt-2 text-sm" style={{ color: "var(--theme-text-secondary)", opacity: 0.6 }}>Analyzing design, materials, and market positioning</p>
            </motion.div>
          )}
        </AnimatePresence>


      </div>

      {/* ===== Right Sidebar Widgets ===== */}
      <aside className="hidden lg:block w-[280px] shrink-0">
        <div className="space-y-5 sticky top-[76px]">
          {/* System Status */}
          <div className="rounded-2xl glass-card-deep p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg neumorphic">
                <Activity size={13} className="text-green-400 drop-shadow-[0_0_4px_rgba(34,197,94,0.3)]" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text)" }}>System Status</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-60 animate-ping" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.5)]" />
              </span>
              <div>
                <span className="text-sm font-medium" style={{ color: "var(--theme-text)" }}>All Operational</span>
                <p className="text-xs mt-0.5" style={{ color: "var(--theme-text-secondary)" }}>AI engine ready</p>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2.5 text-xs border-t pt-3" style={{ color: "var(--theme-text-secondary)", borderColor: "var(--theme-border)" }}>
              <Clock size={12} />
              <span>Real-time AI analysis</span>
            </div>
          </div>

          {/* Recent Analyses */}
          <div className="rounded-2xl glass-card p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg neumorphic">
                <ImageIcon size={13} className="text-[#3B82F6]" />
              </div>
              <h3 className="text-xs font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text)" }}>Recent Analyses</h3>
            </div>
            <div className="flex flex-col items-center py-6 text-center">
              <div className="relative mb-3">
                <div className="absolute -inset-3 bg-[#3B82F6] opacity-[0.04] blur-xl rounded-full" />
                <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-[#3B82F6]/5 border border-[#3B82F6]/10">
                  <ImageIcon size={18} style={{ color: "var(--theme-text-secondary)", opacity: 0.5 }} />
                </div>
              </div>
              <p className="text-sm font-medium" style={{ color: "var(--theme-text-secondary)" }}>No analyses yet</p>
              <p className="text-xs mt-1 leading-relaxed max-w-[160px]" style={{ color: "var(--theme-text-secondary)", opacity: 0.55 }}>
                Upload your first image to get started
              </p>
            </div>
          </div>

          {/* Tips */}
          <div className="rounded-2xl glass-card p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg neumorphic">
                <Lightbulb size={13} className="text-amber-400 drop-shadow-[0_0_4px_rgba(251,191,36,0.3)]" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text)" }}>Pro Tips</span>
            </div>
            <ul className="space-y-4">
              <li className="flex items-start gap-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg shrink-0 mt-0.5" style={{ backgroundColor: "var(--theme-neumorphic)", borderColor: "var(--theme-border-light)" }}>
                  <ImageIcon size={12} className="text-[#3B82F6]" />
                </div>
                <div>
                  <p className="text-xs font-semibold" style={{ color: "var(--theme-text)" }}>Use high-quality images</p>
                  <p className="text-xs mt-0.5 leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>Upload images with good lighting for the best AI analysis results.</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg shrink-0 mt-0.5" style={{ backgroundColor: "var(--theme-neumorphic)", borderColor: "var(--theme-border-light)" }}>
                  <span className="text-[10px] leading-none text-[#3B82F6]">Bg</span>
                </div>
                <div>
                  <p className="text-xs font-semibold" style={{ color: "var(--theme-text)" }}>Neutral background</p>
                  <p className="text-xs mt-0.5 leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>Photograph jewellery against a neutral, solid background.</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg shrink-0 mt-0.5" style={{ backgroundColor: "var(--theme-neumorphic)", borderColor: "var(--theme-border-light)" }}>
                  <span className="text-[10px] leading-none text-[#3B82F6]">4k</span>
                </div>
                <div>
                  <p className="text-xs font-semibold" style={{ color: "var(--theme-text)" }}>Full visibility</p>
                  <p className="text-xs mt-0.5 leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>Ensure the entire piece is visible and in focus.</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </aside>
    </div>
  );
}
