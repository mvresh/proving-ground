import { NextResponse } from "next/server";
import { runCore, type Attestation, type VerifyResult } from "@/lib/core";
import { fixtures, coreUnavailable } from "@/lib/demo";

export const runtime = "nodejs";

// POST /api/verify { attestation, store }
// Re-fetches the blob, recomputes its hash, and reports whether it matches. The core
// exits non-zero on a mismatch (tamper); we still parse stdout to surface the detail.
export async function POST(req: Request) {
  let body: { attestation?: Attestation; store?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }
  if (!body.attestation) {
    return NextResponse.json({ error: "missing attestation" }, { status: 400 });
  }
  const store = body.store === "walrus" ? "walrus" : "stub";

  try {
    const { code, stdout, stderr } = await runCore(
      ["verify", "--store", store],
      JSON.stringify(body.attestation),
    );
    let result: VerifyResult | null = null;
    try {
      result = JSON.parse(stdout) as VerifyResult;
    } catch {
      // verify may print nothing parseable on certain failures (e.g. network)
    }
    if (!result) {
      return NextResponse.json(
        { error: stderr.trim() || `verify exited with code ${code}`, verified: false },
        { status: 502 },
      );
    }
    // exit code 0 => verified; non-zero => tamper detected (verified:false already in result)
    return NextResponse.json({ store, result, exitCode: code, stderr: stderr.trim() });
  } catch (e) {
    if (coreUnavailable(e)) return NextResponse.json(fixtures.verify);
    return NextResponse.json(
      { error: (e as Error).message, verified: false },
      { status: 502 },
    );
  }
}
