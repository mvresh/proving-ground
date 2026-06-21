import { NextResponse } from "next/server";
import { runCoreJson, CoreError } from "@/lib/core";

export const runtime = "nodejs";

// GET /api/models?provider=stub|flock -> string[] of model identifiers.
export async function GET(req: Request) {
  const provider = new URL(req.url).searchParams.get("provider") ?? "stub";
  try {
    const models = await runCoreJson<string[]>(["models", "--provider", provider]);
    return NextResponse.json({ provider, models });
  } catch (e) {
    const err = e as CoreError;
    return NextResponse.json(
      { provider, models: [], error: err.message },
      { status: 200 }, // surface the error in the UI rather than failing the page
    );
  }
}
