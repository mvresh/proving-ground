#!/usr/bin/env python3
"""Build the ProvingGround 6-slide deck as SVG -> PNG -> single PDF (deterministic render)."""
import cairosvg
from PIL import Image
import os

W, H = 1280, 720
BG = "#07090f"
OUT = os.path.dirname(os.path.abspath(__file__))

HEAD = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
 font-family="Helvetica, Arial, sans-serif">
<defs>
 <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
   <stop offset="0" stop-color="#0a0f1a"/><stop offset="1" stop-color="#070910"/></linearGradient>
 <radialGradient id="g1" cx="0.82" cy="0.04" r="0.6">
   <stop offset="0" stop-color="#38bdf8" stop-opacity="0.16"/><stop offset="1" stop-color="#38bdf8" stop-opacity="0"/></radialGradient>
 <radialGradient id="g2" cx="0.03" cy="0.06" r="0.55">
   <stop offset="0" stop-color="#a855f7" stop-opacity="0.14"/><stop offset="1" stop-color="#a855f7" stop-opacity="0"/></radialGradient>
 <linearGradient id="title" x1="0" y1="0" x2="1" y2="0">
   <stop offset="0" stop-color="#e6edf3"/><stop offset="1" stop-color="#7dd3fc"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#g1)"/>
<rect width="{W}" height="{H}" fill="url(#g2)"/>'''

MONO = "monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def eyebrow(text):
    return (f'<circle cx="78" cy="74" r="6" fill="#38bdf8"/>'
            f'<text x="94" y="80" fill="#7dd3fc" font-size="19" letter-spacing="3" '
            f'font-weight="600">{esc(text.upper())}</text>')


def foot(left, right):
    return (f'<line x1="72" y1="660" x2="{W-72}" y2="660" stroke="#ffffff" stroke-opacity="0.10"/>'
            f'<text x="72" y="690" fill="#5b6b7e" font-size="16" font-family="{MONO}">{esc(left)}</text>'
            f'<text x="{W-72}" y="690" fill="#5b6b7e" font-size="16" text-anchor="end">{esc(right)}</text>')


def bullets(items, x=78, y=300, gap=58, size=24, color="#9fb0c3"):
    out = []
    cy = y
    for it in items:
        out.append(f'<rect x="{x}" y="{cy-12}" width="10" height="10" rx="3" fill="#38bdf8"/>')
        # it is a list of (text, bold) spans rendered on one line
        tx = x + 26
        spans = "".join(
            f'<tspan fill="{"#e6edf3" if b else color}" font-weight="{700 if b else 400}">{esc(t)}</tspan>'
            for t, b in it)
        out.append(f'<text x="{tx}" y="{cy}" font-size="{size}">{spans}</text>')
        cy += gap
    return "".join(out)


def chip(x, y, w, text, kind=""):
    stroke = {"p": "#7c3aed", "g": "#10b981"}.get(kind, "#2b3a4f")
    fill = {"p": "#c4b5fd", "g": "#6ee7b7"}.get(kind, "#cdd9e5")
    return (f'<rect x="{x}" y="{y}" width="{w}" height="50" rx="11" fill="#0d1117" stroke="{stroke}" stroke-opacity="0.8"/>'
            f'<text x="{x+w/2}" y="{y+32}" fill="{fill}" font-size="21" font-weight="600" '
            f'text-anchor="middle" font-family="{MONO}">{esc(text)}</text>')


def card(x, y, w, h, tag, title, body_lines):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#ffffff" fill-opacity="0.03" stroke="#ffffff" stroke-opacity="0.10"/>']
    out.append(f'<text x="{x+24}" y="{y+34}" fill="#38bdf8" font-size="14" font-weight="700" letter-spacing="1">{esc(tag.upper())}</text>')
    out.append(f'<text x="{x+24}" y="{y+66}" fill="#e6edf3" font-size="23" font-weight="700">{esc(title)}</text>')
    by = y + 98
    for ln in body_lines:
        out.append(f'<text x="{x+24}" y="{by}" fill="#9fb0c3" font-size="18">{esc(ln)}</text>')
        by += 26
    return "".join(out)


slides = []

# 1 — TITLE
s = HEAD + eyebrow("Manipulation eval harness")
s += '<text x="72" y="250" fill="url(#title)" font-size="92" font-weight="800" letter-spacing="-2">ProvingGround</text>'
s += '<text x="74" y="312" fill="#9fb0c3" font-size="27">Proving market-surveillance models work — by manufacturing</text>'
s += '<text x="74" y="350" fill="#9fb0c3" font-size="27">the labelled reality they\'re missing.</text>'
xs = 74
for i, (lab, w, k) in enumerate([("generate",150,""),("inject",118,""),("detect",132,""),("score",118,""),("attest",132,"p"),("verify",132,"g")]):
    s += chip(xs, 430, w, lab, k)
    xs += w + 16
    if i < 5:
        s += f'<text x="{xs-9}" y="462" fill="#3b4d63" font-size="24" text-anchor="middle">→</text>'
        xs += 14
s += foot("Encode Vibe Coding Hackathon", "Codeplain · FLock · Sui/Walrus · DeepBook · Solvimon · BGA")
s += "</svg>"
slides.append(s)

# 2 — PROBLEM
s = HEAD + eyebrow("The problem")
s += '<text x="72" y="170" fill="#e6edf3" font-size="44" font-weight="750">Detection is easy to claim.</text>'
s += '<text x="72" y="224" fill="#e6edf3" font-size="44" font-weight="750">It\'s impossible to <tspan fill="#38bdf8">prove</tspan>.</text>'
s += '<text x="72" y="300" fill="#e6edf3" font-size="29" font-weight="600">Regulated firms must show their surveillance models catch abuse.</text>'
s += bullets([
    [("Real trading data ", False), ("isn't labelled", True), (" — nobody tags which trades were spoofing.", False)],
    [("So there's ", False), ("no ground truth", True), (" to measure a detector against.", False)],
    [("The hard problem isn't detection — it's ", False), ("validation", True), (". That's the gap.", False)],
], y=380, gap=58)
s += foot("ProvingGround", "01 / problem")
s += "</svg>"
slides.append(s)

# 3 — SOLUTION
s = HEAD + eyebrow("The idea")
s += '<text x="72" y="170" fill="#e6edf3" font-size="46" font-weight="750">Manufacture the labelled reality.</text>'
s += '<text x="72" y="222" fill="#9fb0c3" font-size="25">Generate realistic order books, inject the spoofing ourselves, and record</text>'
s += '<text x="72" y="254" fill="#9fb0c3" font-size="25">exactly which events are manipulation. Now detection is measurable.</text>'
cw, ch = 540, 132
s += card(72, 300, cw, ch, "Known by construction", "Ground truth, for free", ["Every scenario is labelled clean /", "manipulated, with the implicated", "spoof event IDs."])
s += card(668, 300, cw, ch, "Head-to-head", "Two detectors, scored", ["Heuristic vs finance-tuned LLM —", "catch rate, false positives, and", "the exact misses."])
s += card(72, 452, cw, ch, "Tamper-evident", "Provable, not asserted", ["Each result is written to Walrus", "and re-verifiable by recomputing", "its hash."])
s += card(668, 452, cw, ch, "Spec-driven", "Built with Codeplain", ["The whole core is generated from", "one spec — plus its conformance", "tests."])
s += foot("ProvingGround", "02 / solution")
s += "</svg>"
slides.append(s)

# 4 — HOW
s = HEAD + eyebrow("How it works")
s += '<text x="72" y="172" fill="#e6edf3" font-size="46" font-weight="750">One deterministic loop, end to end.</text>'
s += bullets([
    [("generate / inject", True), (" — clean stochastic order flow, then a planted spoof", False)],
    [("(large order far from mid, cancelled before fill) with labelled ground truth.", False)],
    [("detect / score", True), (" — both detectors; catch rate, FPR, precision, and a", False)],
    [("drill-down into every miss (order book + why it was manipulation).", False)],
    [("attest / verify", True), (" — write the run to Walrus; verify by recomputing the", False)],
    [("hash. Tamper a byte and verification fails.", False)],
    [("calibrated to a real market", True), (" — the live DeepBook SUI/USDC book seeds realism.", False)],
], y=250, gap=50, size=23)
s += chip(72, 600, 700, "python proving_ground.py benchmark --seed 7 --count 10")
s += foot("Python core (Codeplain) + Next.js dashboard", "03 / how")
s += "</svg>"
slides.append(s)

# 5 — BOUNTIES
s = HEAD + eyebrow("One build, six bounties")
s += '<text x="72" y="172" fill="#e6edf3" font-size="46" font-weight="750">The same loop satisfies every track.</text>'
s += card(72, 250, cw, 150, "Codeplain", "Spec -> code -> tests", ["12 specs, 68 conformance tests,", "19/100 credits. We generate tests for", "models; they generate tests for code."])
s += card(668, 250, cw, 150, "FLock — Sovereign AI", "Finance-native LLM", ["qwen3-235b-a22b-thinking-qwfin,", "nano-USD cost. Surveillance is exactly", "what you can't outsource."])
s += card(72, 420, cw, 150, "Sui — Walrus + DeepBook", "Verifiable + real", ["Tamper-evident record on Walrus;", "live DeepBook SUI/USDC as the", "market reference."])
s += card(668, 420, cw, 150, "BGA · Solvimon", "Fair + fundable", ["Benchmark integrity is checkable;", "metered per eval-run, with a buyer", "obligated to validate."])
s += foot("ProvingGround", "04 / bounties")
s += "</svg>"
slides.append(s)

# 6 — STATUS
s = HEAD + eyebrow("Status & what's next")
s += '<text x="72" y="172" fill="#e6edf3" font-size="48" font-weight="800">Demo-ready today.</text>'
for i, (n, l, c) in enumerate([("68", "conformance tests passing", "#10b981"),
                                ("39", "unit tests passing", "#38bdf8"),
                                ("19", "/ 100 Codeplain credits", "#a855f7")]):
    x = 72 + i * 320
    s += f'<text x="{x}" y="290" fill="{c}" font-size="64" font-weight="800">{n}</text>'
    s += f'<text x="{x}" y="320" fill="#9fb0c3" font-size="18">{esc(l)}</text>'
s += bullets([
    [("Proven live:", True), (" Walrus write -> verify -> tamper-detection; DeepBook reads; the loop.", False)],
    [("Next:", True), (" FLock account top-up for the live LLM head-to-head (code is mock-proven);", False)],
    [("Solvimon key to flip metering live; Vercel deploy (core as a service).", False)],
    [("Vision:", True), (" validation infrastructure for the firms obligated to prove their models.", False)],
], y=400, gap=50, size=22)
s += foot("github.com/mvresh/eval-harness", "05 / status")
s += "</svg>"
slides.append(s)

# Render
pngs = []
for i, svg in enumerate(slides, 1):
    p = os.path.join(OUT, f"slide_{i}.png")
    cairosvg.svg2png(bytestring=svg.encode(), write_to=p, output_width=W, output_height=H)
    pngs.append(p)

imgs = [Image.open(p).convert("RGB") for p in pngs]
imgs[0].save(os.path.join(OUT, "ProvingGround_deck.pdf"), save_all=True, append_images=imgs[1:])
print(f"rendered {len(pngs)} slides + ProvingGround_deck.pdf")
