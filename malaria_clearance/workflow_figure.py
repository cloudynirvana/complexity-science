"""Biology-and-gate schematic for Thesis #4, drawn as SVG and rendered to PNG.

The verdict strip is read from `results.json`, so it cannot drift from the
computed results.
"""
from __future__ import annotations

import json
from pathlib import Path

INK, MUTED, RULE, PAPER, PANEL = "#0b0b0b", "#52514e", "#d6d5d0", "#ffffff", "#f6f6f4"
RING, MATURE, DRUG = "#2a78d6", "#4a3aa7", "#eb6834"
OK, BAD = "#1baf7a", "#e34948"
W, H = 1240, 700
SANS = "DejaVu Sans, Liberation Sans, sans-serif"


def _e(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _t(x, y, s, size=13, fill=INK, weight="normal", anchor="start", style=""):
    st = f' font-style="{style}"' if style else ""
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{st}>{_e(s)}</text>')


def _box(x, y, w, h, fill=PAPER, stroke=RULE, rx=7, sw=1.4, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def build_svg(res) -> str:
    gate = res["gate"]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="{SANS}"><rect width="{W}" height="{H}" fill="{PAPER}"/>',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
         '<marker id="g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>']

    s.append(_t(28, 34, "What a parasite clearance curve can and cannot measure", 17, INK, "bold"))
    s.append(_t(28, 56, "The 48-hour cycle, the blood film that samples it, and the verdict of the evidence gate.",
                12.5, MUTED))

    # --- panel A: the cycle -------------------------------------------------
    s.append(_t(28, 92, "A · WITHIN-HOST CYCLE", 11, MUTED, "bold"))
    s.append(_box(28, 102, 372, 250, fill=PANEL))
    cx, cy, r = 150, 222, 74
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RULE}" stroke-width="22"/>')
    s.append(f'<path d="M {cx} {cy - r} A {r} {r} 0 0 1 {cx + r} {cy}" fill="none" '
             f'stroke="{RING}" stroke-width="22"/>')
    s.append(f'<path d="M {cx + r} {cy} A {r} {r} 0 0 1 {cx} {cy + r}" fill="none" '
             f'stroke="{MATURE}" stroke-width="22"/>')
    s.append(_t(cx, cy - 4, "48 h", 15, INK, "bold", "middle"))
    s.append(_t(cx, cy + 16, "cycle", 11.5, MUTED, "middle"))
    s.append(_t(cx + 14, cy - r - 12, "0 h  invasion", 11, INK, "bold"))
    s.append(_t(cx + r + 6, cy - 14, "26 h", 11, INK, "bold"))
    s.append(_t(cx - 4, cy + r + 22, "48 h  burst × PMR", 11, INK, "bold", "middle"))
    s.append(f'<circle cx="258" cy="152" r="7" fill="{RING}"/>')
    s.append(_t(272, 157, "rings — circulate", 12, INK, "bold"))
    s.append(_t(272, 175, "visible on a blood film", 11, MUTED))
    s.append(f'<circle cx="258" cy="206" r="7" fill="{MATURE}"/>')
    s.append(_t(272, 211, "mature — sequester", 12, INK, "bold"))
    s.append(_t(272, 229, "invisible to microscopy", 11, MUTED))
    s.append(_t(258, 268, "Artemisinin kills stage-", 11.5, INK))
    s.append(_t(258, 285, "specifically. Partial", 11.5, INK))
    s.append(_t(258, 302, "resistance = rings survive.", 11.5, INK, "bold"))
    s.append(_t(44, 330, "The film counts the circulating fraction only.", 11.5, MUTED, style="italic"))

    # --- panel B: what is measured -----------------------------------------
    s.append(_t(430, 92, "B · WHAT IS MEASURED", 11, MUTED, "bold"))
    s.append(_box(430, 102, 330, 250, fill=PANEL))
    s.append(_t(446, 128, "Standard protocol", 13.5, INK, "bold"))
    s.append(_t(446, 150, "6-hourly blood films to 48 h", 12, MUTED))
    s.append(_t(446, 170, "counting error σ ≈ 0.20", 12, MUTED))
    s.append(_t(446, 196, "Reported phenotype", 13.5, INK, "bold"))
    s.append(_t(446, 218, "clearance half-life t₁₂ — the slope", 12, MUTED))
    s.append(_t(446, 236, "of the log-linear decline", 12, MUTED))
    hl = res["reference_half_life_h"]
    fold = res["confounded"].get("fold_range")
    s.append(_box(446, 254, 298, 76, fill="#fdeeea", stroke=BAD, rx=8, sw=1.8))
    s.append(_t(460, 278, f"t₁₂ = {hl:.1f} h is compatible with a", 12.5, INK, "bold"))
    s.append(_t(460, 298, f"{fold:.0f}-fold range of ring-stage killing,", 12.5, INK, "bold"))
    s.append(_t(460, 318, "once staging is allowed to vary.", 12.5, INK, "bold"))

    s.append(f'<line x1="400" y1="227" x2="424" y2="227" stroke="{INK}" stroke-width="2" marker-end="url(#a)"/>')
    s.append(f'<line x1="760" y1="227" x2="784" y2="227" stroke="{INK}" stroke-width="2" marker-end="url(#a)"/>')

    # --- panel C: the gate ---------------------------------------------------
    s.append(_t(790, 92, "C · EVIDENCE GATE", 11, MUTED, "bold"))
    s.append(_box(790, 102, 422, 250, fill=PANEL))
    s.append(_t(806, 128, "Is the parameter admissible?", 13.5, INK, "bold"))
    for i, (num, txt) in enumerate([("1", "structural — off the null space of S"),
                                    ("2", "practical — CV bound < 0.10"),
                                    ("3", "shape — profile two-sided at 95%")]):
        yy = 156 + i * 30
        s.append(f'<circle cx="818" cy="{yy - 4}" r="10" fill="{INK}"/>')
        s.append(_t(818, yy, num, 11, PAPER, "bold", "middle"))
        s.append(_t(836, yy, txt, 12, INK))
    s.append(_t(806, 262, "Same gate, same code as Thesis #3.", 11.5, MUTED, style="italic"))
    s.append(_t(806, 284, "The verdict belongs to the measurement", 11.5, MUTED, style="italic"))
    s.append(_t(806, 302, "design, not to the biology.", 11.5, MUTED, style="italic"))
    s.append(_t(806, 330, "No parameter is fitted to patient data.", 11.5, MUTED, style="italic"))

    # --- verdict strip -------------------------------------------------------
    s.append(_t(28, 400, "VERDICT — ring-stage killing rate k_ring, the parameter that defines artemisinin partial resistance",
                12, MUTED, "bold"))
    order = ["standard", "intensive", "stage", "stage_intensive", "idealised"]
    bw, gap = 222, 14
    for i, key in enumerate(order):
        g = gate[key]
        x = 28 + i * (bw + gap)
        cv = g["cv"]["k_ring"]
        ok = cv is not None and cv < 0.10
        col = OK if ok else BAD
        s.append(_box(x, 418, bw, 118, fill=PAPER, stroke=col, sw=2, rx=9))
        s.append(_t(x + 14, 442, g["short"], 11, INK, "bold"))
        s.append(_t(x + 14, 460, f"{g['n_obs']} observations · σ {g['sigma']:.2f}", 10.5, MUTED))
        s.append(_t(x + 14, 492, "CV  " + ("—" if cv is None else f"{cv:.2f}"), 20, col, "bold"))
        s.append(_t(x + 14, 516, "ADMISSIBLE" if ok else "REFUSED", 12.5, col, "bold"))
        n_open = sum(1 for v in g["status"].values() if v == "open")
        s.append(_t(x + bw - 14, 516, f"{n_open}/8 admissible", 10.5, MUTED, anchor="end"))

    s.append(_t(28, 572, "The curve determines when the infection started and how parasites sequester. It does not determine how well the drug kills rings.",
                13, INK, "bold"))
    s.append(_t(28, 596, "k_ring becomes admissible only in the idealised design, which needs total parasite biomass — not observable in a patient — and a counting precision light microscopy cannot reach.",
                12, MUTED))
    s.append(_t(28, 618, "Practical reading: treat the half-life as a population screening signal, and measure resistance with a ring-stage survival assay or kelch13 genotype.",
                12, MUTED))

    s.append(f'<line x1="28" y1="{H - 38}" x2="{W - 28}" y2="{H - 38}" stroke="{RULE}"/>')
    s.append(_t(28, H - 18, "Computational research on a mathematical model. Not a medical device, not clinical decision support, not treatment guidance.",
                11, MUTED, style="italic"))
    s.append("</svg>")
    return "".join(s)


def draw(results_path: Path, out_dir: Path):
    res = json.loads(Path(results_path).read_text())
    svg = build_svg(res)
    (out_dir / "fig1_overview.svg").write_text(svg)
    import cairosvg

    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(out_dir / "fig1_overview.png"),
                     output_width=W * 2, output_height=H * 2, background_color="white")
    return out_dir / "fig1_overview.png"
