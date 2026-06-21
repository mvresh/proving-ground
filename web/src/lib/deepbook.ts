// DeepBook — live SUI/USDC market reference (read-only mainnet indexer, no key).
//
// ProvingGround anchors its synthetic scenarios to a real market: we pull the live
// DeepBook SUI/USDC order book and surface its mid price, spread, and depth so the
// manufactured order books are calibrated against genuine market structure rather than
// arbitrary numbers.

const BASE =
  process.env.DEEPBOOK_INDEXER_URL ||
  "https://deepbook-indexer.mainnet.mystenlabs.com";

export interface MarketRef {
  pool: string;
  mid: number;
  best_bid: number;
  best_ask: number;
  spread: number;
  spread_bps: number;
  bid_depth: number; // summed qty of the top levels returned
  ask_depth: number;
  timestamp: string;
  source: string;
}

type Level = [string, string]; // [price, qty]
interface BookResponse {
  timestamp?: string | number;
  bids?: Level[];
  asks?: Level[];
}

const sumQty = (levels: Level[]) =>
  levels.reduce((acc, [, q]) => acc + Number(q), 0);

/** Fetch the live DeepBook SUI/USDC book; throws on network/parse failure. */
export async function fetchMarketRef(pool = "SUI_USDC"): Promise<MarketRef> {
  const res = await fetch(`${BASE}/orderbook/${pool}?level=2&depth=0`, {
    signal: AbortSignal.timeout(15000),
    // a custom UA avoids the same default-urllib/CDN blocks seen on Walrus
    headers: { "User-Agent": "ProvingGround/1.0" },
  });
  if (!res.ok) throw new Error(`DeepBook ${res.status}`);
  const book = (await res.json()) as BookResponse;
  const bids = book.bids ?? [];
  const asks = book.asks ?? [];
  if (bids.length === 0 || asks.length === 0) {
    throw new Error("DeepBook returned an empty book");
  }
  const bestBid = Number(bids[0][0]);
  const bestAsk = Number(asks[0][0]);
  const mid = (bestBid + bestAsk) / 2;
  const spread = bestAsk - bestBid;
  return {
    pool,
    mid,
    best_bid: bestBid,
    best_ask: bestAsk,
    spread,
    spread_bps: mid > 0 ? (spread / mid) * 10000 : 0,
    bid_depth: sumQty(bids),
    ask_depth: sumQty(asks),
    timestamp: String(book.timestamp ?? Date.now()),
    source: "DeepBook mainnet indexer · SUI_USDC",
  };
}
