"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { getHistory, deleteHistoryItem } from "@/services/history.service";
import { useUIStore } from "@/stores/ui-store";
import type { HistoryItem } from "@/types";
import {
  Search,
  ChevronRight,
  Gem,
  CheckCircle2,
  XCircle,
  Loader2,
  SlidersHorizontal,
  Trash2,
  Eye,
  WifiOff,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/utils";

const statusConfig = {
  completed: { icon: CheckCircle2, label: "Completed", color: "text-emerald-400", bg: "bg-emerald-500/10" },
  processing: { icon: Loader2, label: "Processing", color: "text-amber-400", bg: "bg-amber-500/10" },
  failed: { icon: XCircle, label: "Failed", color: "text-red-400", bg: "bg-red-500/10" },
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HistoryPage() {
  const [mounted, setMounted] = useState(false);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<string>("all");
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    setMounted(true);
  }, []);

  // Check backend health
  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(3000) });
        if (!cancelled) setBackendOnline(res.ok);
      } catch {
        if (!cancelled) setBackendOnline(false);
      }
    };
    check();
    return () => { cancelled = true; };
  }, []);

  const fetchHistory = useCallback(async () => {
    if (!backendOnline) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await getHistory();
      setItems(data);
    } catch (err: any) {
      setError(err.message || "Failed to load history");
    } finally {
      setLoading(false);
    }
  }, [backendOnline]);

  useEffect(() => {
    if (mounted) fetchHistory();
  }, [mounted, fetchHistory]);

  const handleDelete = useCallback(async (id: string) => {
    setDeletingIds((prev) => new Set(prev).add(id));
    try {
      await deleteHistoryItem(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err: any) {
      setError(err.message || "Failed to delete item");
    } finally {
      setDeletingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }, []);

  const handleView = useCallback((item: HistoryItem) => {
    // Navigate back to dashboard to view results
    useUIStore.getState().setCurrentPage("dashboard");
  }, []);

  const filtered = items.filter((item) => {
    const matchesSearch = item.productName?.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === "all" || item.status === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="max-w-5xl">
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
        <span className="font-semibold" style={{ color: "var(--theme-text)" }}>History</span>
      </motion.div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>Analysis History</h1>
        <p className="mt-2 text-sm" style={{ color: "var(--theme-text-secondary)" }}>View and manage your previous jewellery analyses.</p>
      </motion.div>

      {/* Backend offline */}
      {!backendOnline && mounted && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 flex items-center gap-3 rounded-2xl border border-amber-500/20 bg-amber-500/8 px-5 py-3"
        >
          <WifiOff size={18} className="text-amber-400 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-amber-400">Backend Offline</p>
            <p className="text-xs text-amber-400/70 mt-0.5">Start the backend server to view analysis history.</p>
          </div>
        </motion.div>
      )}

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 flex items-center gap-3 rounded-2xl border border-red-500/20 bg-red-500/8 px-5 py-3"
        >
          <AlertTriangle size={18} className="text-red-400 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-red-400">Error</p>
            <p className="text-xs text-red-400/70 mt-0.5">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-xs text-red-400/60 hover:text-red-400 transition-colors"
          >
            Dismiss
          </button>
        </motion.div>
      )}

      {/* Search + Filters */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, delay: 0.05, ease: [0.16, 1, 0.3, 1] }}
        className="flex items-center gap-4 mb-8 flex-wrap"
      >
        <div className="relative flex-1 max-w-sm group">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 z-10 transition-colors duration-300" style={{ color: "var(--theme-text-secondary)" }} />
          <input
            type="text"
            placeholder="Search analyses..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full h-10 pl-10 pr-4 rounded-2xl border text-sm outline-none transition-all duration-300 focus:border-[#3B82F6]/30"
            style={{
              backgroundColor: "var(--theme-neumorphic)",
              borderColor: "var(--theme-border-light)",
              color: "var(--theme-text)",
            }}
          />
        </div>
        <div className="flex items-center gap-2">
          <SlidersHorizontal size={14} style={{ color: "var(--theme-text-secondary)", opacity: 0.5 }} />
          {["all", "completed", "processing", "failed"].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={cn(
                "rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all duration-200",
                filter === s
                  ? "bg-[#3B82F6] text-white shadow-[0_4px_16px_rgba(59,130,246,0.35)]"
                  : "border text-white/40 hover:text-white/70"
              )}
              style={{
                backgroundColor: filter === s ? undefined : "var(--theme-neumorphic)",
                borderColor: filter === s ? undefined : "var(--theme-border-light)",
              }}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </motion.div>

      {/* History List */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={mounted ? { opacity: 1 } : {}}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="space-y-4"
      >
        {/* Loading skeleton */}
        {loading && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="rounded-2xl glass-card p-5">
                <div className="flex items-center gap-4">
                  <div className="skeleton h-11 w-11 rounded-xl" />
                  <div className="flex-1 space-y-2">
                    <div className="skeleton h-4 w-40" />
                    <div className="skeleton h-3 w-24" />
                  </div>
                  <div className="skeleton h-6 w-20 rounded-full" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && filtered.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center rounded-2xl glass-card">
            <div className="relative mb-5">
              <div className="absolute -inset-5 bg-[#3B82F6] opacity-[0.04] blur-2xl rounded-full" />
              <Gem size={48} style={{ color: "var(--theme-text-secondary)", opacity: 0.3 }} />
            </div>
            <p className="text-base font-semibold" style={{ color: "var(--theme-text-secondary)" }}>
              {search || filter !== "all" ? "No matching analyses found" : "No analyses yet"}
            </p>
            <p className="text-sm mt-1.5" style={{ color: "var(--theme-text-secondary)", opacity: 0.6 }}>
              {search || filter !== "all" ? "Try a different search term or filter." : "Upload a jewellery image to get started."}
            </p>
          </div>
        )}

        {/* Items */}
        {!loading &&
          filtered.map((item, i) => {
            const StatusIcon = statusConfig[item.status].icon;
            const statusStyle = statusConfig[item.status];
            const isDeleting = deletingIds.has(item.id);
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: i * 0.04 }}
                className="flex items-center justify-between rounded-2xl glass-card p-5 group"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  {/* Thumbnail */}
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl neumorphic overflow-hidden shrink-0">
                    {item.imageUrl ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={item.imageUrl} alt="" className="h-full w-full object-cover" />
                    ) : (
                      <Gem size={20} className="transition-colors duration-300" style={{ color: "var(--theme-text-secondary)" }} />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold truncate" style={{ color: "var(--theme-text)" }}>
                      {item.productName || "Unnamed Product"}
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: "var(--theme-text-secondary)" }}>
                      {item.estimatedPrice ? `$${item.estimatedPrice.toLocaleString()} · ` : ""}
                      {item.analysisDate ? formatDate(item.analysisDate) : ""}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  {/* Status badge */}
                  <span className={cn("hidden sm:inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[11px] font-semibold", statusStyle.bg, statusStyle.color)}>
                    <StatusIcon size={12} className={cn(item.status === "processing" && "animate-spin")} />
                    {statusStyle.label}
                  </span>

                  {/* View button */}
                  <button
                    onClick={() => handleView(item)}
                    className="rounded-xl p-2 transition-all duration-200"
                    style={{ color: "var(--theme-text-secondary)" }}
                    title="View analysis"
                    aria-label="View analysis"
                  >
                    <Eye size={15} className="hover:text-[#3B82F6] transition-colors" />
                  </button>

                  {/* Delete button */}
                  <button
                    onClick={() => handleDelete(item.id)}
                    disabled={isDeleting}
                    className="rounded-xl p-2 transition-all duration-200"
                    style={{ color: "var(--theme-text-secondary)" }}
                    title="Delete analysis"
                    aria-label="Delete analysis"
                  >
                    {isDeleting ? (
                      <Loader2 size={15} className="animate-spin text-red-400" />
                    ) : (
                      <Trash2 size={15} className="hover:text-red-400 transition-colors" />
                    )}
                  </button>
                </div>
              </motion.div>
            );
          })}
      </motion.div>
    </div>
  );
}
