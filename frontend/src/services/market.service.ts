// Market Service - Mock implementation
// Replace with FastAPI calls when backend is ready

import type {
  MarketData,
  CompetitorProduct,
  TrendData,
  SEOData,
  RiskAssessment,
  PricePoint,
} from "@/types";

const MOCK_DELAY = 800;

const MOCK_MARKET_DATA: MarketData[] = [
  { id: "m1", date: "2026-01", averagePrice: 2650, medianPrice: 2500, highestPrice: 4500, lowestPrice: 1200, totalListings: 145, totalSales: 38, category: "Gold Necklace" },
  { id: "m2", date: "2026-02", averagePrice: 2720, medianPrice: 2600, highestPrice: 4800, lowestPrice: 1300, totalListings: 152, totalSales: 42, category: "Gold Necklace" },
  { id: "m3", date: "2026-03", averagePrice: 2680, medianPrice: 2550, highestPrice: 4600, lowestPrice: 1250, totalListings: 148, totalSales: 40, category: "Gold Necklace" },
  { id: "m4", date: "2026-04", averagePrice: 2800, medianPrice: 2700, highestPrice: 5000, lowestPrice: 1350, totalListings: 160, totalSales: 45, category: "Gold Necklace" },
  { id: "m5", date: "2026-05", averagePrice: 2900, medianPrice: 2750, highestPrice: 5200, lowestPrice: 1400, totalListings: 168, totalSales: 50, category: "Gold Necklace" },
  { id: "m6", date: "2026-06", averagePrice: 2850, medianPrice: 2700, highestPrice: 5100, lowestPrice: 1380, totalListings: 155, totalSales: 48, category: "Gold Necklace" },
];

const MOCK_PRICE_POINTS: PricePoint[] = [
  { date: "2026-01", price: 2650, volume: 38 },
  { date: "2026-02", price: 2720, volume: 42 },
  { date: "2026-03", price: 2680, volume: 40 },
  { date: "2026-04", price: 2800, volume: 45 },
  { date: "2026-05", price: 2900, volume: 50 },
  { date: "2026-06", price: 2850, volume: 48 },
];

const MOCK_COMPETITORS: CompetitorProduct[] = [
  {
    id: "c1", name: "Victorian Gold Diamond Necklace", platform: "Etsy", price: 3200, currency: "USD",
    link: "#", material: "18K Yellow Gold", weight: 14.2, goldPurity: "18K",
    sellerRating: 4.8, salesCount: 127, listedDate: "2026-03-15",
  },
  {
    id: "c2", name: "Antique Style Gold Pendant", platform: "Amazon", price: 2450, currency: "USD",
    link: "#", material: "14K Yellow Gold", weight: 10.5, goldPurity: "14K",
    sellerRating: 4.5, salesCount: 89, listedDate: "2026-04-02",
  },
  {
    id: "c3", name: "Handcrafted Gold Necklace with Gems", platform: "eBay", price: 1890, currency: "USD",
    link: "#", material: "18K Rose Gold", weight: 8.8, goldPurity: "18K",
    sellerRating: 4.3, salesCount: 210, listedDate: "2026-02-20",
  },
  {
    id: "c4", name: "Luxury Diamond Gold Necklace", platform: "1stdibs", price: 5600, currency: "USD",
    link: "#", material: "18K White Gold", weight: 16.0, goldPurity: "18K",
    sellerRating: 4.9, salesCount: 45, listedDate: "2026-05-10",
  },
  {
    id: "c5", name: "Vintage Gold Chain Necklace", platform: "Poshmark", price: 1100, currency: "USD",
    link: "#", material: "10K Yellow Gold", weight: 6.5, goldPurity: "10K",
    sellerRating: 4.2, salesCount: 310, listedDate: "2026-04-28",
  },
];

const MOCK_TRENDS: TrendData[] = [
  { keyword: "gold necklace", growth: 24.5, volume: 85000, sentiment: "positive" },
  { keyword: "victorian jewelry", growth: 18.2, volume: 42000, sentiment: "positive" },
  { keyword: "diamond pendant", growth: -5.3, volume: 38000, sentiment: "neutral" },
  { keyword: "vintage gold", growth: 32.7, volume: 28000, sentiment: "positive" },
  { keyword: "18k necklace", growth: 12.1, volume: 22000, sentiment: "positive" },
];

const MOCK_SEO: SEOData[] = [
  { keyword: "gold necklace women", searchVolume: 25000, difficulty: 65, opportunity: "medium", currentRank: null, suggestedTags: ["gold", "necklace", "18k", "yellow gold"] },
  { keyword: "victorian necklace", searchVolume: 8500, difficulty: 35, opportunity: "high", currentRank: 12, suggestedTags: ["victorian", "vintage", "antique", "gold"] },
  { keyword: "diamond gold necklace", searchVolume: 18000, difficulty: 78, opportunity: "low", currentRank: null, suggestedTags: ["diamond", "gold", "necklace", "luxury"] },
  { keyword: "handmade gold jewelry", searchVolume: 12000, difficulty: 42, opportunity: "medium", currentRank: 8, suggestedTags: ["handmade", "artisan", "gold", "unique"] },
];

const MOCK_RISKS: RiskAssessment[] = [
  { category: "Price Volatility", risk: "medium", score: 45, description: "Gold prices show moderate fluctuations affecting valuation.", mitigation: "Consider dynamic pricing strategy." },
  { category: "Market Saturation", risk: "low", score: 25, description: "Moderate competition with manageable saturation levels.", mitigation: "Focus on unique design differentiation." },
  { category: "Counterfeit Risk", risk: "high", score: 72, description: "Premium segment faces higher counterfeit concerns.", mitigation: "Implement authentication certificates." },
  { category: "Supply Chain", risk: "low", score: 18, description: "Stable supply chain with multiple verified sources.", mitigation: "Maintain diversified supplier relationships." },
];

export async function getMarketData(): Promise<MarketData[]> {
  await new Promise((r) => setTimeout(r, MOCK_DELAY));
  return MOCK_MARKET_DATA;
}

export async function getPricePoints(): Promise<PricePoint[]> {
  await new Promise((r) => setTimeout(r, MOCK_DELAY));
  return MOCK_PRICE_POINTS;
}

export async function getCompetitorProducts(): Promise<CompetitorProduct[]> {
  await new Promise((r) => setTimeout(r, MOCK_DELAY));
  return MOCK_COMPETITORS;
}

export async function getTrendData(): Promise<TrendData[]> {
  await new Promise((r) => setTimeout(r, MOCK_DELAY));
  return MOCK_TRENDS;
}

export async function getSEOData(): Promise<SEOData[]> {
  await new Promise((r) => setTimeout(r, MOCK_DELAY));
  return MOCK_SEO;
}

export async function getRiskAssessments(): Promise<RiskAssessment[]> {
  await new Promise((r) => setTimeout(r, MOCK_DELAY));
  return MOCK_RISKS;
}
