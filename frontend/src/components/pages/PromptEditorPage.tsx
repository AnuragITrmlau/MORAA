"use client";

import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PenLine, Save, RotateCcw, Check, Info,
  Camera, Shirt, Palette, PartyPopper, Repeat, Ruler, ShoppingBag, Smartphone,
  Sparkles, Variable, ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { usePromptEditorStore, type PromptTemplatesMap } from "@/stores/prompt-editor-store";
import {
  DEFAULT_PROMPT_TEMPLATES,
  PROMPT_TEMPLATE_FIELDS,
} from "@/services/prompt-generation.service";
import {
  PROMPT_CATEGORIES,
  PROMPT_CATEGORY_LABELS,
  PROMPT_CATEGORY_DESCRIPTIONS,
  type PromptCategory,
} from "@/types/prompts";

// --- Category icons / colors (mirrors PromptGenerationPanel) ---

const CATEGORY_ICONS: Record<PromptCategory, React.ElementType> = {
  professionalShot: Camera,
  useCaseShot: Shirt,
  ingredientStory: Palette,
  festive: PartyPopper,
  transformation: Repeat,
  scaleReference: Ruler,
  complementaryShot: ShoppingBag,
  ugcStyle: Smartphone,
};

const CATEGORY_COLORS: Record<PromptCategory, string> = {
  professionalShot: "#3B82F6",
  useCaseShot: "#F59E0B",
  ingredientStory: "#22C55E",
  festive: "#EC4899",
  transformation: "#A855F7",
  scaleReference: "#06B6D4",
  complementaryShot: "#F97316",
  ugcStyle: "#10B981",
};

const FIELD_HINTS: Record<string, string> = {
  productIdentity: "Product identity (e.g. 18K Gold Diamond Ring)",
  materialProperties: "Metals, finish, setting, hallmarks",
  scaleAndProportion: "Size category, relative scale, proportions",
  designStyle: "Design style / aesthetic direction",
  visualCraftsmanship: "Craftsmanship & visual observations",
  targetDemographic: "Who the product is for",
  psychographics: "Buyer psychology & motivations",
  functionalUtility: "How the product is used",
  lifestyleBranding: "Lifestyle & brand positioning",
  indianFestiveContext: "Indian festive & gifting context",
  marketReadiness: "Confidence score & market readiness",
};

type Drafts = Record<PromptCategory, string>;

function buildInitialDrafts(custom: PromptTemplatesMap): Drafts {
  const drafts = {} as Drafts;
  for (const cat of PROMPT_CATEGORIES) {
    drafts[cat] = custom[cat] ?? DEFAULT_PROMPT_TEMPLATES[cat];
  }
  return drafts;
}


export default function PromptEditorPage() {
  const customTemplates = usePromptEditorStore((s) => s.customTemplates);
  const saveTemplates = usePromptEditorStore((s) => s.saveTemplates);
  const clearTemplates = usePromptEditorStore((s) => s.clearTemplates);
  const hydrate = usePromptEditorStore((s) => s.hydrate);

  const [mounted, setMounted] = useState(false);
  const [drafts, setDrafts] = useState<Drafts>(() =>
    buildInitialDrafts(usePromptEditorStore.getState().customTemplates)
  );
  const [saveFlash, setSaveFlash] = useState(false);
  const [restoreFlash, setRestoreFlash] = useState(false);
  const [showVariables, setShowVariables] = useState(true);

  useEffect(() => {
    setMounted(true);
    hydrate();
    // Keep drafts in sync if the store was hydrated/changed before mount
    setDrafts(buildInitialDrafts(usePromptEditorStore.getState().customTemplates));
  }, [hydrate]);

  const customizedCount = useMemo(
    () =>
      PROMPT_CATEGORIES.filter(
        (cat) => drafts[cat] !== DEFAULT_PROMPT_TEMPLATES[cat]
      ).length,
    [drafts]
  );

  const hasUnsavedChanges = useMemo(
    () =>
      PROMPT_CATEGORIES.some(
        (cat) =>
          drafts[cat] !==
          (customTemplates[cat] ?? DEFAULT_PROMPT_TEMPLATES[cat])
      ),
    [drafts, customTemplates]
  );

  const updateDraft = (cat: PromptCategory, value: string) => {
    setDrafts((prev) => ({ ...prev, [cat]: value }));
  };

  const handleSave = () => {
    const next: PromptTemplatesMap = {};
    for (const cat of PROMPT_CATEGORIES) {
      // Only categories the user actually changed are stored; anything
      // identical to the built-in default keeps using the original
      // generator (byte-identical behavior).
      if (drafts[cat] !== DEFAULT_PROMPT_TEMPLATES[cat]) {
        next[cat] = drafts[cat];
      }
    }
    saveTemplates(next);
    setSaveFlash(true);
    window.setTimeout(() => setSaveFlash(false), 2200);
  };

  const handleRestoreDefaults = () => {
    clearTemplates();
    setDrafts(buildInitialDrafts({}));
    setRestoreFlash(true);
    window.setTimeout(() => setRestoreFlash(false), 2200);
  };

  return (
    <div className="max-w-6xl">
      {/* Breadcrumb */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.3 }}
        className="flex items-center gap-2 text-xs mb-8"
        style={{ color: "var(--theme-text-secondary)" }}
      >
        <span style={{ opacity: 0.6 }}>Dashboard</span>
        <ChevronRight size={10} style={{ opacity: 0.3 }} />
        <span className="font-semibold" style={{ color: "var(--theme-text)" }}>
          Prompt Editor
        </span>
      </motion.div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="mb-8"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-[#3B82F6] to-[#2563EB] shadow-[0_4px_20px_rgba(59,130,246,0.3)]">
            <PenLine size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>
              Prompt Editor
            </h1>
            <p className="mt-1 text-sm" style={{ color: "var(--theme-text-secondary)" }}>
              Edit the 8 promotional image-generation prompts directly from the UI. Prompts are still generated from your AI analysis — these templates only control how that analysis is worded.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Action bar */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, delay: 0.05 }}
        className="mb-6 flex flex-wrap items-center gap-3 rounded-2xl border p-4"
        style={{ borderColor: "var(--theme-border)", backgroundColor: "var(--theme-glass)" }}
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <Sparkles size={14} className="text-[#3B82F6] shrink-0" />
          <span className="text-xs" style={{ color: "var(--theme-text-secondary)" }}>
            <strong className="font-semibold" style={{ color: "var(--theme-text)" }}>
              {customizedCount} of 8
            </strong>{" "}
            categories customized
          </span>
          {hasUnsavedChanges && (
            <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse" />
              Unsaved changes
            </span>
          )}
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleRestoreDefaults}
            className="flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-semibold border transition-all duration-200 active:scale-95 hover:bg-red-500/10 hover:border-red-500/30 hover:text-red-400"
            style={{ color: "var(--theme-text-secondary)", borderColor: "var(--theme-border)" }}
          >
            <RotateCcw size={13} />
            Restore Defaults
          </button>
          <button
            onClick={handleSave}
            disabled={!hasUnsavedChanges}
            className={cn(
              "flex items-center gap-2 rounded-xl px-5 py-2.5 text-xs font-semibold text-white transition-all duration-200 active:scale-95",
              hasUnsavedChanges
                ? "shadow-[0_8px_24px_rgba(59,130,246,0.3)] hover:shadow-[0_8px_32px_rgba(59,130,246,0.4)]"
                : "opacity-40 cursor-not-allowed"
            )}
            style={{
              background: "linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)",
            }}
          >
            {saveFlash ? <Check size={13} /> : <Save size={13} />}
            {saveFlash ? "Saved" : "Save Changes"}
          </button>
        </div>
      </motion.div>

      {/* Flash confirmation */}
      <AnimatePresence>
        {(saveFlash || restoreFlash) && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mb-5 flex items-center gap-2.5 rounded-xl px-4 py-3 border"
            style={{
              borderColor: saveFlash ? "#22C55E33" : "#3B82F633",
              backgroundColor: saveFlash ? "#22C55E10" : "#3B82F610",
            }}
          >
            {saveFlash ? (
              <Check size={14} className="text-emerald-400" />
            ) : (
              <RotateCcw size={14} className="text-[#3B82F6]" />
            )}
            <span className="text-xs font-medium" style={{ color: "var(--theme-text)" }}>
              {saveFlash
                ? "Prompts saved — new generations will use your custom templates immediately."
                : "Defaults restored — all categories back to built-in templates."}
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Variables helper */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, delay: 0.08 }}
        className="mb-8 rounded-2xl border overflow-hidden"
        style={{ borderColor: "var(--theme-border)", backgroundColor: "var(--theme-glass)" }}
      >
        <button
          onClick={() => setShowVariables((v) => !v)}
          aria-expanded={showVariables}
          className="w-full flex items-center justify-between gap-3 px-5 py-3.5 text-left hover:bg-white/[0.03] transition-colors duration-200"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#3B82F6]/10 border border-[#3B82F6]/15">
              <Variable size={13} className="text-[#3B82F6]" />
            </div>
            <div>
              <h3 className="text-xs font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>
                Template Variables
              </h3>
              <p className="text-[10px] mt-0.5" style={{ color: "var(--theme-text-secondary)", opacity: 0.7 }}>
                Use {"{{field}}"} placeholders — replaced with the analysed product data at generation time
              </p>
            </div>
          </div>
          <motion.span animate={{ rotate: showVariables ? 180 : 0 }} transition={{ duration: 0.25 }} style={{ color: "var(--theme-text-secondary)" }}>
            <ChevronRight size={13} className="rotate-90" />
          </motion.span>
        </button>
        <AnimatePresence initial={false}>
          {showVariables && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
              className="overflow-hidden"
            >
              <div className="px-5 pb-5 pt-1 border-t grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2" style={{ borderColor: "var(--theme-border)" }}>
                {PROMPT_TEMPLATE_FIELDS.map((field) => (
                  <div
                    key={field}
                    className="flex items-start gap-2.5 rounded-xl px-3 py-2 border"
                    style={{ borderColor: "var(--theme-border-light)", backgroundColor: "var(--theme-muted)" }}
                  >
                    <code className="text-[10px] font-mono font-semibold shrink-0 px-1.5 py-0.5 rounded-md bg-[#3B82F6]/10 text-[#3B82F6]">
                      {"{{"}{field}{"}}"}
                    </code>
                    <span className="text-[10px] leading-snug" style={{ color: "var(--theme-text-secondary)", opacity: 0.8 }}>
                      {FIELD_HINTS[field]}
                    </span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Editor cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {PROMPT_CATEGORIES.map((category, index) => {
          const Icon = CATEGORY_ICONS[category];
          const color = CATEGORY_COLORS[category];
          const label = PROMPT_CATEGORY_LABELS[category];
          const description = PROMPT_CATEGORY_DESCRIPTIONS[category];
          const isCustomized = drafts[category] !== DEFAULT_PROMPT_TEMPLATES[category];

          return (
            <motion.div
              key={category}
              initial={{ opacity: 0, y: 20 }}
              animate={mounted ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.45, delay: 0.1 + index * 0.05, ease: [0.16, 1, 0.3, 1] }}
              className="group relative overflow-hidden rounded-2xl border transition-all duration-300 hover:shadow-lg"
              style={{ borderColor: "var(--theme-border)", backgroundColor: "var(--theme-glass)" }}
            >
              {/* Top edge color accent */}
              <div
                className="absolute top-0 left-0 right-0 h-[2px] opacity-60"
                style={{ background: `linear-gradient(90deg, ${color}, transparent)` }}
              />

              <div className="p-5">
                {/* Header */}
                <div className="flex items-start justify-between gap-3 mb-4">
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className="flex h-9 w-9 items-center justify-center rounded-xl shrink-0"
                      style={{ backgroundColor: `${color}15`, color }}
                    >
                      <Icon size={16} />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold opacity-40" style={{ color: "var(--theme-text)" }}>
                          {String(index + 1).padStart(2, "0")}
                        </span>
                        <h4 className="text-sm font-bold truncate" style={{ color: "var(--theme-text)" }}>
                          {label}
                        </h4>
                      </div>
                      <p className="text-[10px] mt-0.5 leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>
                        {description}
                      </p>
                    </div>
                  </div>
                  <AnimatePresence>
                    {isCustomized && (
                      <motion.span
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        className="shrink-0 text-[9px] font-bold uppercase tracking-[0.1em] px-2 py-1 rounded-full border"
                        style={{ color, borderColor: `${color}30`, backgroundColor: `${color}10` }}
                      >
                        Custom
                      </motion.span>
                    )}
                  </AnimatePresence>
                </div>

                {/* Textarea */}
                <textarea
                  value={drafts[category]}
                  onChange={(e) => updateDraft(category, e.target.value)}
                  spellCheck={false}
                  className="w-full rounded-xl p-4 text-[12px] leading-relaxed font-mono outline-none resize-y transition-all duration-200 min-h-[190px] border focus:border-[#3B82F6]/30"
                  style={{
                    backgroundColor: "var(--theme-muted)",
                    borderColor: "var(--theme-border)",
                    color: "var(--theme-text)",
                  }}
                  aria-label={`${label} prompt template`}
                />

                {/* Footer */}
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-[10px] tabular-nums" style={{ color: "var(--theme-text-secondary)", opacity: 0.5 }}>
                    {drafts[category].length.toLocaleString()} chars
                  </span>
                  <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--theme-text-secondary)", opacity: 0.6 }}>
                    <Info size={10} />
                    Applied on save
                  </span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
