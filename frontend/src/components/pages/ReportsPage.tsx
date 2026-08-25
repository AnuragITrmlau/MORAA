"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { FileText, ChevronRight, Download, Eye, FileSpreadsheet, Loader2, AlertTriangle, WifiOff } from "lucide-react";

interface ReportItem {
  id: string;
  name: string;
  type: string;
  date: string;
  pages: number;
  size: string;
  url?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ReportsPage() {
  const [mounted, setMounted] = useState(false);
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

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

  const fetchReports = useCallback(async () => {
    if (!backendOnline) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/reports`);
      if (!res.ok) throw new Error("Failed to fetch reports");
      const data = await res.json();
      const items = Array.isArray(data) ? data : data.items || data.reports || [];
      setReports(items.map((r: any) => ({
        id: r.id,
        name: r.filename || r.name || "Report",
        type: r.type || "Analysis",
        date: r.generatedAt || r.date || new Date().toISOString(),
        pages: r.pages || 1,
        size: r.size ? `${(r.size / 1024).toFixed(1)} KB` : "—",
        url: r.url || `${API_BASE_URL}/api/reports/download/${r.id}`,
      })));
    } catch (err: any) {
      setError(err.message || "Failed to load reports");
    } finally {
      setLoading(false);
    }
  }, [backendOnline]);

  useEffect(() => {
    if (mounted) fetchReports();
  }, [mounted, fetchReports]);

  return (
    <div className="max-w-4xl">
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
        <span className="font-semibold" style={{ color: "var(--theme-text)" }}>Reports</span>
      </motion.div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="mb-10"
      >
        <h1 className="text-3xl font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>Reports</h1>
        <p className="mt-2 text-sm" style={{ color: "var(--theme-text-secondary)" }}>View and download generated analysis reports.</p>
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
            <p className="text-xs text-amber-400/70 mt-0.5">Start the backend server to view and download reports.</p>
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
          <button onClick={() => setError(null)} className="text-xs text-red-400/60 hover:text-red-400">Dismiss</button>
        </motion.div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="rounded-2xl glass-card p-5">
              <div className="flex items-center gap-4">
                <div className="skeleton h-11 w-11 rounded-xl" />
                <div className="flex-1 space-y-2">
                  <div className="skeleton h-4 w-48" />
                  <div className="skeleton h-3 w-32" />
                </div>
                <div className="skeleton h-8 w-24 rounded-xl" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && reports.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={mounted ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="flex flex-col items-center justify-center py-24 text-center rounded-2xl glass-card"
        >
          <div className="flex h-18 w-18 items-center justify-center rounded-2xl ring-1 mb-5 neumorphic" style={{ backgroundColor: "var(--theme-neumorphic)", borderColor: "var(--theme-border-light)" }}>
            <FileText size={32} style={{ color: "var(--theme-text-secondary)", opacity: 0.5 }} />
          </div>
          <h3 className="text-lg font-semibold" style={{ color: "var(--theme-text)" }}>No reports yet</h3>
          <p className="text-sm mt-2 max-w-sm leading-relaxed" style={{ color: "var(--theme-text-secondary)" }}>
            Run an analysis first, then generate a report from the results.
          </p>
        </motion.div>
      )}

      {/* Report list */}
      {!loading && reports.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={mounted ? { opacity: 1 } : {}}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="space-y-4"
        >
          {reports.map((report, i) => (
            <motion.div
              key={report.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className="flex items-center justify-between rounded-2xl glass-card p-5 group"
            >
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl neumorphic shrink-0">
                  <FileSpreadsheet size={20} className="text-[#3B82F6]" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold truncate" style={{ color: "var(--theme-text)" }}>{report.name}</p>
                  <p className="text-xs mt-0.5" style={{ color: "var(--theme-text-secondary)" }}>
                    {report.type} · {report.pages} pages · {report.size}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <span className="text-xs hidden sm:block" style={{ color: "var(--theme-text-secondary)" }}>
                  {report.date ? new Date(report.date).toLocaleDateString() : ""}
                </span>
                {report.url && (
                  <>
                    <a
                      href={report.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 rounded-xl btn-secondary px-3.5 py-2 text-xs font-semibold"
                    >
                      <Eye size={14} />
                      <span className="hidden sm:inline">View</span>
                    </a>
                    <a
                      href={report.url}
                      download
                      className="btn-primary flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-semibold"
                    >
                      <Download size={14} />
                      <span className="hidden sm:inline">PDF</span>
                    </a>
                  </>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
