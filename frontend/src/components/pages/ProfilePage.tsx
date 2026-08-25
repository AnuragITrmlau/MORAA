"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ChevronRight, Gem, Calendar, Activity, FileText, Star, Mail, Loader2 } from "lucide-react";
import { getHistoryStats } from "@/services/history.service";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ProfilePage() {
  const [mounted, setMounted] = useState(false);
  const [stats, setStats] = useState({ total: 0, thisMonth: 0, averagePrice: 0 });
  const [loading, setLoading] = useState(true);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const healthRes = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(3000) });
        if (!cancelled) {
          const online = healthRes.ok;
          setBackendOnline(online);
          if (online) {
            try {
              const s = await getHistoryStats();
              if (!cancelled) setStats(s);
            } catch {
              // stats not available yet
            }
          }
        }
      } catch {
        if (!cancelled) setBackendOnline(false);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, []);

  const activityStats = [
    { label: "Total Analyses", value: stats.total.toString(), icon: FileText },
    { label: "This Month", value: stats.thisMonth.toString(), icon: Activity },
    { label: "Avg. Price", value: stats.averagePrice ? `$${stats.averagePrice.toLocaleString()}` : "$0", icon: Star },
    { label: "Reports Generated", value: "0", icon: Gem },
  ];

  return (
    <div className="max-w-4xl">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.3 }}
        className="flex items-center gap-2 text-xs mb-8"
        style={{ color: "var(--theme-text-secondary)" }}
      >
        <span style={{ opacity: 0.6 }}>Dashboard</span>
        <ChevronRight size={10} style={{ opacity: 0.3 }} />
        <span className="font-semibold" style={{ color: "var(--theme-text)" }}>Profile</span>
      </motion.div>

      {/* Profile Card */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="rounded-2xl glass-card-deep p-8 mb-8"
      >
        <div className="flex items-center gap-6">
          <div className="relative">
            <div className="absolute -inset-3 bg-[#3B82F6] opacity-[0.10] blur-2xl rounded-full" />
            <div className="relative flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-[#3B82F6] to-[#2563EB] shadow-[0_8px_32px_rgba(59,130,246,0.3)] shrink-0">
              <span className="text-3xl font-bold text-white">A</span>
            </div>
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>Administrator</h2>
            <p className="text-sm mt-1" style={{ color: "var(--theme-text-secondary)" }}>System Administrator</p>
            <div className="flex items-center gap-5 mt-3">
              <div className="flex items-center gap-1.5 text-xs" style={{ color: "var(--theme-text-secondary)" }}>
                <Mail size={13} />
                <span>admin@moraagemvision.com</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs" style={{ color: "var(--theme-text-secondary)" }}>
                <Calendar size={13} />
                <span>Joined today</span>
              </div>
            </div>
          </div>
          <button className="btn-primary rounded-2xl px-6 py-2.5 text-sm font-semibold shadow-[0_4px_16px_rgba(59,130,246,0.25)]">
            Edit Profile
          </button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={mounted ? { opacity: 1 } : {}}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8"
      >
        {activityStats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 + i * 0.05 }}
              className="rounded-2xl glass-card p-5"
            >
              <div className="flex items-center justify-center w-9 h-9 rounded-xl neumorphic mb-4">
                <Icon size={16} className="text-[#3B82F6]" />
              </div>
              {loading ? (
                <div className="space-y-2">
                  <div className="skeleton h-8 w-16" />
                  <div className="skeleton h-3 w-20" />
                </div>
              ) : (
                <>
                  <p className="text-3xl font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>{stat.value}</p>
                  <p className="text-xs mt-1 font-medium" style={{ color: "var(--theme-text-secondary)" }}>{stat.label}</p>
                </>
              )}
            </motion.div>
          );
        })}
      </motion.div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, delay: 0.2 }}
        className="rounded-2xl glass-card p-6"
      >
        <div className="flex items-center gap-3 mb-5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg neumorphic">
            <Activity size={14} className="text-[#3B82F6]" />
          </div>
          <h3 className="text-base font-semibold tracking-tight" style={{ color: "var(--theme-text)" }}>Recent Activity</h3>
        </div>
        <div className="flex flex-col items-center py-12 text-center">
          <div className="relative mb-4">
            <div className="absolute -inset-4 bg-[#3B82F6] opacity-[0.03] blur-2xl rounded-full" />
            <Activity size={32} className="relative" style={{ color: "var(--theme-text-secondary)", opacity: 0.3 }} />
          </div>
          <p className="text-sm font-medium" style={{ color: "var(--theme-text-secondary)" }}>No recent activity</p>
          <p className="text-xs mt-1.5 max-w-xs leading-relaxed" style={{ color: "var(--theme-text-secondary)", opacity: 0.6 }}>
            Your activity will appear here after your first jewellery analysis.
          </p>
        </div>
      </motion.div>
    </div>
  );
}
