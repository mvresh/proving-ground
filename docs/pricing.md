# Pricing narrative (Solvimon)

Solvimon's thesis: **pricing is infrastructure — don't vibe-code your pricing.** ProvingGround
takes that literally. The product's unit of value is one **eval run** (generate a labelled
scenario set, run the detectors, score it, attest it), so that is exactly the metered unit.

> **D6 status:** the numbers below are *proposed defaults*, chosen to mirror Solvimon's own
> usage-based, low-take-rate model. Swap in real numbers when you have them.

## The meter

- **Meter type:** `count` on event type **`eval_run`**.
- **One usage event per eval run**, `quantity: 1`, with properties `{ detector_id, provider,
  scenario_count, manipulated_fraction }` so usage can be sliced by model and workload.
- Emitted best-effort at the end of a run; metering never blocks or fails the eval itself.

## The plan (proposed defaults)

| Tier | Allowance | Rate | Rationale |
|------|-----------|------|-----------|
| **Free** | first **1,000** eval runs / month | $0 | enough to validate a model in dev without friction |
| **Usage** | beyond the allowance | **$0.02 / eval run** | the metered unit; dominated by LLM-detector inference cost |
| **Platform fee** | — | **0.4% of customer revenue** processed through the harness | mirrors Solvimon's own ~0.4% take-rate framing |

Why these shapes:

- **Free allowance** removes adoption friction — a team can prove out the harness on a model
  before any spend, which matters for a validation tool bought by risk/compliance teams.
- **Per-eval-run** is honest: cost scales with the thing the customer actually does, and it
  tracks the real underlying cost (FLock inference, tracked in **nano-USD** per call — see the
  `benchmark` command's `cost_nano_usd`). A run that uses the heavier finance model costs more,
  and the meter properties capture which model was used.
- **Low platform fee** keeps the harness aligned with the customer's outcome rather than
  rent-seeking — appropriate for infrastructure a regulated firm runs continuously.

## How it's wired

The dashboard emits one `eval_run` usage event per benchmark via `web/src/lib/solvimon.ts`
(sandbox `https://test.api.solvimon.com`, `X-API-KEY` header). With no `SOLVIMON_API_KEY` set
it is a **no-op** — the harness runs fully without it, and metering switches on the moment a
sandbox key is provided. The MCP-driven setup (meter + plan + checkout) is the fastest path to
a live demo; the exact event-payload field names should be confirmed in the sandbox, since the
Solvimon API docs are gated.

## The slide (one-liner)

*"You're already paying for the model. ProvingGround prices the thing that makes the model
trustworthy — each validated eval run — with a free allowance to start and a take-rate that
stays aligned with your outcome."*
