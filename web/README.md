# ProvingGround dashboard (M3)

Next.js dashboard for the ProvingGround manipulation eval harness. It surfaces the two
"money moments": the **head-to-head detector comparison with a miss drill-down**, and the
**tamper-evident Walrus record with client-side verify**.

## How it talks to the core

The dashboard is a **separate root module** from the Python core — different tech stack, so
it is intentionally *not* a Codeplain `requires` dependency. The Next.js API routes shell
into the Codeplain-generated Python CLI (`core/build/proving_ground.py`) and parse its JSON.
Because the core is fully deterministic by `--seed`, the API can run `generate-set` and
`benchmark` as separate invocations and still have them line up (the scenarios returned for
the drill-down are exactly the ones the benchmark scored).

```
browser ──► Next API route ──► python3 proving_ground.py <cmd>  (stdin/stdout JSON)
```

| Route | Core commands | Purpose |
|-------|---------------|---------|
| `GET  /api/models?provider=` | `models --provider` | model catalog (live FLock catalog when `provider=flock`) |
| `POST /api/run` | `generate-set` + `benchmark` | head-to-head metrics + misses + scenarios for drill-down |
| `POST /api/attest` | `run` + `attest --store` | write the scored run to a blob store, return the attestation |
| `POST /api/verify` | `verify --store` | re-fetch + recompute hash → tamper-evidence |

## Running locally

```bash
# 1. build the Python core first (from repo root) — see core/ and docs/HANDOFF.md
# 2. then:
cd web
npm install
npm run dev          # http://localhost:3000
```

### Configuration (env)

| Var | Default | Meaning |
|-----|---------|---------|
| `CORE_DIR` | `../core/build` (relative to `web/`) | directory holding the built `proving_ground.py` |
| `PYTHON_BIN` | `python3` | Python interpreter used to run the core |
| `FLOCK_API_KEY` | — | only needed for the live `flock` provider (see repo `.env`) |
| `WALRUS_PUBLISHER_URL` / `WALRUS_AGGREGATOR_URL` | testnet defaults | only needed to override the Walrus endpoints |

The `walrus` store and `flock` provider make live network calls; the default `stub`
provider and `stub` store keep the whole dashboard offline and deterministic.

## Notes

- Built on Next.js 16 (App Router). API routes run on the Node.js runtime (they spawn a
  child process), so this dashboard runs on a Node host — a Vercel deploy would need the
  Python core exposed as an HTTP service instead of shelled-into (deferred; see build plan).
- `npm run build` succeeds; `/` is static, `/api/*` are dynamic.
