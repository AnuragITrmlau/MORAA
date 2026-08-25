"use client";

import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { sendMessage } from "@/services/assistant.service";
import type { AssistantMessage } from "@/types";
import { Bot, Send, Sparkles, Instagram, Loader2 } from "lucide-react";
import { getWelcomeMessage } from "@/services/assistant.service";

export default function AssistantPanel() {
  const [messages, setMessages] = useState<AssistantMessage[]>([getWelcomeMessage()]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    setLoading(true);

    const userMsg: AssistantMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    const text = input;
    setInput("");

    try {
      const reply = await sendMessage("session-1", text);
      setMessages((prev) => [...prev, reply]);
    } catch {
      setMessages((prev) => [...prev, {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-full flex-col bg-[#0D111C] relative rounded-2xl glass-strong overflow-hidden">
      {/* Top highlight */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/[0.08] to-transparent pointer-events-none z-10" />

      {/* Header */}
      <div className="flex items-center gap-3 border-b border-white/[0.04] px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#3B82F6] to-[#2563EB] shadow-[0_4px_16px_rgba(59,130,246,0.35)]">
          <Bot size={18} className="text-white" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-[#F8FAFC]">AI Assistant</h3>
          <p className="text-[10px] text-[#94A3B8]">Powered by GemVision AI</p>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-5 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}>
            <div
              className={cn(
                "max-w-[85%] rounded-2xl px-5 py-3.5",
                msg.role === "user"
                  ? "bg-gradient-to-br from-[#3B82F6] to-[#2563EB] text-white rounded-tr-md shadow-[0_4px_16px_rgba(59,130,246,0.25)]"
                  : "bg-white/[0.04] text-[#F8FAFC] rounded-tl-md border border-white/[0.04] backdrop-blur-sm"
              )}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              <p className="mt-2 text-[10px] text-white/40">
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-2xl rounded-tl-md bg-white/[0.04] px-5 py-3.5 border border-white/[0.04] backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <Loader2 size={15} className="animate-spin text-[#3B82F6]" />
                <span className="text-sm text-[#94A3B8]">Analyzing...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="border-t border-white/[0.04] px-5 py-3.5 space-y-2.5">
        <button className="btn-primary flex w-full items-center justify-center gap-2.5 rounded-2xl py-3 text-sm font-semibold">
          <Sparkles size={17} />
          Compare Prices
        </button>
        <button className="btn-secondary flex w-full items-center justify-center gap-2.5 rounded-2xl py-3 text-sm font-semibold">
          <Instagram size={17} />
          Generate IG Post
        </button>
      </div>

      {/* Input */}
      <div className="border-t border-white/[0.04] px-5 py-3.5">
        <div className="flex items-center gap-2.5 rounded-2xl bg-[rgba(17,25,40,0.50)] border border-white/[0.06] px-4 py-2.5 focus-within:border-[#3B82F6]/30 focus-within:bg-[rgba(17,25,40,0.60)] focus-within:shadow-[0_0_0_3px_rgba(59,130,246,0.10)] transition-all duration-300">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about this product..."
            className="flex-1 bg-transparent text-sm text-[#F8FAFC] placeholder-[#94A3B8]/35 outline-none"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-xl transition-all duration-300",
              input.trim() && !loading
                ? "btn-primary"
                : "bg-white/5 text-white/30 cursor-not-allowed"
            )}
          >
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
