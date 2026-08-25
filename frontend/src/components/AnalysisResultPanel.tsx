"use client";

import { motion } from "framer-motion";
import type {
  AnalysisResponse,
  JewelleryAnalysisResult,
  GeneralAnalysisResult,
} from "@/types/analysis";
import { isJewelleryAnalysis } from "@/types/analysis";
import { getCategoryLabel, formatConfidence, getConfidenceColor } from "@/services/gemini-analysis.service";
import {
  Gem,
  Tag,
  Sparkles,
  Palette,
  Wrench,
  Eye,
  FileText,
  Shield,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Hash,
  Cpu,
  Brain,
  Target,
  Search,
  Star,
  Award,
  Layers,
  Box,
  ImageIcon,
} from "lucide-react";

// ─── Animation Variants ────────────────────────────────────

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const } },
};

// ─── Field Card ────────────────────────────────────────────

function FieldCard({ icon: Icon, label, value, color = "#3B82F6" }: {
  icon: React.ElementType;
  label: string;
  value: string | string[] | number | null | undefined;
  color?: string;
}) {
  const displayValue = Array.isArray(value)
    ? value.length > 0 ? value.join(", ") : "Not detected"
    : value ?? "Not available";

  return (
    <motion.div
      variants={itemVariants}
      className="group relative overflow-hidden rounded-2xl p-5 bg-gradient-to-br from-white/[0.02] to-transparent border border-white/[0.06] hover:border-white/[0.10] transition-all duration-300"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      <div className="flex items-start gap-4 relative z-10">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl neumorphic" style={{ color }}>
          <Icon size={17} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>
            {label}
          </p>
          <p className="mt-1 text-sm font-medium leading-relaxed" style={{ color: "var(--theme-text)" }}>
            {String(displayValue)}
          </p>
        </div>
      </div>
    </motion.div>
  );
}

// ─── Confidence Badge ──────────────────────────────────────

function ConfidenceBadge({ score }: { score: number }) {
  const color = getConfidenceColor(score);
  return (
    <div
      className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-semibold border"
      style={{ backgroundColor: `${color}15`, borderColor: `${color}30`, color }}
    >
      <Target size={12} />
      Confidence: {formatConfidence(score)}
    </div>
  );
}

// ─── Section Header ────────────────────────────────────────

function SectionHeader({ icon: Icon, title, subtitle }: {
  icon: React.ElementType;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="flex items-center gap-3 mb-6">
      <div className="flex h-8 w-8 items-center justify-center rounded-xl neumorphic">
        <Icon size={15} className="text-[#3B82F6]" />
      </div>
      <div>
        <h3 className="text-base font-semibold tracking-tight" style={{ color: "var(--theme-text)" }}>{title}</h3>
        {subtitle && <p className="text-xs mt-0.5" style={{ color: "var(--theme-text-secondary)" }}>{subtitle}</p>}
      </div>
    </div>
  );
}

// ─── Jewellery Analysis Display ────────────────────────────

function JewelleryDisplay({ data }: { data: JewelleryAnalysisResult }) {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-3 mb-2">
        <div className="inline-flex items-center gap-2 rounded-full bg-[#3B82F6]/10 border border-[#3B82F6]/20 px-4 py-1.5">
          <Gem size={14} className="text-[#3B82F6]" />
          <span className="text-xs font-semibold text-[#3B82F6]">{getCategoryLabel(data.category)}</span>
        </div>
        <ConfidenceBadge score={data.confidenceScore} />
        <div className="inline-flex items-center gap-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 px-3 py-1">
          <Star size={11} className="text-purple-400" />
          <span className="text-[10px] font-semibold text-purple-400">{data.estimatedQuality}</span>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FieldCard icon={Box} label="Jewellery Type" value={data.jewelleryType} color="#3B82F6" />
        <FieldCard icon={Layers} label="Metals Detected" value={data.metalDetection} color="#F59E0B" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FieldCard icon={Gem} label="Gemstones Detected" value={data.gemstoneDetection} color="#EC4899" />
        <FieldCard icon={Award} label="Craftsmanship" value={data.craftsmanship} color="#22C55E" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FieldCard icon={Palette} label="Design Style" value={data.designStyle} color="#8B5CF6" />
        <FieldCard icon={Shield} label="Surface Finish" value={data.surfaceFinish} color="#06B6D4" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FieldCard icon={Search} label="Hallmark Visibility" value={data.hallmarkVisibility} color="#F97316" />
        <FieldCard icon={Wrench} label="Stone Setting" value={data.stoneSetting} color="#10B981" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FieldCard icon={AlertTriangle} label="Visible Damage" value={data.visibleDamage} color="#EF4444" />
        <FieldCard icon={Star} label="Luxury Level" value={data.luxuryLevel} color="#A855F7" />
      </div>

      <motion.div variants={itemVariants} className="relative overflow-hidden rounded-2xl glass-card p-6">
        <SectionHeader icon={Eye} title="Visual Observations" />
        <p className="text-sm leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>
          {data.visualObservations || "No additional observations recorded."}
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="relative overflow-hidden rounded-2xl glass-card p-6 border border-[#3B82F6]/10">
        <SectionHeader icon={Sparkles} title="Recommendations" subtitle="Professional advice for this piece" />
        <p className="text-sm leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>
          {data.recommendations || "No specific recommendations."}
        </p>
      </motion.div>
    </motion.div>
  );
}

// ─── General Analysis Display ──────────────────────────────

function GeneralDisplay({ data }: { data: GeneralAnalysisResult }) {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-3 mb-2">
        <div className="inline-flex items-center gap-2 rounded-full bg-[#3B82F6]/10 border border-[#3B82F6]/20 px-4 py-1.5">
          <ImageIcon size={14} className="text-[#3B82F6]" />
          <span className="text-xs font-semibold text-[#3B82F6]">{getCategoryLabel(data.category)}</span>
        </div>
        <ConfidenceBadge score={data.confidenceScore} />
        {data.estimatedCondition && (
          <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-3 py-1">
            <CheckCircle2 size={11} className="text-emerald-400" />
            <span className="text-[10px] font-semibold text-emerald-400">{data.estimatedCondition}</span>
          </div>
        )}
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FieldCard icon={Box} label="Object Name" value={data.objectName} color="#3B82F6" />
        <FieldCard icon={Tag} label="Brand" value={data.brand || "Not detected"} color="#F59E0B" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FieldCard icon={Layers} label="Primary Material" value={data.primaryMaterial} color="#8B5CF6" />
        <FieldCard icon={Shield} label="Estimated Condition" value={data.estimatedCondition} color="#22C55E" />
      </div>

      <motion.div variants={itemVariants}>
        <FieldCard icon={Search} label="Detected Objects" value={data.detectedObjects} color="#06B6D4" />
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FieldCard icon={Palette} label="Dominant Colors" value={data.color} color="#EC4899" />
        <FieldCard icon={Eye} label="Shape" value={data.shape} color="#10B981" />
      </div>

      <motion.div variants={itemVariants}>
        <FieldCard icon={AlertTriangle} label="Visible Damage" value={data.observations || "None visible"} color="#EF4444" />
      </motion.div>
      <motion.div variants={itemVariants}>
        <FieldCard icon={FileText} label="OCR Text" value={data.textDetected || "No text detected"} color="#F97316" />
      </motion.div>

      <motion.div variants={itemVariants}>
        <FieldCard icon={Target} label="Possible Usage" value={data.usage} color="#A855F7" />
      </motion.div>

      <motion.div variants={itemVariants} className="relative overflow-hidden rounded-2xl glass-card p-6">
        <SectionHeader icon={FileText} title="Description" />
        <p className="text-sm leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>
          {data.description || "No description available."}
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="relative overflow-hidden rounded-2xl glass-card p-6">
        <SectionHeader icon={Eye} title="Observations" />
        <p className="text-sm leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>
          {data.observations || "No observations recorded."}
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="relative overflow-hidden rounded-2xl glass-card p-6 border border-[#3B82F6]/10">
        <SectionHeader icon={Sparkles} title="Recommendations" />
        <p className="text-sm leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>
          {data.recommendations || "No specific recommendations."}
        </p>
      </motion.div>
    </motion.div>
  );
}

// ─── Main Component ────────────────────────────────────────

interface AnalysisResultPanelProps {
  response: AnalysisResponse;
  thumbnailUrl?: string;
}

export default function AnalysisResultPanel({ response }: AnalysisResultPanelProps) {
  const { data, metadata } = response;

  if (!data) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center justify-center py-16 text-center"
      >
        <AlertTriangle size={40} className="text-red-400 mb-4" />
        <h3 className="text-lg font-bold" style={{ color: "var(--theme-text)" }}>Analysis Failed</h3>
        <p className="text-sm mt-2" style={{ color: "var(--theme-text-secondary)" }}>
          {response.error?.message || "An unknown error occurred."}
        </p>
      </motion.div>
    );
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      >
        {isJewelleryAnalysis(data) ? (
          <JewelleryDisplay data={data} />
        ) : (
          <GeneralDisplay data={data} />
        )}
      </motion.div>

      {metadata && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.4 }}
          className="rounded-2xl glass-card p-5"
        >
          <SectionHeader icon={Cpu} title="AI Processing Details" subtitle="Analysis metadata" />
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Clock size={12} style={{ color: "var(--theme-text-secondary)" }} />
                <span className="text-[10px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>Time</span>
              </div>
              <p className="text-sm font-semibold tabular-nums" style={{ color: "var(--theme-text)" }}>
                {(metadata.executionTimeMs / 1000).toFixed(1)}s
              </p>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Brain size={12} style={{ color: "var(--theme-text-secondary)" }} />
                <span className="text-[10px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>Model</span>
              </div>
              <p className="text-sm font-semibold tabular-nums" style={{ color: "var(--theme-text)" }}>
                {metadata.model || "AI model"}
              </p>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Hash size={12} style={{ color: "var(--theme-text-secondary)" }} />
                <span className="text-[10px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>Request ID</span>
              </div>
              <p className="text-sm font-mono font-semibold" style={{ color: "var(--theme-text)" }}>
                {metadata.requestId.length > 16 ? `${metadata.requestId.slice(0, 16)}...` : metadata.requestId}
              </p>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Cpu size={12} style={{ color: "var(--theme-text-secondary)" }} />
                <span className="text-[10px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>Tokens</span>
              </div>
              <p className="text-sm font-semibold tabular-nums" style={{ color: "var(--theme-text)" }}>
                {metadata.promptTokens + metadata.completionTokens}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
