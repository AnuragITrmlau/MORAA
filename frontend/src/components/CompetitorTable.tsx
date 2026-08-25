"use client";

import { cn } from "@/lib/utils";
import { ExternalLink, Star } from "lucide-react";

interface Competitor {
  id: string;
  name: string;
  platform: string;
  price: number;
  sellerRating: number;
  salesCount: number;
  material: string;
  goldPurity: string;
}

interface CompetitorTableProps {
  competitors?: Competitor[];
  className?: string;
}

const defaultCompetitors: Competitor[] = [
  { id: "c1", name: "Victorian Gold Diamond Necklace", platform: "Etsy", price: 3200, sellerRating: 4.8, salesCount: 127, material: "18K Yellow Gold", goldPurity: "18K" },
  { id: "c2", name: "Antique Style Gold Pendant", platform: "Amazon", price: 2450, sellerRating: 4.5, salesCount: 89, material: "14K Yellow Gold", goldPurity: "14K" },
  { id: "c3", name: "Handcrafted Gold Necklace", platform: "eBay", price: 1890, sellerRating: 4.3, salesCount: 210, material: "18K Rose Gold", goldPurity: "18K" },
  { id: "c4", name: "Luxury Diamond Gold Necklace", platform: "1stdibs", price: 5600, sellerRating: 4.9, salesCount: 45, material: "18K White Gold", goldPurity: "18K" },
  { id: "c5", name: "Vintage Gold Chain Necklace", platform: "Poshmark", price: 1100, sellerRating: 4.2, salesCount: 310, material: "10K Yellow Gold", goldPurity: "10K" },
];

function getMatchLevel(price: number, basePrice: number = 2850): { label: string; color: string; bg: string } {
  const diff = ((price - basePrice) / basePrice) * 100;
  if (Math.abs(diff) <= 10) return { label: "High", color: "text-emerald-400", bg: "bg-emerald-500/10" };
  if (Math.abs(diff) <= 25) return { label: "Medium", color: "text-amber-400", bg: "bg-amber-500/10" };
  return { label: "Low", color: "text-red-400", bg: "bg-red-500/10" };
}

function getStatus(salesCount: number): { label: string; color: string; bg: string } {
  if (salesCount > 150) return { label: "Trending", color: "text-emerald-400", bg: "bg-emerald-500/10" };
  if (salesCount > 75) return { label: "Active", color: "text-blue-400", bg: "bg-blue-500/10" };
  return { label: "Low Vol.", color: "text-white/40", bg: "bg-white/5" };
}

export default function CompetitorTable({ competitors = defaultCompetitors, className }: CompetitorTableProps) {
  return (
    <div className={cn("rounded-2xl glass-card overflow-hidden", className)}>
      <div className="border-b border-white/[0.04] px-6 py-5">
        <h3 className="text-base font-semibold tracking-tight" style={{ color: "var(--theme-text)" }}>Competitor Pricing</h3>
        <p className="mt-1 text-xs" style={{ color: "var(--theme-text-secondary)" }}>Similar products across marketplaces</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/[0.04] bg-white/[0.01]">
              <th className="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>Competitor</th>
              <th className="px-4 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>Similar Product</th>
              <th className="px-4 py-4 text-right text-[11px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>Price Point</th>
              <th className="px-4 py-4 text-center text-[11px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>Match</th>
              <th className="px-4 py-4 text-center text-[11px] font-semibold uppercase tracking-[0.1em]" style={{ color: "var(--theme-text-secondary)" }}>Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {competitors.map((comp) => {
              const match = getMatchLevel(comp.price);
              const status = getStatus(comp.salesCount);
              return (
                <tr key={comp.id} className="group hover:bg-white/[0.02] transition-all duration-200 cursor-pointer">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2.5">
                      <span className="text-sm font-semibold group-hover:text-white transition-colors duration-200" style={{ color: "var(--theme-text)" }}>{comp.platform}</span>
                      <ExternalLink size={12} className="text-white/20" />
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <p className="text-sm truncate max-w-[200px] group-hover:text-white/70 transition-colors duration-200" style={{ color: "var(--theme-text-secondary)" }}>{comp.name}</p>
                    <p className="text-xs mt-0.5" style={{ color: "var(--theme-text-secondary)", opacity: 0.5 }}>{comp.material}</p>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <span className="text-sm font-bold" style={{ color: "var(--theme-text)" }}>${comp.price.toLocaleString()}</span>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex justify-center">
                      <span className={cn("rounded-full px-3 py-1 text-[11px] font-semibold", match.bg, match.color)}>
                        {match.label}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex justify-center">
                      <span className={cn("rounded-full px-3 py-1 text-[11px] font-semibold", status.bg, status.color)}>
                        {status.label}
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
