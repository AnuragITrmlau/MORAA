"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";
import { Upload, X, AlertCircle, CheckCircle2, ImagePlus } from "lucide-react";

const MAX_FILES = 10;
const MAX_FILE_SIZE_MB = 10;
const ACCEPTED_TYPES = ["image/png", "image/jpeg", "image/webp"];

export default function UnifiedUploadCard() {
  const {
    upload,
    multiUpload,
    removeMultiImage,
    resetUpload,
    clearMultiUpload,
  } = useUIStore();

  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const progressTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Mirrors `progress` outside React state so the completion side-effects
  // (store updates) can run in the interval callback — an async context —
  // instead of inside a setState updater (which React may invoke during the
  // render phase, causing "Cannot update a component while rendering").
  const progressRef = useRef<number>(0);

  useEffect(() => {
    return () => {
      if (progressTimer.current) clearInterval(progressTimer.current);
      if (hideTimer.current) clearTimeout(hideTimer.current);
    };
  }, []);

  const validateFile = useCallback((file: File): string | null => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      return `"${file.name}" has an unsupported format. Use PNG, JPEG, or WEBP.`;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      return `"${file.name}" is too large (max ${MAX_FILE_SIZE_MB} MB).`;
    }
    return null;
  }, []);

  const simulateProgress = useCallback((isMulti: boolean) => {
    if (progressTimer.current) clearInterval(progressTimer.current);
    if (hideTimer.current) clearTimeout(hideTimer.current);
    progressRef.current = 5;
    setProgress(5);
    progressTimer.current = setInterval(() => {
      // Compute the next value from the ref (NOT inside the setState updater)
      // and perform the store side-effects here, in the async tick, so no
      // state update ever happens during React's render phase.
      const next = Math.min(100, progressRef.current + Math.random() * 22 + 8);
      progressRef.current = next;
      setProgress(next);
      if (next >= 100) {
        if (progressTimer.current) {
          clearInterval(progressTimer.current);
          progressTimer.current = null;
        }
        if (isMulti) {
          useUIStore.getState().setMultiUpload({ status: "completed" });
        } else {
          useUIStore.getState().setUpload({ status: "completed", progress: 100 });
        }
        hideTimer.current = setTimeout(() => setProgress(null), 450);
      }
    }, 120);
  }, []);

  const processFiles = useCallback(
    (files: FileList | File[]) => {
      const fileArray = Array.from(files);
      if (fileArray.length === 0) return;

      const store = useUIStore.getState();

      const errors: string[] = [];
      const valid: File[] = [];
      for (const file of fileArray) {
        const validationError = validateFile(file);
        if (validationError) errors.push(validationError);
        else valid.push(file);
      }
      setError(errors.length > 0 ? errors.join("\n") : null);
      if (valid.length === 0) return;

      store.setGeminiAnalysis(null);

      if (valid.length === 1) {
        const file = valid[0];
        if (upload.previewUrl) URL.revokeObjectURL(upload.previewUrl);
        if (multiUpload.images.length > 0) {
          multiUpload.images.forEach((img) => URL.revokeObjectURL(img.previewUrl));
        }
        const url = URL.createObjectURL(file);
        store.setUploadMode("single");
        store.setUpload({
          file,
          previewUrl: url,
          status: "uploading",
          progress: 0,
          errorMessage: null,
        });
        simulateProgress(false);
      } else {
        const currentCount = multiUpload.images.length;
        if (currentCount + valid.length > MAX_FILES) {
          setError(`Maximum ${MAX_FILES} images (${currentCount} already added).`);
          return;
        }
        if (upload.previewUrl) URL.revokeObjectURL(upload.previewUrl);
        store.setUploadMode("multi");
        const startOrder = multiUpload.images.length;
        valid.forEach((file, i) => {
          const url = URL.createObjectURL(file);
          store.addMultiImage({
            id: `img_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
            file,
            previewUrl: url,
            order: startOrder + i,
            status: "pending",
            filename: file.name,
            size: file.size,
          });
        });
        store.setMultiUpload({ status: "uploading", errorMessage: null });
        simulateProgress(true);
      }
    },
    [validateFile, simulateProgress, upload.previewUrl, multiUpload.images]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (e.dataTransfer.files.length > 0) processFiles(e.dataTransfer.files);
    },
    [processFiles]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => setDragOver(false), []);

  const handleClick = useCallback(() => inputRef.current?.click(), []);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        processFiles(e.target.files);
      }
      e.target.value = "";
    },
    [processFiles]
  );

  const handleRemoveSingle = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      if (upload.previewUrl) URL.revokeObjectURL(upload.previewUrl);
      resetUpload();
      setError(null);
      if (inputRef.current) inputRef.current.value = "";
    },
    [upload.previewUrl, resetUpload]
  );

  const handleRemoveMulti = useCallback(
    (id: string, e: React.MouseEvent) => {
      e.stopPropagation();
      const item = multiUpload.images.find((img) => img.id === id);
      if (item) URL.revokeObjectURL(item.previewUrl);
      removeMultiImage(id);
    },
    [multiUpload.images, removeMultiImage]
  );

  const handleClearAll = useCallback(() => {
    multiUpload.images.forEach((img) => URL.revokeObjectURL(img.previewUrl));
    clearMultiUpload();
    setError(null);
  }, [multiUpload.images, clearMultiUpload]);

  const hasMulti = multiUpload.images.length > 0;
  const hasSingle = !!upload.previewUrl;
  const isEmpty = !hasMulti && !hasSingle;

  return (
    <div className="flex flex-col gap-4">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={isEmpty ? handleClick : undefined}
        className={cn(
          "group relative cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed p-8 sm:p-10 transition-all duration-300 min-h-[320px] flex items-center justify-center",
          dragOver
            ? "border-amber-500/60 bg-amber-500/[0.06]"
            : error
            ? "border-red-500/40 bg-red-500/5"
            : !isEmpty
            ? "border-emerald-400/25 bg-emerald-500/[0.03]"
            : "hover:border-amber-500/30"
        )}
        style={
          !dragOver && !error && isEmpty
            ? { borderColor: "var(--theme-border)" }
            : undefined
        }
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if ((e.key === "Enter" || e.key === " ") && isEmpty) {
            e.preventDefault();
            handleClick();
          }
        }}
        aria-label={
          hasMulti
            ? `${multiUpload.images.length} images ready for analysis`
            : hasSingle
            ? "1 image ready for analysis"
            : "Upload jewellery images - drag and drop or click to browse"
        }
      >
        <div
          className="absolute -inset-8 rounded-full pointer-events-none transition-all duration-500 opacity-0 group-hover:opacity-100"
          style={{
            background:
              "radial-gradient(ellipse at center, rgba(245,158,11,0.10) 0%, transparent 70%)",
            filter: "blur(60px)",
            display: isEmpty ? undefined : "none",
          }}
        />

        <input
          ref={inputRef}
          type="file"
          multiple
          accept="image/*"
          className="hidden"
          onChange={handleChange}
        />

        {hasMulti ? (
          <div className="relative z-10 w-full" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4 px-1">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-emerald-400" />
                <span className="text-sm font-medium" style={{ color: "var(--theme-text)" }}>
                  {multiUpload.images.length} image
                  {multiUpload.images.length !== 1 ? "s" : ""}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClick();
                  }}
                  className="text-xs font-semibold uppercase tracking-wider text-amber-500 hover:text-amber-400 transition-colors"
                >
                  Add More
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClearAll();
                  }}
                  className="text-xs font-semibold uppercase tracking-wider text-red-400/70 hover:text-red-400 transition-colors"
                >
                  Clear All
                </button>
              </div>
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
              <AnimatePresence mode="popLayout">
                {multiUpload.images.map((item) => (
                  <motion.div
                    key={item.id}
                    layout
                    initial={{ opacity: 0, scale: 0.85 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.85 }}
                    transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
                    className="group/image relative aspect-square rounded-xl overflow-hidden border"
                    style={{ borderColor: "var(--theme-border)" }}
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={item.previewUrl}
                      alt={item.filename}
                      className="object-contain w-full h-full rounded-xl transition-all duration-300 group-hover/image:scale-105"
                      style={{ backgroundColor: "var(--theme-neumorphic)" }}
                    />
                    <div className="absolute top-1.5 left-1.5 w-5 h-5 flex items-center justify-center rounded-full bg-black/50 backdrop-blur-sm text-[10px] font-semibold text-white/80">
                      {item.order + 1}
                    </div>
                    <button
                      onClick={(e) => handleRemoveMulti(item.id, e)}
                      className="absolute top-1.5 right-1.5 flex items-center justify-center w-5 h-5 rounded-full bg-black/50 backdrop-blur-sm border border-white/10 text-white/70 hover:text-white hover:bg-black/70 transition-all duration-200 opacity-0 group-hover/image:opacity-100"
                      aria-label={`Remove ${item.filename}`}
                      title="Remove image"
                    >
                      <X size={10} />
                    </button>
                    <div className="absolute bottom-0 inset-x-0 px-2 py-1.5 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover/image:opacity-100 transition-opacity duration-200 pointer-events-none">
                      <p className="text-[10px] text-white/80 truncate">{item.filename}</p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>
        ) : hasSingle ? (
          <div
            className="relative z-10 w-full h-full flex flex-col items-center justify-center p-2"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative flex-1 w-full flex items-center justify-center min-h-0">
              <div className="relative w-full max-w-full max-h-[260px] flex items-center justify-center">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={upload.previewUrl || ""}
                  alt={upload.file?.name || "Uploaded image preview"}
                  className="object-contain w-full h-full max-h-[260px] rounded-xl transition-all duration-500"
                  style={{ filter: "drop-shadow(0 8px 32px var(--theme-shadow-card))" }}
                />
                <button
                  onClick={handleRemoveSingle}
                  className="absolute top-2 right-2 flex items-center justify-center w-8 h-8 rounded-full bg-black/50 backdrop-blur-sm border border-white/10 text-white/80 hover:text-white hover:bg-black/70 hover:border-white/20 transition-all duration-200 z-20"
                  aria-label="Remove image"
                  title="Remove image"
                >
                  <X size={14} />
                </button>
              </div>
            </div>

            <div className="mt-3 w-full flex items-center justify-between px-1">
              <div className="flex items-center gap-2 min-w-0">
                <CheckCircle2 size={14} className="text-emerald-400 shrink-0" />
                <span
                  className="text-xs font-medium truncate"
                  style={{ color: "var(--theme-text-secondary)" }}
                >
                  {upload.file?.name}
                </span>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <span className="text-xs tabular-nums" style={{ color: "var(--theme-text-secondary)" }}>
                  {upload.file?.size ? `${(upload.file.size / 1024).toFixed(1)} KB` : ""}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClick();
                  }}
                  className="text-[10px] font-semibold uppercase tracking-wider text-amber-500 hover:text-amber-400 transition-colors"
                >
                  Replace
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center text-center relative z-10">
            <div className="relative mb-6">
              <div className="absolute -inset-6 bg-amber-500 opacity-[0.06] blur-3xl rounded-full transition-all duration-500 group-hover:opacity-[0.15] group-hover:scale-110" />
              <div
                className="relative flex h-20 w-20 items-center justify-center rounded-2xl ring-1 transition-all duration-500 group-hover:scale-110 group-hover:ring-amber-500/25 neumorphic"
                style={{
                  backgroundColor: "var(--theme-neumorphic)",
                  borderColor: "var(--theme-border-light)",
                }}
              >
                <ImagePlus
                  size={28}
                  className="transition-all duration-500 group-hover:text-amber-500 group-hover:drop-shadow-[0_0_12px_rgba(245,158,11,0.5)]"
                  style={{ color: "var(--theme-text-secondary)" }}
                />
              </div>
            </div>

            <h3 className="text-xl font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>
              Upload Jewellery Images
            </h3>
            <p className="mt-2 text-sm max-w-xs leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>
              Drag and drop one or more images, or click to browse
            </p>

            <button
              onClick={(e) => {
                e.stopPropagation();
                handleClick();
              }}
              className="btn-primary mt-6 rounded-2xl px-8 py-3 text-sm font-semibold shadow-[0_8px_24px_rgba(245,158,11,0.18)]"
              aria-label="Choose files to upload"
            >
              <span className="relative z-10 flex items-center gap-2">
                <Upload size={16} />
                Choose Images
              </span>
            </button>

            <p className="mt-4 text-xs" style={{ color: "var(--theme-text-secondary)" }}>
              PNG, JPEG, WEBP · max {MAX_FILE_SIZE_MB} MB each · up to {MAX_FILES} images
            </p>
          </div>
        )}

        {progress !== null && (
          <div className="absolute bottom-0 left-0 right-0 z-20 h-[3px] bg-white/[0.06]">
            <div
              className="h-full rounded-r-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-150 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="flex items-start gap-2 rounded-xl bg-red-500/10 border border-red-500/20 px-4 py-2.5"
          >
            <AlertCircle size={14} className="text-red-400 shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              {error.split("\n").map((line, i) => (
                <p key={i} className="text-xs text-red-400/80">
                  {line}
                </p>
              ))}
            </div>
            <button
              onClick={() => setError(null)}
              className="shrink-0 text-red-400/50 hover:text-red-400 transition-colors"
              aria-label="Dismiss error"
            >
              <X size={14} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
