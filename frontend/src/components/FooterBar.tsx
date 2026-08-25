"use client";

import { Gem } from "lucide-react";

export default function FooterBar() {
  return (
    <footer className="w-full border-t border-white/[0.04] py-10 mt-24">
      <div className="flex flex-col items-center justify-center gap-3 px-6">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <Gem size={16} className="text-[#3B82F6] drop-shadow-[0_0_6px_rgba(59,130,246,0.3)]" />
            <div className="absolute -inset-2 bg-[#3B82F6] opacity-[0.06] blur-lg rounded-full" />
          </div>
          <span className="text-sm font-semibold text-[#94A3B8]">MORAA GemVision</span>
        </div>
        <p className="text-xs text-white/20 font-medium">
          AI-Powered Jewellery Image Analysis
        </p>
      </div>
    </footer>
  );
}
