# ProvingGround — Hackathon Submission Pack

Working file collecting the submission deliverables. Assets in this folder:
`proving_ground_card.png` / `.svg` (project image).

---

## Project Description (3 paragraphs)

**ProvingGround** is a validation harness for market-manipulation detection. The hard problem
in financial surveillance isn't *detecting* manipulation — it's *proving* your detector works.
Regulators require banks and exchanges to demonstrate their surveillance models catch abuse,
but real trading data isn't labelled (nobody tags which trades were spoofing), so there's no
ground truth to measure against. ProvingGround closes that gap by manufacturing the labelled
reality: it generates synthetic-but-realistic order-book scenarios with *injected, labelled*
spoofing, so the right answers are known by construction.

From that one idea, ProvingGround runs a full evaluation loop: **generate → inject → run
detectors → score → attest → verify**. It pits two detectors head-to-head — a rule-based
heuristic and a finance-tuned LLM — and measures each on catch rate, false-positive rate, and
the specific scenarios it missed. Every scored run is written to decentralized storage as a
content-addressed record, so anyone can re-fetch it, recompute its hash, and confirm the
benchmark wasn't tampered with — turning a catch-rate *claim* into a catch-rate *proof*. A
dashboard surfaces the head-to-head scoreboard, a drill-down into each miss (the order book
with the spoof orders highlighted and the ground-truth explanation), and the one-click verify.

The core engine is **spec-driven**: it's generated from a single specification file by
Codeplain, which also auto-generates its conformance tests — a clean parallel to the product
itself (Codeplain generates tests for code; ProvingGround generates tests for detection
models). The result is a compact, reproducible, end-to-end prototype of the validation
infrastructure that regulated firms are obligated to have but currently can't build — with 39
unit and 68 conformance tests passing, and a live, tamper-evident storage round-trip proven on
testnet.

---

> Remaining sections (Submission Details, links, deck) appended as they're produced.

---

## Challenge Explanation (how we incorporate each selected challenge)

**Codeplain — best project built with Codeplain.** The entire core engine is generated from a
single specification, `core/proving_ground.plain` — 12 functional specs, each one an observable
CLI subcommand — using Codeplain's official `plain-forge` authoring skills. Codeplain renders
both the implementation *and* its conformance tests; we never hand-edited generated code, only
the spec. There's a clean thematic rhyme: Codeplain auto-generates conformance tests for code,
and ProvingGround auto-generates conformance tests for *detection models*. The committed
`core/build/` shows the full spec → code → 68 passing conformance tests chain, built on only 19
of 100 credits.

**FLock — Sovereign AI.** The LLM detector runs on FLock's finance-native reasoning model
`qwen3-235b-a22b-thinking-qwfin` over the OpenAI-compatible API (LiteLLM `x-litellm-api-key`),
and we track the cost of every call in nano-USD against a pinned price table. The sovereignty
angle is the point: financial-surveillance validation is exactly the workload a bank *cannot*
outsource to a centralized frontier model — it touches market-abuse signals and regulatory
evidence — so running it on FLock's sovereign, finance-tuned models is a genuine fit, not a
checkbox.

**Sui — the next AI-native app with DeepBook and Walrus.** Walrus is the trust layer: every
scored run is written to Walrus testnet as a content-addressed blob, and a one-click *verify*
re-fetches the bytes and recomputes the hash, so the benchmark is tamper-evident (we proved the
full write → verify → tamper-detection round-trip live, and even caught two real testnet quirks
doing so — a User-Agent block and propagation delay). DeepBook supplies the realism: the
dashboard pulls the live DeepBook SUI/USDC order book (read-only mainnet indexer) and surfaces
its mid price, spread, and depth, so our manufactured scenarios are calibrated against genuine
market structure rather than arbitrary numbers. Together they make ProvingGround AI-native
end-to-end on Sui — real market structure in, verifiable evaluation record out.

**BGA — AI Trading and Strategy track.** ProvingGround is the integrity layer beneath AI
trading and surveillance strategy: it measures whether a detection strategy actually works, on
labelled data, with a result that's cryptographically checkable. The `scenario_set_hash` binds
each benchmark to its exact inputs, so anchoring it makes *benchmark integrity itself*
verifiable — you can't quietly cherry-pick a favorable test set. That's the fairness primitive
a fairer-markets mission needs: not just "our model is good," but "here is the tamper-evident
proof, on the data we committed to."

**Solvimon — most likely to be a successful business.** The unit of value is one *eval run*, so
that is exactly what we meter: the dashboard emits one `eval_run` usage event per benchmark
(sandbox `X-API-KEY`), and the pricing is a real model — a free allowance, then a small per-run
rate, plus a low platform fee aligned with the customer's outcome (`docs/pricing.md`). The
buyer already exists and is *obligated* to validate their models (banks, exchanges, regulators)
but has no way to do it — a wedge with a built-in compliance budget, which is what makes it a
fundable business rather than a demo.

---

---

## Submission Details

### What we built
ProvingGround is an end-to-end validation harness for market-manipulation detection. It runs
the full loop **generate → inject → detect → score → attest → verify**, exposed both as a
deterministic Python CLI core and as a Next.js dashboard. The core manufactures labelled
order-book scenarios (clean baseline order flow plus *injected, labelled* spoofing — a large
order placed far from the mid price and cancelled before it fills), runs two detectors against
them (a rule-based heuristic and a finance-tuned LLM), scores catch rate / false-positive rate
/ precision / per-miss detail, writes the scored result to Walrus as a content-addressed blob,
and lets anyone verify it by re-fetching and recomputing the hash.

### The insight
The hard problem in surveillance isn't detection — it's *validation*. Regulated firms are
required to prove their detection models work, but real manipulation in their data isn't
labelled, so there's no ground truth to measure against. ProvingGround manufactures that ground
truth: because we inject the spoofing ourselves, we know exactly which events are manipulation
(`implicated_event_ids`), turning "is this model good?" into a measurable, reproducible number.

### How we built it (process)
The core was built **spec-first with Codeplain**. We authored one specification file,
`core/proving_ground.plain`, as 12 functional specs — each one an observable CLI subcommand —
using Codeplain's official `plain-forge` skills. Codeplain rendered both the implementation and
its conformance tests; we never hand-edited generated code, only the spec, and re-rendered. We
worked credit-frugally (free `--dry-run` validation, incremental `--render-from`, `--headless`
to avoid a TUI hang), spending **19 of 100 credits** for the whole core. The work proceeded in
milestones: M1 core loop, M2 FLock LLM detector + head-to-head benchmark, M4 Walrus
tamper-evidence, M3 dashboard, M5 polish (README, Solvimon metering, pricing). Throughout, a
deterministic offline **stub** backs every integration, keeping all 68 conformance + 39 unit
tests hermetic — no network, no flakiness — while the real FLock / Walrus / DeepBook backends
are selected explicitly.

### Integrations, validated against the live APIs
Rather than coding from memory, we cross-checked each provider against its live API and saved
the responses as fixtures — which surfaced real bugs a mock would have hidden:
- **FLock:** OpenAI-compatible, `x-litellm-api-key`, finance-native `qwen3-235b-a22b-thinking-qwfin`,
  per-call cost in nano-USD. The live check caught that our first render *discarded* token
  counts (cost read 0) and *silently swallowed* a provider error as a "miss" — both fixed via
  the spec (cost accumulates; provider failures exit loudly) and proven with a local mock.
- **Walrus:** content-addressed write to the testnet publisher, read back from the aggregator,
  verify by recomputing the hash. The live round-trip caught two real testnet quirks — the
  aggregator 403s the default `Python-urllib` User-Agent, and fresh blobs have a propagation
  delay — both handled. Tamper-detection (corrupt the blob → `verified:false`, non-zero exit)
  is proven.
- **DeepBook:** the dashboard reads the live SUI/USDC order book from the mainnet indexer and
  surfaces mid/spread/depth, so scenarios are calibrated against genuine market structure.
- **Solvimon:** the dashboard meters one `eval_run` usage event per benchmark (best-effort,
  no-op without a key), with a real pricing model in `docs/pricing.md`.

### Architecture
Two root modules with a thin boundary, intentionally *not* coupled (different tech stacks): the
**Codeplain-generated Python core** (`core/`, stdlib-only, JSON-in/JSON-out) and the
**hand-built Next.js 16 dashboard** (`web/`). The dashboard's API routes shell into the core
CLI; because the core is fully deterministic by `--seed`, separate `generate-set` and
`benchmark` invocations stay in lockstep, so the miss drill-down shows exactly the scenarios
that were scored.

### Current status
The build is demo-ready: full core loop + dashboard working, **39 unit + 68 conformance tests
passing**, with live Walrus write/verify/tamper-detection and live DeepBook reads proven. Every
integration also has a deterministic offline stub, so the demo runs reliably without depending
on a live network.

---

## Links

- **Code:** https://github.com/mvresh/eval-harness (branch `claude/quirky-lovelace-9jmpkz-gmhybz`)
- **Presentation:** `docs/submission/deck.html` (6 slides; open in a browser, print to PDF)
- **Live demo:** runs locally — `cd web && npm install && npm run dev` → http://localhost:3000
  (public Vercel URL deferred; see caveats above)
