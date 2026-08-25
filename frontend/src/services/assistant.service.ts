import type { AssistantMessage } from "@/types";

const MOCK_RESPONSES: Record<string, string> = {
  default:
    "I've analyzed this jewellery piece and can help with:\n\n" +
    "1. **Detailed Material Analysis** - Breakdown of gold purity, gemstones, and craftsmanship\n" +
    "2. **Market Comparison** - How this piece compares to similar listings\n" +
    "3. **Pricing Recommendations** - Optimal pricing strategy based on market data\n" +
    "4. **Authentication Insights** - Verification markers and authenticity indicators\n\n" +
    "What would you like to know more about?",
  price:
    "Based on the market analysis:\n\n" +
    "• **Estimated Value**: $2,800 - $3,200\n" +
    "• **Market Average**: $2,720 (similar pieces)\n" +
    "• **Premium Factors**: Victorian design (+15%), Diamond accents (+25%)\n" +
    "• **Recommended Price**: $2,990 for optimal sell-through\n\n" +
    "Would you like a detailed pricing breakdown?",
  material:
    "**Material Analysis Results:**\n\n" +
    "• **Primary Material**: 18K Yellow Gold (75% purity)\n" +
    "• **Weight**: 12.45 grams\n" +
    "• **Gemstones**: Diamond (0.25ct, VS2 clarity), Sapphire (0.15ct)\n" +
    "• **Craftsmanship**: Machine-set with hand-finishing details\n" +
    "• **Hallmarks**: 750 stamp detected (18K)\n\n" +
    "The gold content alone is valued at approximately $650.",
};

export async function sendMessage(_sessionId: string, message: string): Promise<AssistantMessage> {
  await new Promise((r) => setTimeout(r, 1200));
  let content = MOCK_RESPONSES.default;
  const lower = message.toLowerCase();
  if (lower.includes("price") || lower.includes("cost") || lower.includes("value"))
    content = MOCK_RESPONSES.price;
  else if (lower.includes("material") || lower.includes("gold") || lower.includes("diamond"))
    content = MOCK_RESPONSES.material;
  return {
    id: `msg-${Date.now()}`,
    role: "assistant",
    content,
    timestamp: new Date().toISOString(),
    suggestions: ["Tell me about pricing", "Analyze materials", "Compare with competitors"],
  };
}

export function getWelcomeMessage(): AssistantMessage {
  return {
    id: "welcome",
    role: "assistant",
    content:
      "👋 Hello! I'm your **AI Jewellery Analyst**. Upload a product image or paste a link, and I'll " +
      "provide detailed analysis including material composition, market value, and competitive insights.",
    timestamp: new Date().toISOString(),
    suggestions: ["Upload an image", "View sample analysis", "How does it work?"],
  };
}
