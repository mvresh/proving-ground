import { NextResponse } from "next/server";
import { runCoreJson, CoreError, type Attestation } from "@/lib/core";
import { fixtures, coreUnavailable } from "@/lib/demo";

export const runtime = "nodejs";

// POST /api/attest { seed, count, fraction, store }
// Produces a RunResult, then stores it in the selected BlobStore and returns the
// Attestation (run_id, scenario_set_hash, store, blob_id, content_sha256).
export async function POST(req: Request) {
  let body: { seed?: number; count?: number; fraction?: number; store?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }
  const seed = Number(body.seed ?? 7);
  const count = Number(body.count ?? 10);
  const fraction = Number(body.fraction ?? 0.4);
  const store = body.store === "walrus" ? "walrus" : "stub";

  try {
    const runResult = await runCoreJson<Record<string, unknown>>([
      "run",
      "--seed", String(seed),
      "--count", String(count),
      "--manipulated-fraction", String(fraction),
    ]);
    const attestation = await runCoreJson<Attestation>(
      ["attest", "--store", store],
      JSON.stringify(runResult),
    );
    return NextResponse.json({ store, attestation });
  } catch (e) {
    if (coreUnavailable(e)) return NextResponse.json(fixtures.attest);
    const err = e as CoreError;
    return NextResponse.json(
      { error: err.message, stderr: err.stderr ?? "" },
      { status: 502 },
    );
  }
}
