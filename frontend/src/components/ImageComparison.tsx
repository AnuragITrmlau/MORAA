"use client";

import { useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ComparisonInfo } from "@/types";
import {
  CheckCircle2,
  Loader2,
  AlertTriangle,
  RefreshCw,
  ZoomIn,
  ArrowDown,
  Clock,
  Hash,
  FileCheck,
} from "lucide-react";

interface ImagePanelProps {
  src: string;
  alt: string;
  label: string;
  accentColor: string;
  onError: () => void;
}

function ImagePanel({ src, alt, label, accentColor, onError }: ImagePanelProps) {
  const [loaded, setLoaded] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [zoomed, setZoomed] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 50, y: 50 });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!zoomed) return;
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      setMousePos({
        x: Math.min(100, Math.max(0, x)),
        y: Math.min(100, Math.max(0, y)),
      });
    },
    [zoomed]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        setZoomed((prev) => !prev);
      }
      if (e.key === "Escape" && zoomed) {
        setZoomed(false);
        setMousePos({ x: 50, y: 50 });
      }
    },
    [zoomed]
  );

  if (loadError) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-red-500/20 bg-red-500/5 p-8 min-h-[280px] text-center">
        <AlertTriangle size={28} className="text-red-400 mb-3" />
        <p className="text-sm font-semibold text-red-400">Failed to load image</p>
        <p className="text-xs text-red-400/70 mt-1 mb-4 max-w-[200px]">
          The {label.toLowerCase()} image could not be retrieved.
        </p>
        <button
          onClick={() => {
            setLoadError(false);
            setLoaded(false);
            onError();
          }}
          className="inline-flex items-center gap-1.5 rounded-xl bg-red-500/10 border border-red-500/20 px-4 py-2 text-xs font-semibold text-red-400 hover:bg-red-500/20 transition-colors"
        >
          <RefreshCw size={13} />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Label */}
      <div className="flex items-center gap-2">
        <div className="h-[3px] w-6 rounded-full" style={{ backgroundColor: accentColor }} />
        <span
          className="text-[11px] font-bold uppercase tracking-[0.12em]"
          style={{ color: accentColor }}
        >
          {label}
        </span>
      </div>

      {/* Image Container */}
      <div
        ref={containerRef}
        onMouseEnter={() => setZoomed(true)}
        onMouseLeave={() => {
          setZoomed(false);
          setMousePos({ x: 50, y: 50 });
        }}
        onMouseMove={handleMouseMove}
        onKeyDown={handleKeyDown}
        tabIndex={0}
        className="group relative overflow-hidden rounded-2xl border glass-card-deep transition-all duration-500 cursor-crosshair focus:outline-none focus:ring-2 focus:ring-[#3B82F6]/30"
        style={{ borderColor: "var(--theme-border-light)", minHeight: 320 }}
        role="img"
        aria-label={`${label} image - hover or press Enter to zoom and inspect details`}
      >
        {/* Loading skeleton */}
        {!loaded && (
          <div className="absolute inset-0 flex items-center justify-center z-10" style={{ backgroundColor: "var(--theme-muted)" }}>
            <Loader2 size={24} className="animate-spin" style={{ color: "var(--theme-text-secondary)" }} />
          </div>
        )}

        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={src}
          alt={alt}
          onLoad={() => setLoaded(true)}
          onError={() => {
            setLoadError(true);
            setLoaded(false);
          }}
          className={cn(
            "w-full h-full object-contain transition-all duration-500 ease-premium select-none",
            loaded ? "opacity-100" : "opacity-0 absolute",
            zoomed ? "scale-[2.2]" : "scale-100"
          )}
          style={{
            transformOrigin: zoomed ? `${mousePos.x}% ${mousePos.y}%` : "center center",
            minHeight: 320,
          }}
          draggable={false}
        />

        {/* Zoom hint - appears on hover */}
        <div
          className={cn(
            "absolute bottom-3 right-3 flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[10px] font-semibold backdrop-blur-md transition-all duration-300",
            "bg-black/40 text-white/80 border border-white/10",
            zoomed ? "opacity-0 scale-90" : "opacity-0 group-hover:opacity-100"
          )}
        >
          <ZoomIn size={12} />
          Hover to zoom
        </div>

        {/* Zoom indicator */}
        {zoomed && (
          <div className="absolute top-3 right-3 flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-semibold backdrop-blur-md bg-black/40 text-white/80 border border-white/10">
            <ZoomIn size={11} />
            2.2x
          </div>
        )}
      </div>
    </div>
  );
}

export default function ImageComparison({ comparison }: { comparison: ComparisonInfo }) {
  const [retryCount, setRetryCount] = useState(0);

  const handleRetry = useCallback(() => {
    setRetryCount((prev) => prev + 1);
  }, []);

  const hasImages = comparison.originalImageUrl || comparison.processedImageUrl;

  if (!hasImages) {
    return null;
  }

  return (
    <motion.div
      key={`comparison-${retryCount}`}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="space-y-8"
    >
      {/* Section Heading */}
      <div className="text-center">
        <motion.h2
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
          className="text-2xl font-bold tracking-tight"
          style={{ color: "var(--theme-text)" }}
        >
          Before & After
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
          className="mt-2 text-sm"
          style={{ color: "var(--theme-text-secondary)" }}
        >
          Visual comparison of original upload and processed result
        </motion.p>
      </div>

      {/* Image Panels */}
      <div className="relative grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 items-start">
        {/* Original Image */}
        <ImagePanel
          src={comparison.originalImageUrl}
          alt="Original uploaded jewellery image"
          label="Original"
          accentColor="#94A3B8"
          onError={handleRetry}
        />

        {/* Downward arrow between images (desktop) */}
        <div className="hidden md:flex absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10 pointer-events-none">
          <div className="flex flex-col items-center">
            <div className="h-12 w-[2px] rounded-full bg-gradient-to-b from-[#3B82F6]/40 to-[#3B82F6]/10" />
            <div className="mt-[-2px]">
              <ArrowDown size={16} className="text-[#3B82F6]/50" />
            </div>
          </div>
        </div>

        {/* Processed Image */}
        <ImagePanel
          src={comparison.processedImageUrl}
          alt="Processed jewellery image"
          label="Processed"
          accentColor="#3B82F6"
          onError={handleRetry}
        />
      </div>

      {/* Downward arrow between images (mobile) */}
      <div className="flex md:hidden justify-center -my-2">
        <div className="flex flex-col items-center">
          <ArrowDown size={18} className="text-[#3B82F6]/40" />
        </div>
      </div>

      {/* Processing Summary */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="grid grid-cols-1 sm:grid-cols-2 gap-4"
      >
        {/* Enhancements */}
        <div className="rounded-2xl glass-card p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg neumorphic">
              <FileCheck size={13} className="text-emerald-400" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text)" }}>
              Processing Summary
            </span>
          </div>
          <div className="space-y-2.5">
            {comparison.enhancements.map((enhancement) => (
              <div key={enhancement.name} className="flex items-center gap-2.5">
                <CheckCircle2
                  size={14}
                  className={cn(
                    "shrink-0",
                    enhancement.status === "completed"
                      ? "text-emerald-400"
                      : enhancement.status === "failed"
                      ? "text-red-400"
                      : "text-amber-400"
                  )}
                />
                <span className="text-sm" style={{ color: "var(--theme-text-secondary)" }}>
                  {enhancement.name}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Metadata */}
        <div className="rounded-2xl glass-card p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg neumorphic">
              <Clock size={13} className="text-[#3B82F6]" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text)" }}>
              Processing Details
            </span>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock size={12} style={{ color: "var(--theme-text-secondary)" }} />
                <span className="text-xs" style={{ color: "var(--theme-text-secondary)" }}>
                  Processing Time
                </span>
              </div>
              <span className="text-xs font-semibold tabular-nums" style={{ color: "var(--theme-text)" }}>
                {comparison.processingTime.toFixed(1)} sec
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Hash size={12} style={{ color: "var(--theme-text-secondary)" }} />
                <span className="text-xs" style={{ color: "var(--theme-text-secondary)" }}>
                  Request ID
                </span>
              </div>
              <span className="text-xs font-mono font-semibold" style={{ color: "var(--theme-text)" }}>
                {comparison.requestId.length > 12
                  ? `${comparison.requestId.slice(0, 12)}...`
                  : comparison.requestId}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCheck size={12} style={{ color: "var(--theme-text-secondary)" }} />
                <span className="text-xs" style={{ color: "var(--theme-text-secondary)" }}>
                  Version
                </span>
              </div>
              <span className="text-xs font-semibold" style={{ color: "var(--theme-text)" }}>
                V{comparison.version}
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
