# ProvingGround

**A validation harness for market-manipulation detection.** Built for the Encode Vibe Coding
Hackathon.

> The hard problem in manipulation detection isn't detection — it's **validation**. You can't
> prove a surveillance model works without ground-truth labels, and real manipulation isn't
> labelled. ProvingGround manufactures the labelled reality: it generates synthetic order-book
> scenarios with **injected, labelled** spoofing, runs detectors against them, scores catch
> rate / false positives / misses, and writes a **tamper-evident** record you can verify.

```
generate → inject → run detectors → score → attest (Walrus) → verify → dashboard
```

## Why this matters

Regulated firms are *required* to prove their surveillance models work — but they can't, because
real manipulation in their data isn't labelled. ProvingGround is a prototype of the **validation
infrastructure** that closes that gap: synthetic-but-labelled scenarios give you ground truth by
construction, so catch rate, false-positive rate, and the specific misses become measurable —
and the benchmark record becomes tamper-evident and checkable by a third party.

## What's in the box

| Part | Path | Stack | Built with |
|------|------|-------|-----------|
| **Core** — generate / inject / detect / score / run / benchmark / attest / verify | `core/` | Python 3, stdlib-only | **Codeplain** (`.plain` → code) |
| **Dashboard** — head-to-head, miss drill-down, Walrus verify | `web/` | Next.js 16 | hand-built |

The core is **specification-driven**: `core/proving_ground.plain` is the source of truth, and
Codeplain renders the implementation *and its conformance tests* from it. The generated code
lives in `core/build/` for transparency.

## The core CLI

Every capability is one deterministic, JSON-in/JSON-out subcommand. All randomness derives from
`--seed`, so runs are reproducible.

```bash
cd core/build
python3 proving_ground.py generate --seed 42 --events 60
python3 proving_ground.py generate-set --seed 7 --count 10 --manipulated-fraction 0.4
python3 proving_ground.py run --seed 7 --count 10 --manipulated-fraction 0.4
python3 proving_ground.py benchmark --seed 7 --count 10 --manipulated-fraction 0.4
python3 proving_ground.py run ... | python3 proving_ground.py attest --store walrus
... | python3 proving_ground.py verify --store walrus
python3 proving_ground.py models --provider flock
```

- **Detectors:** a heuristic detector (`heuristic_v1`) and an LLM detector (`llm_v1`) running on
  **FLock**'s finance-native model `qwen3-235b-a22b-thinking-qwfin`.
- **Providers / stores are pluggable**: an offline deterministic **stub** (default — keeps tests
  hermetic) and the real **FLock** / **Walrus** backends. LLM cost is tracked in **nano-USD**.

## Running it

```bash
# core (no third-party dependencies)
cd core
bash scripts/run_unittests_python.sh build                       # 39 unit tests
bash scripts/run_conformance_tests_python.sh build conformance_tests/proving_ground  # 68 conformance tests

# dashboard
cd web && npm install && npm run dev      # http://localhost:3000
```

Set `FLOCK_API_KEY` for the live LLM head-to-head; the Walrus testnet needs no key; the live
DeepBook SUI/USDC market reference is read-only.

## How it maps to the bounties

| Bounty | What ProvingGround does |
|--------|--------------------------|
| **Codeplain** | The entire core is generated from `core/proving_ground.plain` — 12 functional specs, each one a CLI subcommand, with auto-generated conformance tests (68 passing). We auto-generate conformance tests for *detection models* the way Codeplain does for code. Authored with the official `plain-forge` skills (see `.claude/`). |
| **FLock — Sovereign AI** | The LLM detector runs on FLock's finance-native `qwen3-235b-a22b-thinking-qwfin` (OpenAI-compatible, `x-litellm-api-key`), with per-call **nano-USD** cost tracking and a live model catalog. |
| **Sui — Walrus + DeepBook** | Each scored run is written to Walrus as a content-addressed blob; **verify** re-fetches and recomputes the hash → tamper-evident. The dashboard reads the live DeepBook SUI/USDC book as the market reference. |
| **BGA — AI Trading & Strategy** | The `scenario_set_hash` binds a benchmark to its exact inputs, making **benchmark integrity cryptographically checkable** — a fairness primitive. |
| **Solvimon** | Metered **per-eval-run** billing — pricing is infrastructure. See [`docs/pricing.md`](docs/pricing.md). |

## Repository layout

```
core/    proving_ground.plain (source of truth) · resources/ (JSON schemas) · build/ (generated) · scripts/
web/     Next.js dashboard (App Router) · src/lib/core.ts (boundary to the core CLI)
docs/    pricing · submission (deck + write-up)
.claude/ plain-forge skills + rules used to author the spec
```
