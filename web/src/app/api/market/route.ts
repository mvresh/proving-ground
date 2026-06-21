import { NextResponse } from "next/server";
import { fetchMarketRef } from "@/lib/deepbook";

export const runtime = "nodejs";

// GET /api/market -> live DeepBook SUI/USDC market reference (mid, spread, depth).
export async function GET() {
  try {
    const market = await fetchMarketRef("SUI_USDC");
    return NextResponse.json(market);
  } catch (e) {
    return NextResponse.json(
      { error: (e as Error).message },
      { status: 200 }, // surface in the UI rather than failing the page
    );
  }
}
