import { spawn } from "node:child_process";
import path from "node:path";

// The ProvingGround Python core (Codeplain-generated) is a CLI that reads JSON on
// stdin and writes JSON on stdout. The dashboard shells into it. Deterministic seeds
// keep separate invocations (e.g. generate-set + benchmark) in lockstep.
//
// CORE_DIR overrides the location of the built core; by default we resolve it
// relative to the web/ working directory (npm run dev runs from web/).
const CORE_DIR =
  process.env.CORE_DIR || path.resolve(process.cwd(), "..", "core", "build");
const PYTHON = process.env.PYTHON_BIN || "python3";
const MAIN = "proving_ground.py";

export interface CoreResult {
  code: number;
  stdout: string;
  stderr: string;
}

/** Run the core CLI with the given args, optionally piping `input` to stdin. */
export function runCore(args: string[], input?: string): Promise<CoreResult> {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [MAIN, ...args], {
      cwd: CORE_DIR,
      env: { ...process.env },
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));
    child.on("error", (err) =>
      reject(new Error(`Failed to spawn core (${PYTHON} ${MAIN}): ${err.message}`)),
    );
    child.on("close", (code) => resolve({ code: code ?? -1, stdout, stderr }));
    if (input !== undefined) {
      child.stdin.write(input);
    }
    child.stdin.end();
  });
}

/** Run the core and parse stdout as JSON; throw with stderr on failure. */
export async function runCoreJson<T = unknown>(
  args: string[],
  input?: string,
): Promise<T> {
  const { code, stdout, stderr } = await runCore(args, input);
  if (code !== 0) {
    throw new CoreError(
      stderr.trim() || `core exited with code ${code}`,
      code,
      stderr.trim(),
    );
  }
  try {
    return JSON.parse(stdout) as T;
  } catch {
    throw new CoreError(
      `core produced non-JSON output: ${stdout.slice(0, 200)}`,
      code,
      stderr.trim(),
    );
  }
}

export class CoreError extends Error {
  code: number;
  stderr: string;
  constructor(message: string, code: number, stderr: string) {
    super(message);
    this.name = "CoreError";
    this.code = code;
    this.stderr = stderr;
  }
}

// ---- Domain types mirrored from the core's JSON schemas (read-only on this side) ----

export interface OrderEvent {
  event_id: string;
  ts: number;
  type: "place" | "cancel" | "modify" | "trade";
  order_id: string;
  side: "bid" | "ask";
  price: number;
  size: number;
  owner_id: string;
}

export interface GroundTruth {
  label: "clean" | "manipulated";
  manipulation_type: string | null;
  implicated_event_ids: string[];
  explanation: string;
}

export interface Scenario {
  scenario_id: string;
  market: string;
  duration_ms: number;
  events: OrderEvent[];
  ground_truth: GroundTruth;
}

export interface Metrics {
  catch_rate: number;
  false_positive_rate: number;
  precision: number;
  by_type: Record<string, { caught: number; total: number }>;
}

export interface Miss {
  scenario_id: string;
  manipulation_type: string;
  explanation: string;
}

export interface DetectorEntry {
  detector_id: string;
  metrics: Metrics;
  misses: Miss[];
}

export interface BenchmarkResult {
  scenario_set_hash: string;
  detectors: DetectorEntry[];
  cost_nano_usd: number;
}

export interface Attestation {
  run_id: string;
  scenario_set_hash: string;
  store: "stub" | "walrus";
  blob_id: string;
  content_sha256: string;
}

export interface VerifyResult {
  verified: boolean;
  blob_id: string;
  computed_sha256: string;
  expected_sha256: string;
}
