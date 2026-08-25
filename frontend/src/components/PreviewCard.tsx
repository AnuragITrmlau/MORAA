"use client";

import { useUIStore } from "@/stores/ui-store";
import { ImageIcon, X } from "lucide-react";

export default function PreviewCard() {
  const { upload, resetUpload } = useUIStore();

  const handleRemove = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    if (upload.previewUrl) {
      URL.revokeObjectURL(upload.previewUrl);
    }
    resetUpload();
  };

  return (
    <div className="group relative overflow-hidden rounded-2xl glass-card-deep min-h-[320px] flex flex-col">
      {/* Ambient light behind preview */}
      <div className="absolute -inset-6 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" style={{
        background: 'radial-gradient(ellipse at center, rgba(59,130,246,0.08) 0%, transparent 70%)',
        filter: 'blur(50px)',
      }} />

      {/* Subtle gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#3B82F6]/0 via-transparent to-[#3B82F6]/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none z-10" />

      {/* Glass surface reflection */}
      <div className="absolute inset-0 rounded-2xl pointer-events-none" style={{ background: "linear-gradient(180deg, var(--theme-text-white-high) 0%, transparent 100%)" }} />

      {/* Image Area */}
      <div className="relative flex-1 flex items-center justify-center p-6 z-10">
        {upload.previewUrl ? (
          <div className="relative w-full flex items-center justify-center group/image">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={upload.previewUrl}
              alt="Product preview"
              className="object-contain rounded-xl w-full max-h-[300px] transition-all duration-500 group-hover/image:scale-[1.02]"
              style={{ filter: "drop-shadow(0 12px 48px var(--theme-shadow-card))" }}
            />

            {/* Remove button - top-right, always visible but subtle */}
            <button
              onClick={handleRemove}
              className="absolute top-2 right-2 flex items-center justify-center w-8 h-8 rounded-full bg-black/40 backdrop-blur-sm border border-white/10 text-white/70 hover:text-white hover:bg-black/60 hover:border-white/20 transition-all duration-200 opacity-0 group-hover/image:opacity-100"
              aria-label="Remove image"
              title="Remove image"
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="relative mb-5">
              <div className="absolute -inset-5 bg-[#3B82F6] opacity-[0.04] blur-2xl rounded-full" />
              <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl ring-1 neumorphic" style={{ backgroundColor: "var(--theme-neumorphic)", borderColor: "var(--theme-border-light)" }}>
                <ImageIcon size={28} style={{ color: "var(--theme-text-secondary)" }} />
              </div>
            </div>
            <p className="text-base font-medium" style={{ color: "var(--theme-text-secondary)" }}>Upload to see preview</p>
            <p className="text-xs mt-1.5" style={{ color: "var(--theme-text-secondary)" }}>Image analysis ready</p>
          </div>
        )}
      </div>

      {/* Footer */}
      {upload.file && (
        <div className="border-t px-6 py-3 flex items-center justify-between relative z-10" style={{ borderColor: "var(--theme-border)", backgroundColor: "var(--theme-muted)" }}>
          <span className="text-xs truncate max-w-[200px] font-medium" style={{ color: "var(--theme-text-secondary)" }}>{upload.file.name}</span>
          <div className="flex items-center gap-3">
            <span className="text-xs" style={{ color: "var(--theme-text-secondary)" }}>{(upload.file.size / 1024).toFixed(1)} KB</span>
            <button
              onClick={handleRemove}
              className="text-xs text-red-400/70 hover:text-red-400 transition-colors font-medium"
              aria-label="Remove"
            >
              Remove
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
