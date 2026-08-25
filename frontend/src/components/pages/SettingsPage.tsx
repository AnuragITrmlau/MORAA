"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ChevronRight, User, Bell, Palette, Shield, Sun, Moon, Check, Save } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/contexts/ThemeContext";

const settingsSections = [
  {
    id: "profile",
    icon: User,
    label: "Profile Information",
    description: "Update your personal details and public profile.",
    fields: [
      { label: "Full Name", value: "Administrator" },
      { label: "Email", value: "admin@moraagemvision.com" },
      { label: "Role", value: "System Administrator" },
    ],
  },
  {
    id: "notifications",
    icon: Bell,
    label: "Notification Settings",
    description: "Manage your email and in-app notification preferences.",
    toggles: [
      { key: "analysis", label: "Analysis complete notifications", enabled: true },
      { key: "weekly", label: "Weekly summary emails", enabled: false },
      { key: "updates", label: "Product updates and tips", enabled: true },
    ],
  },
  {
    id: "appearance",
    icon: Palette,
    label: "Theme Preference",
    description: "Customize the appearance of your workspace.",
  },
  {
    id: "security",
    icon: Shield,
    label: "Account Security",
    description: "Manage your password and security settings.",
  },
];

export default function SettingsPage() {
  const [mounted, setMounted] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const [toggles, setToggles] = useState<Record<string, boolean>>({
    analysis: true,
    weekly: false,
    updates: true,
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleToggle = (key: string) => {
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

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
        <span className="font-semibold" style={{ color: "var(--theme-text)" }}>Settings</span>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={mounted ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="mb-10"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight" style={{ color: "var(--theme-text)" }}>Settings</h1>
            <p className="mt-2 text-sm" style={{ color: "var(--theme-text-secondary)" }}>Manage your account and application preferences.</p>
          </div>
          <button
            onClick={handleSave}
            className="btn-primary flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold shadow-[0_4px_16px_rgba(59,130,246,0.25)]"
          >
            {saved ? (
              <>
                <Check size={15} />
                Saved
              </>
            ) : (
              <>
                <Save size={15} />
                Save Changes
              </>
            )}
          </button>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={mounted ? { opacity: 1 } : {}}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="space-y-6"
      >
        {settingsSections.map((section, i) => {
          const Icon = section.icon;
          return (
            <motion.div
              key={section.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className="rounded-2xl glass-card p-6"
            >
              <div className="flex items-center gap-3 mb-5">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl neumorphic">
                  <Icon size={18} className="text-[#3B82F6]" />
                </div>
                <div>
                  <h3 className="text-base font-semibold" style={{ color: "var(--theme-text)" }}>{section.label}</h3>
                  <p className="text-xs mt-0.5" style={{ color: "var(--theme-text-secondary)" }}>{section.description}</p>
                </div>
              </div>

              {/* Profile fields */}
              {"fields" in section && section.fields && (
                <div className="space-y-3">
                  {section.fields.map((field) => (
                    <div key={field.label} className="flex items-center justify-between py-2.5 border-b last:border-0" style={{ borderColor: "var(--theme-border)" }}>
                      <span className="text-sm" style={{ color: "var(--theme-text-secondary)" }}>{field.label}</span>
                      <span className="text-sm font-semibold" style={{ color: "var(--theme-text)" }}>{field.value}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Notification toggles */}
              {"toggles" in section && section.toggles && (
                <div className="space-y-4">
                  {section.toggles.map((toggle) => (
                    <div key={toggle.key} className="flex items-center justify-between py-1">
                      <span className="text-sm" style={{ color: "var(--theme-text-secondary)" }}>{toggle.label}</span>
                      <button
                        onClick={() => handleToggle(toggle.key)}
                        className={cn(
                          "relative w-11 h-6 rounded-full transition-all duration-300 cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-[#3B82F6]/50",
                          toggles[toggle.key] ? "bg-[#3B82F6] shadow-[0_0_10px_rgba(59,130,246,0.35)]" : ""
                        )}
                        style={{ backgroundColor: toggles[toggle.key] ? undefined : "var(--theme-text-white-high)" }}
                        role="switch"
                        aria-checked={toggles[toggle.key]}
                        aria-label={toggle.label}
                      >
                        <div
                          className={cn(
                            "absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-md transition-all duration-300",
                            toggles[toggle.key] && "translate-x-5"
                          )}
                        />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Theme selector */}
              {section.id === "appearance" && (
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => theme === "light" ? null : toggleTheme()}
                    className={cn(
                      "flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold transition-all duration-200",
                      theme === "light"
                        ? "btn-primary shadow-[0_4px_16px_rgba(59,130,246,0.25)]"
                        : "btn-secondary"
                    )}
                    aria-pressed={theme === "light"}
                  >
                    <Sun size={15} />
                    Light
                  </button>
                  <button
                    onClick={() => theme === "dark" ? null : toggleTheme()}
                    className={cn(
                      "flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold transition-all duration-200",
                      theme === "dark"
                        ? "btn-primary shadow-[0_4px_16px_rgba(59,130,246,0.25)]"
                        : "btn-secondary"
                    )}
                    aria-pressed={theme === "dark"}
                  >
                    <Moon size={15} />
                    Dark
                  </button>
                </div>
              )}

              {/* Security placeholder */}
              {section.id === "security" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between py-2.5 border-b" style={{ borderColor: "var(--theme-border)" }}>
                    <span className="text-sm" style={{ color: "var(--theme-text-secondary)" }}>Password</span>
                    <button className="text-sm font-semibold text-[#3B82F6] hover:text-[#60A5FA] transition-colors">Change</button>
                  </div>
                  <div className="flex items-center justify-between py-2.5 border-b" style={{ borderColor: "var(--theme-border)" }}>
                    <span className="text-sm" style={{ color: "var(--theme-text-secondary)" }}>Two-Factor Authentication</span>
                    <button className="text-sm font-semibold text-[#3B82F6] hover:text-[#60A5FA] transition-colors">Enable</button>
                  </div>
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-sm" style={{ color: "var(--theme-text-secondary)" }}>Active Sessions</span>
                    <span className="text-sm font-semibold" style={{ color: "var(--theme-text)" }}>1 Session</span>
                  </div>
                </div>
              )}
            </motion.div>
          );
        })}
      </motion.div>
    </div>
  );
}
