"""Workflow schematic for the evidence gate, drawn as SVG and rendered to PNG.

The verdict panel on the right is read from `results.json`, so the figure cannot
drift from the computed results. Run via `python -m glucose_competition.analysis`,
or directly:

    python -m glucose_competition.workflow_figure
"""
from __future__ import annotations

import json
from pathlib import Path

INK, MUTED, RULE, PAPER = "#0b0b0b", "#52514e", "#d6d5d0", "#ffffff"
PANEL = "#f6f6f4"
# Verdict colours: validated categorical slots. Every chip also carries a letter
# code, so identity is never conveyed by colour alone.
VERDICT = {
    "refused:structural": ("#e34948", "S", "structurally invisible"),
    "refused:practical": ("#eb6834", "P", "bound too wide"),
    "refused:one_sided_profile": ("#eda100", "1", "one-sided interval"),
    "open": ("#1baf7a", "O", "admissible"),
}
PARAMS = ["u", "v", "d", "k", "h", "s", "b", "m"]
PARAM_LABEL = {
    "u": "u  tumour glucose uptake",
    "v": "v  effector glucose uptake",
    "d": "d  tumour loss",
    "k": "k  effector kill rate",
    "h": "h  effector fuel half-sat.",
    "s": "s  effector influx",
    "b": "b  antigen-driven expansion",
    "m": "m  effector loss",
}

W, H = 1240, 700
SANS = "DejaVu Sans, Liberation Sans, sans-serif"


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _text(x, y, s, size=13, fill=INK, weight="normal", anchor="start", style=""):
    extra = f' font-style="{style}"' if style else ""
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{extra}>{_esc(s)}</text>')


def _box(x, y, w, h, fill=PAPER, stroke=RULE, rx=7, sw=1.4):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def _arrow(x1, y1, x2, y2, stroke=INK, sw=1.8, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}" marker-end="url(#a)"{d}/>')


def _gate(x, y, w, h, n, title, question, detail):
    """One test in the pipeline: numbered badge, question, and the quantity tested."""
    out = [_box(x, y, w, h, fill=PAPER, stroke=INK, sw=1.6)]
    out += [f'<circle cx="{x + 24}" cy="{y + 25}" r="13" fill="{INK}"/>',
            _text(x + 24, y + 30, str(n), 13, PAPER, "bold", "middle")]
    out += [_text(x + 46, y + 23, title, 11.5, MUTED, "bold"),
            _text(x + 46, y + 42, question, 14, INK, "bold"),
            _text(x + 46, y + 63, detail, 12, MUTED, style="italic")]
    return "".join(out)


def _chip(x, y, key, label):
    colour, code, _ = VERDICT[key]
    return "".join([
        _box(x, y, 152, 34, fill=PAPER, stroke=colour, rx=17, sw=1.8),
        f'<circle cx="{x + 19}" cy="{y + 17}" r="11" fill="{colour}"/>',
        _text(x + 19, y + 22, code, 12, PAPER, "bold", "middle"),
        _text(x + 37, y + 22, label, 12.5, INK, "bold"),
    ])


def build_svg(gate: dict) -> str:
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="{SANS}">',
         f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
         f'markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/>'
         '</marker></defs>']

    s.append(_text(28, 34, "The evidence gate: from a declared measurement to an admissible parameter", 17, INK, "bold"))
    s.append(_text(28, 56, "A parameter leaves “refused” only for a stated experiment. Change the observables and the verdict changes.",
                   12.5, MUTED))

    # ---- inputs -------------------------------------------------------------
    s.append(_text(28, 92, "INPUTS", 11, MUTED, "bold"))
    s.append(_box(28, 102, 262, 92, fill=PANEL))
    s.append(_text(44, 126, "Mechanistic model", 13.5, INK, "bold"))
    s.append(_text(44, 148, "dG/dt, dT/dt, dE/dt", 12, MUTED))
    s.append(_text(44, 168, "parameter vector θ  (8 entries)", 12, MUTED))
    s.append(_text(44, 186, "no value fitted to data", 11.5, MUTED, style="italic"))

    s.append(_box(28, 212, 262, 112, fill=PANEL))
    s.append(_text(44, 236, "Declared experiment", 13.5, INK, "bold"))
    s.append(_text(44, 258, "observables ⊆ {T, G, E}", 12, MUTED))
    s.append(_text(44, 278, "sample times · noise σ · seeding arms", 12, MUTED))
    s.append(_text(44, 300, "declared up front, not after the fit", 11.5, MUTED, style="italic"))

    s.append(_text(44, 352, "Sensitivity matrix", 13, INK, "bold"))
    s.append(_text(44, 372, "S = ∂ log y / ∂ log θ", 12.5, MUTED))
    s.append(_text(44, 392, "F = SᵀS / σ²", 12.5, MUTED))

    s.append(_arrow(159, 194, 159, 208))
    s.append(_arrow(159, 324, 159, 334))
    s.append(_arrow(290, 372, 320, 372, sw=2))

    # ---- the three tests ----------------------------------------------------
    gx, gw = 330, 300
    s.append(_text(330, 92, "THE GATE  — all three must pass", 11, MUTED, "bold"))
    s.append(_gate(gx, 102, gw, 82, 1, "STRUCTURAL",
                   "Is θⱼ off the null space of S?",
                   "a symmetry no sample size can break"))
    s.append(_gate(gx, 212, gw, 82, 2, "PRACTICAL",
                   "Is CV = √(F⁻¹)ⱼⱼ < 0.10?",
                   "Cramér–Rao bound at the declared σ"))
    s.append(_gate(gx, 322, gw, 82, 3, "SHAPE",
                   "Does Δχ² cross 3.84 both sides?",
                   "profile likelihood, not a local bound"))

    for y0 in (184, 294, 404):
        s.append(_arrow(gx + gw / 2, y0, gx + gw / 2, y0 + 26))
        s.append(_text(gx + gw / 2 + 8, y0 + 20, "pass", 11, MUTED, style="italic"))

    s.append(_box(gx + 52, 430, 226, 44, fill="#eafaf3", stroke=VERDICT["open"][0], rx=10, sw=2))
    s.append(_text(gx + 165, 458, "ADMISSIBLE PARAMETER", 14, INK, "bold", "middle"))
    s.append(_text(gx + 165, 500, "May now be estimated — for this experiment only.", 12, MUTED, "middle"))
    s.append(_text(gx + 165, 520, "Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction",
                   11.5, INK, "bold", "middle"))

    # fail branches
    for y0, key, label in ((143, "refused:structural", "structural"),
                           (253, "refused:practical", "practical"),
                           (363, "refused:one_sided_profile", "one-sided")):
        s.append(_arrow(gx + gw, y0, gx + gw + 36, y0, stroke=MUTED))
        s.append(_text(gx + gw + 4, y0 - 8, "fail", 11, MUTED, style="italic"))
        s.append(_chip(gx + gw + 40, y0 - 17, key, label))

    # ---- worked verdicts ----------------------------------------------------
    px, py = 848, 452
    s.append(_text(px, 92, "WORKED VERDICT — tumour / effector / glucose model", 11, MUTED, "bold"))
    s.append(_box(px, py - 350, 392, 300, fill=PANEL, stroke=RULE))
    s.append(_text(px + 196, py - 326, "What each measurement set admits", 13, INK, "bold", "middle"))
    cx1, cx2 = px + 268, px + 334
    s.append(_text(cx1, py - 303, "{T}", 12, INK, "bold", "middle"))
    s.append(_text(cx2, py - 303, "{T,G,E}", 12, INK, "bold", "middle"))
    s.append(_text(px + 16, py - 303, "measured:", 11.5, MUTED))

    for i, p in enumerate(PARAMS):
        yy = py - 288 + i * 29
        if i % 2 == 0:
            s.append(f'<rect x="{px + 10}" y="{yy}" width="372" height="27" rx="4" fill="{PAPER}"/>')
        s.append(_text(px + 20, yy + 19, PARAM_LABEL[p], 12, INK))
        for cx, obs in ((cx1, "T"), (cx2, "T,G,E")):
            colour, code, _ = VERDICT[gate[obs][p]]
            s.append(f'<rect x="{cx - 11}" y="{yy + 4}" width="22" height="19" rx="4" fill="{colour}"/>')
            s.append(_text(cx, yy + 19, code, 11.5, PAPER, "bold", "middle"))

    n_open = sum(1 for p in PARAMS if gate["T,G,E"][p] == "open")
    for i, line in enumerate(["Tumour counts alone admit nothing. Measuring glucose",
                              f"and effectors admits {n_open} of 8."]):
        s.append(_text(px, 430 + i * 19, line, 12, INK))
    for i, line in enumerate(["The kill rate k is refused in every design \u2014",
                              "the parameter most often fitted in practice."]):
        s.append(_text(px, 474 + i * 19, line, 12, INK, "bold"))

    s.append(_text(px, 528, "VERDICTS", 11, MUTED, "bold"))
    for i, (key, (colour, code, meaning)) in enumerate(VERDICT.items()):
        yy = 540 + i * 24
        s.append(f'<rect x="{px}" y="{yy}" width="22" height="19" rx="4" fill="{colour}"/>')
        s.append(_text(px + 11, yy + 14, code, 11.5, PAPER, "bold", "middle"))
        s.append(_text(px + 32, yy + 14, f"{key.split(':')[-1].replace('_', ' ')} \u2014 {meaning}", 12, INK))

    s.append(f'<line x1="28" y1="{H - 38}" x2="{W - 28}" y2="{H - 38}" stroke="{RULE}" stroke-width="1"/>')
    s.append(_text(28, H - 18,
                   "Computational research only. Not a medical device, not clinical decision support, not dosing advice.",
                   11, MUTED, style="italic"))
    s.append("</svg>")
    return "".join(s)


def draw(results_path: Path, out_dir: Path):
    gate = json.loads(Path(results_path).read_text())["gate"]
    svg = build_svg(gate)
    (out_dir / "fig1_workflow.svg").write_text(svg)
    import cairosvg

    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(out_dir / "fig1_workflow.png"),
                     output_width=W * 2, output_height=H * 2, background_color="white")
    return out_dir / "fig1_workflow.png"


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "docs" / "manuscript" / "thesis_03_figures"
    print("wrote", draw(out / "results.json", out))
