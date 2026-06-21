import { NextResponse } from "next/server";
import { runCoreJson, CoreError, type Scenario, type BenchmarkResult } from "@/lib/core";
import { meterEvalRun } from "@/lib/solvimon";

export const runtime = "nodejs";

// POST /api/run { seed, count, fraction, provider }
// Runs generate-set AND benchmark with the SAME seed so the scenarios returned for
// the miss drill-down are exactly the ones the benchmark scored (deterministic).
export async function POST(req: Request) {
  let body: { seed?: number; count?: number; fraction?: number; provider?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }
  const seed = Number(body.seed ?? 7);
  const count = Number(body.count ?? 10);
  const fraction = Number(body.fraction ?? 0.4);
  const provider = body.provider === "flock" ? "flock" : "stub";

  const common = [
    "--seed", String(seed),
    "--count", String(count),
    "--manipulated-fraction", String(fraction),
  ];

  try {
    const scenarios = await runCoreJson<Scenario[]>(["generate-set", ...common]);
    const benchmark = await runCoreJson<BenchmarkResult>([
      "benchmark", ...common, "--provider", provider,
    ]);
    // Meter this eval run (Solvimon). Best-effort: a no-op without SOLVIMON_API_KEY,
    // and never allowed to fail the run.
    const metering = await meterEvalRun({
      provider,
      scenario_count: count,
      manipulated_fraction: fraction,
      detector_ids: benchmark.detectors.map((d) => d.detector_id),
      cost_nano_usd: benchmark.cost_nano_usd,
    });
    return NextResponse.json({
      seed, count, fraction, provider, scenarios, benchmark, metering,
    });
  } catch (e) {
    const err = e as CoreError;
    return NextResponse.json(
      { error: err.message, stderr: err.stderr ?? "" },
      { status: 502 },
    );
  }
}
