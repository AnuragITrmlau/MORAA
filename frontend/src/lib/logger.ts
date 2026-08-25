// ============================================================
// logger.ts — Structured Logger Utility
// MORAA GemVision
// ============================================================

export type LogLevel = "debug" | "info" | "warn" | "error";

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  requestId?: string;
  data?: Record<string, unknown>;
  durationMs?: number;
}

/**
 * Flexible metadata type for log calls.
 * Accepts any key-value pairs for structured logging.
 */
export type LogMeta = Record<string, unknown>;

const LOG_LEVEL_PRIORITY: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

class Logger {
  private minLevel: LogLevel = "debug";

  setMinLevel(level: LogLevel): void {
    this.minLevel = level;
  }

  private shouldLog(level: LogLevel): boolean {
    return LOG_LEVEL_PRIORITY[level] >= LOG_LEVEL_PRIORITY[this.minLevel];
  }

  private formatEntry(entry: LogEntry): string {
    return JSON.stringify(entry);
  }

  private log(
    level: LogLevel,
    message: string,
    meta?: LogMeta
  ): void {
    if (!this.shouldLog(level)) return;

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      ...meta,
    };

    const formatted = this.formatEntry(entry);

    if (level === "error") {
      console.error(formatted);
    } else if (level === "warn") {
      console.warn(formatted);
    } else {
      console.log(formatted);
    }
  }

  debug(
    message: string,
    meta?: LogMeta
  ): void {
    this.log("debug", message, meta);
  }

  info(
    message: string,
    meta?: LogMeta
  ): void {
    this.log("info", message, meta);
  }

  warn(
    message: string,
    meta?: LogMeta
  ): void {
    this.log("warn", message, meta);
  }

  error(
    message: string,
    meta?: LogMeta
  ): void {
    this.log("error", message, meta);
  }
}

export const logger = new Logger();

export function generateRequestId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 10);
  const counter = Math.random().toString(36).substring(2, 6);
  return `req_${timestamp}${random}${counter}`;
}
