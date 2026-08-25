"use client";

import { Bell, Search, Sun, Moon, Gem } from "lucide-react";
import { useTheme } from "@/contexts/ThemeContext";
import { useUIStore } from "@/stores/ui-store";

export default function Header() {
  const { theme, toggleTheme } = useTheme();
  const { sidebarCollapsed } = useUIStore();

  return (
    <header
      className="fixed top-0 right-0 z-30 flex h-[64px] items-center justify-between px-6 border-b backdrop-blur-2xl"
      style={{
        left: sidebarCollapsed ? 68 : 240,
        backgroundColor: "var(--theme-surface)",
        borderColor: "var(--theme-border)",
        boxShadow: "0 1px 0 rgba(255,255,255,0.02) inset",
      }}
    >
      {/* Top highlight */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/[0.08] to-transparent pointer-events-none" />

      {/* Bottom edge glow */}
      <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-blue-500/6 to-transparent pointer-events-none" />

      {/* Left - Premium Brand */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="absolute -inset-2.5 bg-[#3B82F6] opacity-[0.08] blur-xl rounded-full" />
            <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#3B82F6] to-[#2563EB] shadow-[0_4px_16px_rgba(59,130,246,0.3)]">
              <Gem size={18} className="text-white drop-shadow-sm" />
            </div>
          </div>
          <div>
            <span className="text-base font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>
              MORAA
            </span>
            <span className="text-base font-normal ml-1.5 tracking-tight" style={{ color: "var(--theme-text-secondary)" }}>GemVision</span>
          </div>
        </div>
      </div>

      {/* Center - Premium Glass Search */}
      <div className="hidden md:flex items-center flex-1 max-w-lg mx-8">
        <div className="relative w-full group">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 z-10 transition-all duration-300" style={{ color: "var(--theme-text-secondary)" }} />
          <input
            type="text"
            placeholder="Search analyses, products..."
            className="w-full h-10 pl-10 pr-4 rounded-2xl border text-sm outline-none transition-all duration-300 focus:border-[#3B82F6]/30 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.10),0_4px_16px_rgba(0,0,0,0.15)] focus:ring-0"
            style={{
              backgroundColor: "var(--theme-neumorphic)",
              borderColor: "var(--theme-border-light)",
              color: "var(--theme-text)",
            }}
          />
          {/* Search shortcut hint */}
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:flex items-center gap-0.5 text-[10px] border rounded-md px-1.5 py-0.5" style={{ color: "var(--theme-text-secondary)", borderColor: "var(--theme-border)" }}>
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2.5">
        {/* AI Status - Premium badge */}
        <div className="hidden sm:flex items-center gap-2 rounded-2xl bg-gradient-to-r from-green-500/8 to-green-500/4 border border-green-500/15 px-3.5 py-1.5 neumorphic">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-70" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
          </span>
          <span className="text-[10px] font-semibold text-green-400/90 tracking-wide uppercase">AI Active</span>
        </div>

        {/* Divider */}
        <div className="hidden sm:block w-px h-7 mx-1" style={{ backgroundColor: "var(--theme-border)" }} />

        {/* Theme toggle - now fully functional */}
        <button
          onClick={toggleTheme}
          className="flex h-9 w-9 items-center justify-center rounded-xl neumorphic transition-all duration-300 group"
          style={{ color: "var(--theme-text-secondary)" }}
          title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {theme === "dark" ? (
            <Sun size={15} className="group-hover:scale-110 transition-transform duration-300" />
          ) : (
            <Moon size={15} className="group-hover:scale-110 transition-transform duration-300" />
          )}
        </button>

        {/* Notifications */}
        <button className="relative flex h-9 w-9 items-center justify-center rounded-xl neumorphic transition-all duration-300 group" style={{ color: "var(--theme-text-secondary)" }} title="Notifications">
          <Bell size={15} className="group-hover:scale-110 transition-transform duration-300" />
          <span className="absolute top-2 right-2 h-1.5 w-1.5 rounded-full bg-[#3B82F6] shadow-[0_0_6px_rgba(59,130,246,0.6)]" />
        </button>

        {/* Profile */}
        <button className="relative group" title="Profile">
          <div className="absolute -inset-2.5 bg-[#3B82F6] opacity-0 group-hover:opacity-[0.10] blur-2xl rounded-full transition-opacity duration-300" />
          <div className="relative flex h-9 w-9 items-center justify-center rounded-xl overflow-hidden neumorphic">
            <div className="h-full w-full bg-gradient-to-br from-[#3B82F6] to-[#2563EB] flex items-center justify-center shadow-[inset_0_1px_0_rgba(255,255,255,0.15)]">
              <span className="text-xs font-bold text-white drop-shadow-sm">A</span>
            </div>
          </div>
        </button>
      </div>
    </header>
  );
}
