"use client";

import { cn } from "@/lib/utils";
import { AlertTriangle, ShieldCheck, AlertCircle } from "lucide-react";

interface RiskItem {
  category: string;
  risk: "low" | "medium" | "high";
  score: number;
  description: string;
}

interface RiskAssessmentProps {
  risks?: RiskItem[];
  className?: string;
}

const defaultRisks: RiskItem[] = [
  { category: "Price Volatility", risk: "medium", score: 45, description: "Moderate fluctuations affect valuation" },
  { category: "Market Saturation", risk: "low", score: 25, description: "Manageable competition levels" },
  { category: "Counterfeit Risk", risk: "high", score: 72, description: "Premium segment concerns" },
  { category: "Supply Chain", risk: "low", score: 18, description: "Stable supplier network" },
];

const riskConfig = {
  low: { color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-400/20", icon: ShieldCheck, label: "Low" },
  medium: { color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-400/20", icon: AlertTriangle, label: "Medium" },
  high: { color: "text-red-400", bg: "bg-red-500/10", border: "border-red-400/20", icon: AlertCircle, label: "High" },
};

export default function RiskAssessmentCard({ risks = defaultRisks, className }: RiskAssessmentProps) {
  return (
    <div className={cn("rounded-2xl glass-card overflow-hidden", className)}>
      <div className="border-b border-white/[0.04] px-5 py-4">
        <h3 className="text-sm font-semibold tracking-tight" style={{ color: "var(--theme-text)" }}>Risk Assessment</h3>
      </div>
      <div className="divide-y divide-white/[0.04]">
        {risks.map((item, i) => {
          const config = riskConfig[item.risk];
          const Icon = config.icon;
          return (
            <div key={i} className="px-5 py-4 group hover:bg-white/[0.01] transition-colors duration-200">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2.5">
                  <Icon size={15} className={cn(config.color, "transition-transform duration-200 group-hover:scale-110")} />
                  <span className="text-sm font-medium" style={{ color: "var(--theme-text)" }}>{item.category}</span>
                </div>
                <span className={cn("rounded-full px-2.5 py-0.5 text-[10px] font-semibold", config.bg, config.color)}>
                  {config.label}
                </span>
              </div>
              <p className="text-xs ml-7" style={{ color: "var(--theme-text-secondary)" }}>{item.description}</p>
              <div className="mt-2 ml-7 h-1.5 w-full max-w-[140px] rounded-full bg-white/5 overflow-hidden">
                <div
                  className={cn("h-full rounded-full transition-all duration-700", config.bg)}
                  style={{ width: `${item.score}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
