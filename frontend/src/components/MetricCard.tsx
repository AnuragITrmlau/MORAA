"use client";

import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: { value: number; positive: boolean };
  icon?: React.ReactNode;
  className?: string;
  loading?: boolean;
}

export default function MetricCard({ title, value, subtitle, trend, icon, className, loading }: MetricCardProps) {
  if (loading) {
    return (
      <div className={cn("rounded-2xl glass-card p-6", className)}>
        <div className="space-y-3">
          <div className="skeleton h-3 w-24" />
          <div className="skeleton h-8 w-20" />
          <div className="skeleton h-3 w-16" />
        </div>
      </div>
    );
  }

  return (
    <div className={cn("rounded-2xl glass-card p-6 group", className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>{title}</p>
          <p className="mt-2 text-3xl font-bold truncate tracking-tight" style={{ color: "var(--theme-text)" }}>{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs" style={{ color: "var(--theme-text-secondary)" }}>{subtitle}</p>
          )}
          {trend && (
            <div className="mt-3 flex items-center gap-1.5">
              {trend.positive ? (
                <TrendingUp size={15} className="text-green-400" />
              ) : (
                <TrendingDown size={15} className="text-red-400" />
              )}
              <span className={cn(
                "text-xs font-semibold",
                trend.positive ? "text-green-400" : "text-red-400"
              )}>
                {trend.positive ? "+" : ""}{trend.value}% vs last month
              </span>
            </div>
          )}
        </div>
        {icon && (
          <div className="flex-shrink-0 ml-4 flex h-11 w-11 items-center justify-center rounded-xl neumorphic text-[#3B82F6] transition-all duration-300 group-hover:scale-110 group-hover:shadow-[0_0_16px_rgba(59,130,246,0.15)]">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
