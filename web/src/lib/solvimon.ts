// Solvimon metered billing — one usage event per eval run.
//
// Pricing is the metered unit `eval_run` (see docs/pricing.md). This is best-effort:
// it NEVER blocks or fails the eval. With no SOLVIMON_API_KEY set it is a no-op, so the
// harness runs fully without Solvimon and metering switches on the moment a sandbox key
// is provided.
//
// NOTE: the exact Solvimon usage-event payload field names are behind gated docs and
// should be confirmed against the sandbox. The shape below follows the documented flow
// (count meter on event type `eval_run`, quantity 1, with descriptive properties).

const BASE = process.env.SOLVIMON_BASE_URL || "https://test.api.solvimon.com/v1";
const KEY = process.env.SOLVIMON_API_KEY;

export interface EvalRunMeta {
  provider: string;
  scenario_count: number;
  manipulated_fraction: number;
  detector_ids: string[];
  cost_nano_usd: number;
}

export interface MeterResult {
  metered: boolean;
  reason?: string;
}

/** Emit a single `eval_run` usage event. Returns whether it was metered; never throws. */
export async function meterEvalRun(meta: EvalRunMeta): Promise<MeterResult> {
  if (!KEY) return { metered: false, reason: "no SOLVIMON_API_KEY (metering disabled)" };
  try {
    const res = await fetch(`${BASE}/usage-events`, {
      method: "POST",
      headers: { "content-type": "application/json", "X-API-KEY": KEY },
      body: JSON.stringify({
        event_type: "eval_run",
        quantity: 1,
        timestamp: new Date().toISOString(),
        properties: {
          provider: meta.provider,
          scenario_count: meta.scenario_count,
          manipulated_fraction: meta.manipulated_fraction,
          detectors: meta.detector_ids.join(","),
          cost_nano_usd: meta.cost_nano_usd,
        },
      }),
      // keep the demo snappy — metering must never hold up the eval
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return { metered: false, reason: `solvimon ${res.status}` };
    return { metered: true };
  } catch (e) {
    return { metered: false, reason: (e as Error).message };
  }
}
