"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import {
  Tag,
  Gem,
  Sparkles,
  Palette,
  Wrench,
  Eye,
  FileText,
} from "lucide-react";

interface SummaryCardProps {
  analysis?: Record<string, string> | null;
  loading?: boolean;
}

const observationCards = [
  { key: "category", label: "Category", icon: Tag, color: "from-[#3B82F6]/8 to-transparent", iconColor: "text-[#3B82F6]", border: "border-[#3B82F6]/12" },
  { key: "material", label: "Possible Material", icon: Gem, color: "from-blue-500/8 to-transparent", iconColor: "text-blue-400", border: "border-blue-400/12" },
  { key: "gemstones", label: "Visible Stones", icon: Eye, color: "from-pink-500/8 to-transparent", iconColor: "text-pink-400", border: "border-pink-400/12" },
  { key: "style", label: "Design Style", icon: Palette, color: "from-purple-500/8 to-transparent", iconColor: "text-purple-400", border: "border-purple-400/12" },
  { key: "features", label: "Visible Features", icon: Sparkles, color: "from-teal-500/8 to-transparent", iconColor: "text-teal-400", border: "border-teal-400/12" },
  { key: "condition", label: "Craftsmanship Notes", icon: Wrench, color: "from-emerald-500/8 to-transparent", iconColor: "text-emerald-400", border: "border-emerald-400/12" },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const } },
};

export default function SummaryCard({ analysis, loading }: SummaryCardProps) {
  if (loading) {
    return (
      <div className="rounded-2xl glass-card p-8 space-y-5">
        <div className="skeleton h-7 w-48" />
        <div className="skeleton h-4 w-full" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton h-28 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="space-y-6"
    >
      {/* Section Heading */}
      <div className="text-center">
        <motion.h2
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
          className="text-2xl font-bold tracking-tight" style={{ color: "var(--theme-text)" }}
        >
          Analysis Results
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
          className="mt-2 text-sm" style={{ color: "var(--theme-text-secondary)" }}
        >
          Observations based on visible design characteristics
        </motion.p>
      </div>

      {/* Observation Cards */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 sm:grid-cols-2 gap-4"
      >
        {observationCards.map((card) => {
          const value = analysis?.[card.key];
          const Icon = card.icon;
          return (
            <motion.div
              key={card.key}
              variants={item}
              className={cn(
                "group relative overflow-hidden rounded-2xl p-5 transition-all duration-300",
                "bg-gradient-to-br",
                card.color,
                "border",
                card.border,
                "cursor-default glass-card"
              )}
            >
              {/* Hover light effect */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

              <div className="flex items-start gap-4 relative z-10">
                <div className={cn(
                  "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl neumorphic",
                )}>
                  <Icon size={17} className={card.iconColor} />
                </div>
                <div className="min-w-0 flex-1">                    <p className="text-[11px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>
                    {card.label}
                  </p>
                  <p className={cn(
                    "mt-1 text-sm font-medium leading-relaxed",
                    value ? "text-[var(--theme-text)]" : "italic"
                  )}>
                    {value || "Not available"}
                  </p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Overall Summary */}
      {analysis?.summary && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="relative overflow-hidden rounded-2xl glass-card p-6"
        >
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/[0.06] to-transparent pointer-events-none" />

          <div className="flex items-center gap-3 mb-4 relative z-10">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl neumorphic">
              <FileText size={15} className="text-[#3B82F6]" />
            </div>
            <span className="text-base font-semibold" style={{ color: "var(--theme-text)" }}>Summary</span>
          </div>
          <p className="text-sm leading-relaxed relative z-10" style={{ color: "var(--theme-text-secondary)" }}>
            {analysis.summary}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
}
