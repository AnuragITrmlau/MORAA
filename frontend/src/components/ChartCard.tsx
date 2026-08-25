"use client";

import { cn } from "@/lib/utils";

interface PricePoint {
  date: string;
  price: number;
  volume: number;
}

interface ChartCardProps {
  data?: PricePoint[];
  className?: string;
}

const defaultData: PricePoint[] = [
  { date: "Jan", price: 2650, volume: 38 },
  { date: "Feb", price: 2720, volume: 42 },
  { date: "Mar", price: 2680, volume: 40 },
  { date: "Apr", price: 2800, volume: 45 },
  { date: "May", price: 2900, volume: 50 },
  { date: "Jun", price: 2850, volume: 48 },
];

const maxPrice = Math.max(...defaultData.map((d) => d.price));
const minPrice = Math.min(...defaultData.map((d) => d.price));
const range = maxPrice - minPrice || 1;

export default function ChartCard({ data = defaultData, className }: ChartCardProps) {
  const chartHeight = 180;
  const barWidth = 36;

  return (
    <div className={cn("rounded-2xl glass-card overflow-hidden", className)}>
      {/* Header */}
      <div className="border-b border-white/[0.04] px-6 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold tracking-tight" style={{ color: "var(--theme-text)" }}>Price Distribution</h3>
            <p className="mt-1 text-xs" style={{ color: "var(--theme-text-secondary)" }}>Market price trends over the last 6 months</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-[#3B82F6] shadow-[0_0_4px_rgba(59,130,246,0.3)]" />
              <span className="text-xs" style={{ color: "var(--theme-text-secondary)" }}>Avg Price</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-[#3B82F6]/30" />
              <span className="text-xs" style={{ color: "var(--theme-text-secondary)" }}>Volume</span>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Body */}
      <div className="px-6 py-6">
        <div className="flex gap-3">
          {/* Y-axis */}
          <div className="flex flex-col justify-between text-[10px] w-10 py-0" style={{ height: chartHeight, color: "var(--theme-text-secondary)" }}>
            <span>${(maxPrice / 1000).toFixed(1)}K</span>
            <span>${((maxPrice + minPrice) / 2 / 1000).toFixed(1)}K</span>
            <span>${(minPrice / 1000).toFixed(1)}K</span>
          </div>

          {/* Chart area */}
          <div className="flex-1">
            <div className="relative" style={{ height: chartHeight }}>
              {/* Grid lines */}
              <div className="absolute inset-0 flex flex-col justify-between">
                <div className="border-t border-white/[0.03]"></div>
                <div className="border-t border-white/[0.03]"></div>
                <div className="border-t border-white/[0.03]"></div>
              </div>

              {/* Bars */}
              <div className="absolute inset-0 flex items-end justify-between px-1">
                {data.map((point, i) => {
                  const pricePercent = ((point.price - minPrice) / range) * 100;
                  const volPercent = (point.volume / 50) * 100;
                  return (
                    <div key={i} className="flex flex-col items-center gap-1" style={{ width: barWidth }}>
                      <div className="relative w-full flex justify-center gap-1">
                        <div
                          className="w-3 rounded-t-sm bg-gradient-to-t from-[#3B82F6] to-[#60A5FA] transition-all duration-500 shadow-[0_0_8px_rgba(59,130,246,0.2)] hover:shadow-[0_0_16px_rgba(59,130,246,0.4)] hover:scale-y-105 origin-bottom"
                          style={{ height: `${Math.max(pricePercent * 1.2, 4)}px` }}
                          title={`$${point.price}`}
                        ></div>
                        <div
                          className="w-3 rounded-t-sm bg-gradient-to-t from-[#3B82F6]/20 to-[#3B82F6]/40 transition-all duration-500"
                          style={{ height: `${Math.max(volPercent * 0.8, 4)}px` }}
                          title={`${point.volume} sales`}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* X-axis */}
            <div className="flex justify-between px-1 mt-2">
              {data.map((point, i) => (
                <span key={i} className="text-[10px] text-center font-medium" style={{ width: barWidth, color: "var(--theme-text-secondary)" }}>
                  {point.date}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Summary stats */}
        <div className="mt-6 grid grid-cols-3 gap-6 border-t border-white/[0.04] pt-5">
          <div>
            <p className="text-[10px] uppercase tracking-[0.1em] font-semibold" style={{ color: "var(--theme-text-secondary)" }}>Average</p>
            <p className="mt-1 text-base font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>
              ${(data.reduce((s, d) => s + d.price, 0) / data.length).toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-[0.1em] font-semibold" style={{ color: "var(--theme-text-secondary)" }}>Highest</p>
            <p className="mt-1 text-base font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>
              ${maxPrice.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-[0.1em] font-semibold" style={{ color: "var(--theme-text-secondary)" }}>Lowest</p>
            <p className="mt-1 text-base font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>
              ${minPrice.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
