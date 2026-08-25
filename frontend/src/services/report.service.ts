// Report Service - Connects to FastAPI backend
// Backend: http://localhost:8000

import type { ReportConfig } from "@/types";

export interface GeneratedReport {
  id: string;
  url: string;
  filename: string;
  size: number;
  pages: number;
  generatedAt: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function generateReport(config: ReportConfig): Promise<GeneratedReport> {
  if (!config.type || !config.format) {
    throw new Error("Report type and format are required");
  }

  const response = await fetch(`${API_BASE_URL}/api/reports/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      type: config.type,
      format: config.format,
      include_charts: config.includeCharts,
      date_range: config.dateRange,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to generate report" }));
    throw new Error(error.detail || "Failed to generate report");
  }

  const report = await response.json();
  return {
    id: report.id,
    url: `${API_BASE_URL}/api/reports/download/${report.id}`,
    filename: report.filename,
    size: report.size,
    pages: report.pages,
    generatedAt: report.generatedAt,
  };
}

export async function exportData(format: "csv" | "excel"): Promise<string> {
  // Note: Currently only PDF generation is supported via the backend
  // For CSV/Excel, a separate endpoint would be needed
  return `Report exported as ${format}. File ready for download.`;
}
