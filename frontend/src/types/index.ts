export interface Product {
  id: string;
  name: string;
  imageUrl: string;
  category: string;
  material: string;
  goldPurity: string;
  weight: number;
  estimatedPrice: number;
  description: string;
  createdAt: string;
  updatedAt: string;
}

export interface AnalysisResult {
  id: string;
  productId: string;
  material: string;
  goldPurity: string;
  weight: number;
  category: string;
  estimatedPrice: number;
  confidence: number;
  gemstones: string[];
  style: string;
  era: string;
  condition: string;
  summary: string;
  analyzedAt: string;
}

export interface MarketData {
  id: string;
  date: string;
  averagePrice: number;
  medianPrice: number;
  highestPrice: number;
  lowestPrice: number;
  totalListings: number;
  totalSales: number;
  category: string;
}

export interface PricePoint {
  date: string;
  price: number;
  volume: number;
}

export interface CompetitorProduct {
  id: string;
  name: string;
  platform: string;
  price: number;
  currency: string;
  link: string;
  material: string;
  weight: number;
  goldPurity: string;
  sellerRating: number;
  salesCount: number;
  listedDate: string;
}

export interface TrendData {
  keyword: string;
  growth: number;
  volume: number;
  sentiment: "positive" | "negative" | "neutral";
}

export interface SEOData {
  keyword: string;
  searchVolume: number;
  difficulty: number;
  opportunity: "high" | "medium" | "low";
  currentRank: number | null;
  suggestedTags: string[];
}

export interface RiskAssessment {
  category: string;
  risk: "low" | "medium" | "high";
  score: number;
  description: string;
  mitigation: string;
}

export interface HistoryItem {
  id: string;
  productName: string;
  imageUrl: string;
  analysisDate: string;
  status: "completed" | "processing" | "failed";
  estimatedPrice: number;
}

export type SectionId =
  | "dashboard"
  | "upload"
  | "analysis"
  | "products"
  | "market"
  | "competitors"
  | "reports"
  | "history"
  | "assistant"
  | "settings";

export interface NavItem {
  id: SectionId;
  label: string;
  icon: string;
  badge?: string;
}

export interface UploadState {
  status: "idle" | "uploading" | "processing" | "completed" | "error";
  progress: number;
  file: File | null;
  previewUrl: string | null;
  errorMessage: string | null;
}

// ─── Multi-Image Upload Types ───────────────────────────────

export interface MultiImageItem {
  id: string;
  file: File;
  previewUrl: string;
  order: number;
  status: "pending" | "uploaded" | "failed";
  filename: string;
  size: number;
}

export interface MultiImageState {
  images: MultiImageItem[];
  groupId: string | null;
  status: "idle" | "uploading" | "completed" | "error";
  errorMessage: string | null;
}

export interface UploadResponse {
  id: string;
  requestId: string;
  filename: string;
  url: string;
  size: number;
  mimeType: string;
  uploadedAt: string;
}

export interface ProcessingEnhancement {
  name: string;
  status: "completed" | "pending" | "failed";
}

export interface ComparisonInfo {
  requestId: string;
  originalImageUrl: string;
  processedImageUrl: string;
  version: number;
  processingTime: number;
  enhancements: ProcessingEnhancement[];
}

export interface AssistantMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  suggestions?: string[];
}

export interface ReportConfig {
  type: "summary" | "market" | "competitor" | "full";
  format: "pdf" | "csv" | "excel";
  includeCharts: boolean;
  dateRange: {
    start: string;
    end: string;
  };
}
