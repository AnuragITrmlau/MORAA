"use client";

import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface TrendItem {
  keyword: string;
  growth: number;
  volume: number;
  sentiment: "positive" | "negative" | "neutral";
}

interface TrendAlertProps {
  trends?: TrendItem[];
  className?: string;
}

const defaultTrends: TrendItem[] = [
  { keyword: "gold necklace", growth: 24.5, volume: 85000, sentiment: "positive" },
  { keyword: "victorian jewelry", growth: 18.2, volume: 42000, sentiment: "positive" },
  { keyword: "diamond pendant", growth: -5.3, volume: 38000, sentiment: "neutral" },
  { keyword: "vintage gold", growth: 32.7, volume: 28000, sentiment: "positive" },
];

export default function TrendAlert({ trends = defaultTrends, className }: TrendAlertProps) {
  return (
    <div className={cn("rounded-2xl glass-card overflow-hidden", className)}>
      <div className="border-b border-white/[0.04] px-5 py-4">
        <h3 className="text-sm font-semibold tracking-tight" style={{ color: "var(--theme-text)" }}>Trend Alert</h3>
      </div>
      <div className="divide-y divide-white/[0.04]">
        {trends.map((trend, i) => (
          <div key={i} className="flex items-center justify-between px-5 py-3 group hover:bg-white/[0.01] transition-all duration-200">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate capitalize group-hover:text-white transition-colors" style={{ color: "var(--theme-text)" }}>{trend.keyword}</p>
              <p className="text-xs mt-0.5" style={{ color: "var(--theme-text-secondary)" }}>{trend.volume.toLocaleString()} searches</p>
            </div>
            <div className={cn(
              "flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold transition-all duration-200",
              trend.growth > 0
                ? "bg-green-500/10 text-green-400"
                : trend.growth < 0
                ? "bg-red-500/10 text-red-400"
                : "bg-white/5 text-white/40"
            )}>
              {trend.growth > 0 ? (
                <TrendingUp size={12} />
              ) : trend.growth < 0 ? (
                <TrendingDown size={12} />
              ) : (
                <Minus size={12} />
              )}
              <span>{trend.growth >= 0 ? "+" : ""}{trend.growth}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
