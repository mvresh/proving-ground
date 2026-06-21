import { NextResponse } from "next/server";
import { runCoreJson, CoreError } from "@/lib/core";
import { fixtures, coreUnavailable } from "@/lib/demo";

export const runtime = "nodejs";

// GET /api/models?provider=stub|flock -> string[] of model identifiers.
export async function GET(req: Request) {
  const provider = new URL(req.url).searchParams.get("provider") ?? "stub";
  try {
    const models = await runCoreJson<string[]>(["models", "--provider", provider]);
    return NextResponse.json({ provider, models });
  } catch (e) {
    // On a host without the core, serve the precomputed catalog (real snapshot).
    if (coreUnavailable(e)) {
      const key = provider === "flock" ? "flock" : "stub";
      return NextResponse.json({ provider, models: fixtures.models[key] ?? [], demo: true });
    }
    const err = e as CoreError;
    return NextResponse.json(
      { provider, models: [], error: err.message },
      { status: 200 },
    );
  }
}
