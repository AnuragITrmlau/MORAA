"use client";

import { useState, useCallback, useRef, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  SlidersHorizontal,
  RotateCcw,
  Download,
  Check,
  ArrowLeftRight,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  FILTERS,
  applyFilter,
  applyFilterAsBlob,
  getFilterThumbnailStyle,
  type FilterId,
} from "@/lib/filter-engine";
import { logger } from "@/lib/logger";

// --- Filter Card Thumbnail ---

function FilterThumbnail({
  imageUrl,
  filterId,
  isActive,
}: {
  imageUrl: string;
  filterId: FilterId;
  isActive: boolean;
}) {
  const cssFilter = getFilterThumbnailStyle(filterId);

  return (
    <div
      className={cn(
        "w-full aspect-square rounded-md overflow-hidden relative",
        "border transition-all duration-300",
        isActive
          ? "border-amber-500/60 shadow-[0_0_12px_rgba(245,158,11,0.2)]"
          : "border-white/[0.06] hover:border-white/[0.12]",
      )}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={imageUrl}
        alt={`${filterId} preview`}
        className="w-full h-full object-cover"
        style={{ filter: cssFilter }}
        loading="lazy"
      />
      {isActive && (
        <div className="absolute inset-0 bg-amber-500/10 pointer-events-none" />
      )}
    </div>
  );
}

// --- Before / After Slider ---

function BeforeAfterSlider({
  originalUrl,
  filteredUrl,
  filterLabel,
}: {
  originalUrl: string;
  filteredUrl: string;
  filterLabel: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState(50); // percentage
  const [isDragging, setIsDragging] = useState(false);

  const updatePosition = useCallback((clientX: number) => {
    const container = containerRef.current;
    if (!container) return;
    const rect = container.getBoundingClientRect();
    const x = clientX - rect.left;
    const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setPosition(pct);
  }, []);

  const handlePointerDown = useCallback(
    (e: React.PointerEvent) => {
      setIsDragging(true);
      updatePosition(e.clientX);
      (e.target as HTMLElement).setPointerCapture(e.pointerId);
    },
    [updatePosition],
  );

  const handlePointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (!isDragging) return;
      updatePosition(e.clientX);
    },
    [isDragging, updatePosition],
  );

  const handlePointerUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  return (
    <div
      ref={containerRef}
      className="relative w-full aspect-[4/5] max-h-[200px] rounded-lg overflow-hidden cursor-col-resize select-none"
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      style={{ touchAction: "none" }}
    >
      {/* After (filtered) — full width behind */}
      <div className="absolute inset-0">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={filteredUrl}
          alt={`After: ${filterLabel}`}
          className="w-full h-full object-contain"
        />
      </div>

      {/* Before (original) — clipped */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{ width: `${position}%` }}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={originalUrl}
          alt="Before (original)"
          className="w-full h-full object-contain"
          style={{
            /* Constrain to parent width so the image doesn't shift */
            minWidth: containerRef.current?.offsetWidth ?? 400,
            maxWidth: "none",
          }}
        />
      </div>

      {/* Divider line */}
      <div
        className="absolute top-0 bottom-0 w-[2px] bg-white/80 shadow-[0_0_8px_rgba(255,255,255,0.3)] z-10"
        style={{ left: `${position}%`, transform: "translateX(-50%)" }}
      >
        {/* Drag handle */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center shadow-lg cursor-col-resize">
          <ArrowLeftRight size={10} className="text-black/70" />
        </div>
      </div>

      {/* Labels */}
      <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/60 backdrop-blur-sm text-[9px] font-semibold text-white/90 uppercase tracking-wider z-10">
        Before
      </div>
      <div className="absolute top-2 right-2 px-2 py-0.5 rounded bg-black/60 backdrop-blur-sm text-[9px] font-semibold text-white/90 uppercase tracking-wider z-10">
        After
      </div>
    </div>
  );
}

// --- Main Component ---

interface PhotoFilterPanelProps {
  /** URL of the original AI-generated image */
  originalImageUrl: string;
  /** Callback when download is requested */
  onDownload?: (blob: Blob, filename: string) => void;
}

export default function PhotoFilterPanel({
  originalImageUrl,
  onDownload,
}: PhotoFilterPanelProps) {
  const [selectedFilter, setSelectedFilter] = useState<FilterId>("original");
  const [filteredImageUrl, setFilteredImageUrl] = useState<string>(
    originalImageUrl,
  );
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloaded, setDownloaded] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  // Scroll container for filter cards
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Keep filtered image in sync when original changes
  useEffect(() => {
    if (selectedFilter === "original") {
      setFilteredImageUrl(originalImageUrl);
    }
  }, [originalImageUrl, selectedFilter]);

  // Apply filter when selection changes
  useEffect(() => {
    if (selectedFilter === "original") {
      setFilteredImageUrl(originalImageUrl);
      setError(null);
      return;
    }

    let cancelled = false;

    const run = async () => {
      setIsProcessing(true);
      setError(null);
      try {
        const result = await applyFilter(originalImageUrl, selectedFilter);
        if (!cancelled) {
          setFilteredImageUrl(result);
        }
      } catch (err) {
        if (!cancelled) {
          const msg =
            err instanceof Error ? err.message : "Filter application failed";
          logger.error("Filter error", { filter: selectedFilter, error: msg });
          setError(msg);
          setFilteredImageUrl(originalImageUrl);
          setSelectedFilter("original");
        }
      } finally {
        if (!cancelled) setIsProcessing(false);
      }
    };

    run();
    return () => {
      cancelled = true;
    };
  }, [selectedFilter, originalImageUrl]);

  // Reset
  const handleReset = useCallback(() => {
    setSelectedFilter("original");
    setFilteredImageUrl(originalImageUrl);
    setShowComparison(false);
    setError(null);
  }, [originalImageUrl]);

  // Download filtered image
  const handleDownload = useCallback(async () => {
    try {
      let blob: Blob;
      if (selectedFilter === "original") {
        const response = await fetch(originalImageUrl);
        blob = await response.blob();
      } else {
        blob = await applyFilterAsBlob(originalImageUrl, selectedFilter);
      }

      const filterLabel =
        selectedFilter === "original"
          ? "original"
          : selectedFilter.replace(/\s+/g, "_").toLowerCase();

      const filename = `moraa_gemvision_${filterLabel}.jpg`;

      if (onDownload) {
        onDownload(blob, filename);
      } else {
        // Default download behavior
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }

      setDownloaded(true);
      setTimeout(() => setDownloaded(false), 2000);
    } catch (err) {
      logger.error("Failed to download filtered image", {
        error: String(err),
      });
    }
  }, [selectedFilter, originalImageUrl, onDownload]);

  // Scroll filter list
  const scrollFilters = useCallback((direction: "left" | "right") => {
    const container = scrollContainerRef.current;
    if (!container) return;
    const scrollAmount = 200;
    container.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  }, []);

  const activeFilterDef = useMemo(
    () => FILTERS.find((f) => f.id === selectedFilter),
    [selectedFilter],
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="rounded-2xl border overflow-hidden"
      style={{
        borderColor: "var(--theme-border)",
        backgroundColor: "var(--theme-glass)",
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/10">
            <SlidersHorizontal size={12} className="text-amber-400" />
          </div>
          <div>
            <h4 className="text-xs font-bold" style={{ color: "var(--theme-text)" }}>
              Photo Filters
            </h4>
          </div>
        </div>

        {/* Active filter indicator */}
        {selectedFilter !== "original" && (
          <motion.span
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-[9px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400"
          >
            {activeFilterDef?.emoji} {activeFilterDef?.label}
          </motion.span>
        )}
      </div>

      {/* Error Banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="px-3 pb-2"
          >
            <div className="flex items-start gap-2 rounded-lg bg-red-500/10 border border-red-500/20 px-3 py-2">
              <AlertTriangle size={12} className="text-red-400 shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-red-400/80">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="shrink-0 text-red-400/50 hover:text-red-400 transition-colors"
                aria-label="Dismiss error"
              >
                ×
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <div className="px-3 pb-2 space-y-1.5">
        {/* Before / After Comparison */}
        <AnimatePresence mode="wait">
          {showComparison && (
            <motion.div
              key="comparison"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <BeforeAfterSlider
                originalUrl={originalImageUrl}
                filteredUrl={filteredImageUrl}
                filterLabel={activeFilterDef?.label ?? "Original"}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="flex items-center justify-center gap-2 py-1">
            <div
              className="w-4 h-4 rounded-full border-2 animate-spin"
              style={{
                borderColor: "var(--theme-border)",
                borderTopColor: "#F59E0B",
              }}
            />
            <span
              className="text-[11px] font-medium"
              style={{ color: "var(--theme-text-secondary)" }}
            >
              Applying filter...
            </span>
          </div>
        )}

        {/* Filter Cards — Horizontally Scrollable */}
        <div className="relative">
          {/* Scroll Left Button */}
          <button
            onClick={() => scrollFilters("left")}
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-6 h-6 rounded-full bg-black/60 backdrop-blur-sm flex items-center justify-center text-white/70 hover:text-white hover:bg-black/80 transition-all opacity-0 hover:opacity-100 group-hover:opacity-100"
            style={{ left: "-8px" }}
            aria-label="Scroll filters left"
          >
            <ChevronLeft size={12} />
          </button>

          <div
            ref={scrollContainerRef}
            className="flex gap-2 overflow-x-auto pb-0.5 scrollbar-none"
            style={{
              scrollbarWidth: "none",
              msOverflowStyle: "none",
              WebkitOverflowScrolling: "touch",
            }}
          >
            {FILTERS.map((filter) => {
              const isActive = selectedFilter === filter.id;
              return (
                <motion.button
                  key={filter.id}
                  onClick={() => setSelectedFilter(filter.id)}
                  whileTap={{ scale: 0.95 }}
                  className={cn(
                    "shrink-0 flex flex-col items-center gap-0.5 p-1 rounded-lg transition-all duration-200",
                    "min-w-[48px] group/card",
                    isActive
                      ? "bg-amber-500/10 ring-1 ring-amber-500/30"
                      : "hover:bg-white/[0.04]",
                  )}
                  disabled={isProcessing}
                >
                  <FilterThumbnail
                    imageUrl={originalImageUrl}
                    filterId={filter.id}
                    isActive={isActive}
                  />
                  <span
                    className={cn(
                      "text-[8px] font-medium transition-colors duration-200 whitespace-nowrap",
                      isActive ? "text-amber-400" : "text-[var(--theme-text-secondary)]",
                    )}
                  >
                    {filter.emoji} {filter.label}
                  </span>
                </motion.button>
              );
            })}
          </div>

          {/* Scroll Right Button */}
          <button
            onClick={() => scrollFilters("right")}
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-6 h-6 rounded-full bg-black/60 backdrop-blur-sm flex items-center justify-center text-white/70 hover:text-white hover:bg-black/80 transition-all opacity-0 hover:opacity-100 group-hover:opacity-100"
            style={{ right: "-8px" }}
            aria-label="Scroll filters right"
          >
            <ChevronRight size={12} />
          </button>
        </div>

        {/* Action Bar */}
        <div className="flex items-center justify-between pt-0.5">
          <div className="flex items-center gap-2">
            {/* Before / After Toggle */}
            <button
              onClick={() => setShowComparison(!showComparison)}
              className={cn(
                "flex items-center gap-1 rounded-md px-2 py-1 text-[10px] font-semibold transition-all duration-200",
                "active:scale-95",
                showComparison
                  ? "bg-blue-500/15 text-blue-400 border border-blue-500/20"
                  : "hover:bg-white/[0.06] border border-transparent",
              )}
              style={{
                color: showComparison ? undefined : "var(--theme-text-secondary)",
              }}
            >
              <ArrowLeftRight size={12} />
              {showComparison ? "Hide Comparison" : "Before / After"}
            </button>

            {/* Reset */}
            {selectedFilter !== "original" && (
              <motion.button
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                onClick={handleReset}
                className="flex items-center gap-1 rounded-md px-2 py-1 text-[10px] font-semibold hover:bg-white/[0.06] active:scale-95 transition-all duration-200 border border-transparent"
                style={{ color: "var(--theme-text-secondary)" }}
              >
                <RotateCcw size={12} />
                Reset
              </motion.button>
            )}
          </div>

          {/* Download */}
          <button
            onClick={handleDownload}
            className="flex items-center gap-1 rounded-md px-2 py-1 text-[10px] font-semibold transition-all duration-200 hover:bg-white/[0.08] active:scale-95"
            style={{
              color: downloaded ? "#22C55E" : "var(--theme-text-secondary)",
            }}
          >
            {downloaded ? (
              <>
                <Check size={12} />
                Downloaded
              </>
            ) : (
              <>
                <Download size={12} />
                Download
              </>
            )}
          </button>
        </div>
      </div>
    </motion.div>
  );
}
