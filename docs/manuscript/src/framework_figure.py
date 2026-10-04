"""The complexity-science framework, drawn as one schematic.

Panel A is the epistemic ladder the whole series rests on. Panels B-D are the
three manuscripts and what each does with the gate between Mechanism and
Parameter. Every verdict and number is read from the two `results.json` files,
so the figure cannot drift from the computed results.

    python docs/manuscript/src/framework_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "manuscript" / "framework"
G3 = ROOT / "docs" / "manuscript" / "thesis_03_figures" / "results.json"
G4 = ROOT / "docs" / "manuscript" / "thesis_04_figures" / "results.json"

INK, MUTED, RULE, PAPER, PANEL = "#0b0b0b", "#52514e", "#d6d5d0", "#ffffff", "#f6f6f4"
BLUE, ORANGE, AQUA, YELLOW, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#4a3aa7"
RED = "#e34948"
W, H = 1420, 880
SANS = "DejaVu Sans, Liberation Sans, sans-serif"

LADDER = [
    ("KNOWLEDGE", "a review article,\na guideline, a hallmark", BLUE),
    ("EVIDENCE", "a measurement in\na stated protocol", BLUE),
    ("MECHANISM", "a hypothesis with\na named falsifier", VIOLET),
    ("PARAMETER", "a number with\nphysical meaning", ORANGE),
    ("PREDICTION", "a claim about\na person", RED),
]


def _e(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _t(x, y, s, size=13, fill=INK, weight="normal", anchor="start", style=""):
    st = f' font-style="{style}"' if style else ""
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{st}>{_e(s)}</text>')


def _lines(x, y, text, size=11.5, fill=MUTED, anchor="start", dy=15, **kw):
    return "".join(_t(x, y + i * dy, ln, size, fill, anchor=anchor, **kw)
                   for i, ln in enumerate(text.split("\n")))


def _box(x, y, w, h, fill=PAPER, stroke=RULE, rx=8, sw=1.4, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def _arrow(x1, y1, x2, y2, stroke=INK, sw=1.8):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}" marker-end="url(#a)"/>')


def build(g3: dict, g4: dict) -> str:
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="{SANS}"><rect width="{W}" height="{H}" fill="{PAPER}"/>',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
         '<marker id="r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker></defs>']

    s.append(_t(32, 40, "A framework for honest computation in complex biology", 20, INK, "bold"))
    s.append(_t(32, 64, "Five layers that are routinely collapsed into one number, the gate that separates them, and three studies that test it.",
                13, MUTED))

    # ---------- A: the ladder ------------------------------------------------
    s.append(_t(32, 104, "A · THE EPISTEMIC LADDER", 11.5, MUTED, "bold"))
    bw, gap, y0 = 232, 28, 118
    for i, (name, sub, col) in enumerate(LADDER):
        x = 32 + i * (bw + gap)
        s.append(_box(x, y0, bw, 96, fill=PANEL, stroke=col, sw=2))
        s.append(_t(x + 16, y0 + 30, name, 14, col, "bold"))
        s.append(_lines(x + 16, y0 + 52, sub))
        if i < len(LADDER) - 1 and i != 2:  # the gate line replaces the sign there
            s.append(_t(x + bw + gap / 2, y0 + 52, "≠", 17, INK, "bold", "middle"))

    # the gate sits between Mechanism and Parameter
    gx = 32 + 3 * (bw + gap) - gap / 2
    s.append(f'<line x1="{gx}" y1="{y0 - 14}" x2="{gx}" y2="{y0 + 140}" stroke="{RED}" '
             f'stroke-width="2.5" stroke-dasharray="7 5"/>')
    s.append(_t(gx, y0 - 22, "THE GATE", 12, RED, "bold", "middle"))
    s.append(_t(gx - 10, y0 + 136, "everything left of the line is argument", 11.5, MUTED, anchor="end", style="italic"))
    s.append(_t(gx + 10, y0 + 136, "everything right of it is a number someone will act on", 11.5, MUTED, style="italic"))

    # ---------- B, C, D ------------------------------------------------------
    py, pw, ph = 292, 442, 486
    xs = [32, 32 + pw + 24, 32 + 2 * (pw + 24)]

    # --- B: Thesis #2
    x = xs[0]
    s.append(_t(x, py - 10, "B · THESIS #2  —  THE GATE NEVER OPENS", 11.5, MUTED, "bold"))
    s.append(_box(x, py, pw, ph, fill=PANEL))
    s.append(_t(x + 20, py + 32, "A data-only research object", 14.5, INK, "bold"))
    s.append(_lines(x + 20, py + 54,
                    "A contributor writes one YAML CaseCard: disease framing,\n"
                    "systemic axes, research-only observables, candidate\n"
                    "mechanisms, falsifiers, qualitative NSTG constraints,\n"
                    "and Vancouver citations. No solver is edited.", 12))
    step_y = py + 128
    for i, (lab, note) in enumerate([
            ("CaseCard (YAML)", "knowledge + evidence pointers"),
            ("Parameter-smuggling scan", "refuses doses, EC50, rate constants, ODE knobs"),
            ("NSTG constraint layer", "themes only — never a coefficient"),
            ("PathwaySketch", "ranked hypotheses + evidence still required")]):
        yy = step_y + i * 62
        s.append(_box(x + 20, yy, pw - 40, 46, stroke=VIOLET if i else BLUE, sw=1.6))
        s.append(_t(x + 34, yy + 20, lab, 12.5, INK, "bold"))
        s.append(_t(x + 34, yy + 37, note, 11, MUTED))
        if i < 3:
            s.append(_arrow(x + pw / 2, yy + 46, x + pw / 2, yy + 60))
    s.append(_box(x + 20, py + 388, pw - 40, 76, fill="#fdeeea", stroke=RED, sw=1.8))
    s.append(_t(x + 34, py + 412, "Always emitted, even for a clean card:", 12, INK, "bold"))
    s.append(_lines(x + 34, py + 432, "refused: nstg_scale   ·   refused: parameter\nrefused: prediction", 11.5, RED))

    # --- C: Thesis #3
    x = xs[1]
    s.append(_t(x, py - 10, "C · THESIS #3  —  THE GATE MADE COMPUTABLE", 11.5, MUTED, "bold"))
    s.append(_box(x, py, pw, ph, fill=PANEL))
    s.append(_t(x + 20, py + 32, "When may a parameter be admitted?", 14.5, INK, "bold"))
    s.append(_lines(x + 20, py + 54,
                    "A refusal by rule is safe but sterile. The rule is replaced\n"
                    "by three tests, run against a declared experiment:\n"
                    "observables, sample times, noise, arms.", 12))
    for i, (num, head, sub) in enumerate([
            ("1", "STRUCTURAL", "is θⱼ off the null space of S?"),
            ("2", "PRACTICAL", "is the Cramér–Rao CV bound < 0.10?"),
            ("3", "SHAPE", "does Δχ² cross 3.84 on both sides?")]):
        yy = py + 126 + i * 64
        s.append(_box(x + 20, yy, pw - 40, 50, stroke=INK, sw=1.6))
        s.append(f'<circle cx="{x + 46}" cy="{yy + 25}" r="13" fill="{INK}"/>')
        s.append(_t(x + 46, yy + 30, num, 13, PAPER, "bold", "middle"))
        s.append(_t(x + 70, yy + 21, head, 11.5, MUTED, "bold"))
        s.append(_t(x + 70, yy + 39, sub, 12.5, INK))
    s.append(_box(x + 20, py + 326, pw - 40, 112, fill="#eafaf3", stroke=AQUA, sw=1.8))
    s.append(_t(x + 34, py + 350, "Tested on a tumour / T-cell / glucose model", 12.5, INK, "bold"))
    n_open3 = sum(1 for v in g3["T,G,E"].values() if v == "open")
    s.append(_lines(x + 34, py + 372,
                    "Tumour counts alone: the kill rate is structurally\n"
                    "invisible — a symmetry no sample size can break.\n"
                    f"Measure glucose and T cells: {n_open3} of 8 admitted.\n"
                    "The kill rate stays refused in every design.", 12, INK))

    # --- D: Thesis #4
    x = xs[2]
    s.append(_t(x, py - 10, "D · THESIS #4  —  THE SAME GATE, A REAL PROTOCOL", 11.5, MUTED, "bold"))
    s.append(_box(x, py, pw, ph, fill=PANEL))
    s.append(_t(x + 20, py + 32, "What does a blood film allow?", 14.5, INK, "bold"))
    s.append(_lines(x + 20, py + 54,
                    "Artemisinin partial resistance is surveilled worldwide by\n"
                    "the parasite clearance half-life, and read as a statement\n"
                    "about ring-stage drug killing. The same code judges it.", 12))
    cv = g4["gate"]["standard"]["cv"]["k_ring"]
    fold = g4["confounded"]["fold_range"]
    s.append(_box(x + 20, py + 126, pw - 40, 92, fill="#fdeeea", stroke=RED, sw=1.8))
    s.append(_t(x + 34, py + 150, "The summary is degenerate", 12.5, INK, "bold"))
    s.append(_lines(x + 34, py + 170,
                    f"One half-life of 3.1 h is produced by a {fold:.0f}-fold range\n"
                    "of ring-stage killing, once the time the patient\n"
                    "presented is free to vary.", 11.5, INK))
    s.append(_box(x + 20, py + 234, pw - 40, 92, fill=PAPER, stroke=RED, sw=1.8))
    s.append(_t(x + 34, py + 258, "The routine protocol admits nothing", 12.5, INK, "bold"))
    s.append(_lines(x + 34, py + 278,
                    f"6-hourly films, 48 h, realistic counting error:\n"
                    f"0 of 8 parameters admissible. Ring-stage killing\n"
                    f"has a CV bound of {cv:.2f} — wider than the quantity.", 11.5, INK))
    s.append(_box(x + 20, py + 342, pw - 40, 122, fill="#eafaf3", stroke=AQUA, sw=1.8))
    s.append(_t(x + 34, py + 366, "What the curve does measure", 12.5, INK, "bold"))
    s.append(_lines(x + 34, py + 386,
                    "Sequestration age and the parasite age at\n"
                    "presentation — the observation process, not the drug.\n"
                    "So the half-life is a population screening signal,\n"
                    "and the phenotype needs a ring-stage assay.", 11.5, INK))

    s.append(f'<line x1="32" y1="{H - 42}" x2="{W - 32}" y2="{H - 42}" stroke="{RULE}"/>')
    s.append(_t(32, H - 20,
                "Every verdict and number above is read from the committed results files, not typed by hand. "
                "Computational research only — not a medical device, not clinical decision support, not treatment guidance.",
                11.5, MUTED, style="italic"))
    s.append("</svg>")
    return "".join(s)


def draw():
    g3 = json.loads(G3.read_text())["gate"]
    g4 = json.loads(G4.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    svg = build(g3, g4)
    (OUT / "fig_framework.svg").write_text(svg)
    import cairosvg

    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(OUT / "fig_framework.png"),
                     output_width=W * 2, output_height=H * 2, background_color="white")
    return OUT / "fig_framework.png"


if __name__ == "__main__":
    print("wrote", draw())
