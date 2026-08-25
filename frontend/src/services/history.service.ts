// History Service - Connects to FastAPI backend
// Backend: http://localhost:8000

import type { HistoryItem } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getHistory(): Promise<HistoryItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/history`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to fetch history" }));
    throw new Error(error.detail || "Failed to fetch history");
  }

  const data = await response.json();
  const items = data.items || data || [];

  return items.map((item: any) => ({
    id: item.id,
    productName: item.productName,
    imageUrl: item.imageUrl,
    analysisDate: item.analysisDate,
    status: item.status,
    estimatedPrice: item.estimatedPrice,
  }));
}

export async function deleteHistoryItem(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/history/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to delete history item" }));
    throw new Error(error.detail || "Failed to delete history item");
  }
}

export async function getHistoryStats(): Promise<{ total: number; thisMonth: number; averagePrice: number }> {
  const response = await fetch(`${API_BASE_URL}/api/history/stats`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to fetch stats" }));
    throw new Error(error.detail || "Failed to fetch stats");
  }

  const stats = await response.json();
  return {
    total: stats.total,
    thisMonth: stats.thisMonth,
    averagePrice: stats.averagePrice,
  };
}
