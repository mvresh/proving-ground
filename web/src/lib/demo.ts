// Demo-mode fallback fixtures.
//
// When the Python core can't be reached (e.g. on Vercel, which has no `python3` and no
// core/ alongside the app), the API routes fall back to these precomputed fixtures so the
// deployed dashboard still works end-to-end. The fixtures are REAL output from the core
// (deterministic seed 7, count 10, manipulated-fraction 0.4) — captured once, not faked.
//
// Locally (where the core runs) the routes return live results and never touch these.

import runFixture from "./fixtures/run.json";
import attestFixture from "./fixtures/attest.json";
import verifyFixture from "./fixtures/verify.json";
import modelsFixture from "./fixtures/models.json";

export const fixtures = {
  run: runFixture,
  attest: attestFixture,
  verify: verifyFixture,
  models: modelsFixture as { stub: string[]; flock: string[] },
};

/**
 * True when an error means the core binary/runtime is unavailable (so we should serve the
 * demo fixture), as opposed to the core running and returning a genuine error.
 */
export function coreUnavailable(err: unknown): boolean {
  const msg = (err as Error)?.message ?? "";
  return (
    msg.includes("Failed to spawn core") || // spawn ENOENT (no python3 / wrong cwd)
    msg.includes("ENOENT") ||
    msg.includes("non-JSON output") ||
    msg.includes("exited with code")
  );
}
