"""Figures for Thesis #4."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3de"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
RED = "#e34948"
plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
    "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "savefig.dpi": 200, "savefig.bbox": "tight",
})
PRETTY = {"k_ring": "$k_{ring}$", "k_mature": "$k_{mature}$", "ec50": "$EC_{50}$",
          "pmr": "PMR", "mu0": "$\\mu_0$", "sd0": "$\\sigma_0$", "a_seq": "$a_{seq}$",
          "ke": "$k_e$"}


def fig_curves(res, out: Path):
    c = res["curves"]; t = np.array(c["t"])
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    for name, col, lab in [("sensitive", S1, "full ring killing"),
                           ("reference", S4, "partial ring resistance"),
                           ("resistant", RED, "strong ring resistance")]:
        y = np.array(c[name]["log_circ"]) / np.log(10)
        ax.plot(t, y, color=col, lw=2.2)
        ax.text(t[-1] + 0.6, y[-1], f"{lab}\n$t_{{1/2}}$ = {c[name]['t_half']:.1f} h",
                color=INK, fontsize=8, va="center")
    ax.axhline(1.0, color=INK2, ls="--", lw=1)
    ax.text(0.5, 1.15, "microscopy detection limit", color=INK2, fontsize=8)
    ax.set_xlim(0, 62); ax.set_xticks(np.arange(0, 49, 12))
    ax.set_xlabel("hours after first dose"); ax.set_ylabel("log$_{10}$ circulating parasites/µL")
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_title("Clearance curves by ring-stage killing")
    fig.tight_layout(); fig.savefig(out / "fig2_curves.png"); plt.close(fig)


def fig_surface(res, out: Path):
    s = res["half_life_surface"]
    k = np.array(s["k_ring"]); mu = np.array(s["mu0"]); z = np.array(s["t_half"], dtype=float)
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    im = ax.pcolormesh(k, mu, z, cmap="BuPu", shading="nearest")
    cs = ax.contour(k, mu, z, levels=[2.0, 3.1, 4.0, 5.0], colors=INK, linewidths=1.1)
    ax.clabel(cs, fmt="%.1f h", fontsize=8)
    conf = res["confounded"]
    if conf.get("n_matches"):
        lo, hi = conf["lowest_k_ring"], conf["highest_k_ring"]
        ax.plot([lo["k_ring"], hi["k_ring"]], [lo["mu0"], hi["mu0"]], "o", ms=8,
                mfc="white", mec=RED, mew=2)
        ax.annotate("", xy=(hi["k_ring"], hi["mu0"]), xytext=(lo["k_ring"], lo["mu0"]),
                    arrowprops=dict(arrowstyle="<->", color=RED, lw=1.6))
        ax.text(0.022, 7.0, f"the same $t_{{1/2}}$ = {conf['target']} h\n"
                            f"spans a {conf['fold_range']:.0f}-fold range\n"
                            f"of ring-stage killing",
                color=RED, fontsize=8.5, fontweight="bold", va="top")
    ax.set_xscale("log")
    ax.set_xlabel("ring-stage killing rate $k_{ring}$ (/h)")
    ax.set_ylabel("mean parasite age at presentation $\\mu_0$ (h)")
    cb = fig.colorbar(im, ax=ax); cb.set_label("clearance half-life (h)")
    ax.set_title("One half-life, many biologies")
    fig.tight_layout(); fig.savefig(out / "fig3_surface.png"); plt.close(fig)


def fig_gate(res, out: Path):
    g = res["gate"]; keys = list(g); names = list(g[keys[0]]["cv"])
    M = np.array([[g[k]["cv"][n] if g[k]["cv"][n] is not None else np.nan for k in keys]
                  for n in names])
    L = np.log10(np.where(np.isnan(M), 1e3, M))
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    im = ax.imshow(L, cmap="Blues_r", vmin=-2, vmax=1.0, aspect="auto")
    for i in range(len(names)):
        for j in range(len(keys)):
            v = M[i, j]
            txt = "—" if np.isnan(v) else (f"{v:.2f}" if v < 10 else f"{v:.0f}")
            opened = (not np.isnan(v)) and v < 0.10
            ax.text(j, i, txt + (" ✓" if opened else ""), ha="center", va="center", fontsize=8,
                    color="white" if (not np.isnan(v) and v < 0.25) else INK,
                    fontweight="bold" if opened else "normal")
    ax.set_xticks(range(len(keys)), [k.replace("_", "\n") for k in keys], fontsize=8)
    ax.set_yticks(range(len(names)), [PRETTY[n] for n in names])
    ax.set_xlabel("measurement design")
    ax.set_title("CV bound per parameter (✓ = admissible, CV < 0.10)")
    cb = fig.colorbar(im, ax=ax, shrink=0.85); cb.set_label("log$_{10}$ CV bound")
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout(); fig.savefig(out / "fig4_gate.png"); plt.close(fig)


def fig_noise(res, out: Path):
    rows = res["noise_scaling"]
    sig = np.array([r["sigma"] for r in rows])
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    for key, col, lab in [("standard", S2, "standard"), ("intensive", S4, "intensive"),
                          ("stage", S3, "+ stage"), ("stage_intensive", S1, "+ stage, intensive")]:
        y = np.array([r[key] for r in rows], dtype=float)
        ax.plot(sig, y, "-o", color=col, lw=2, ms=4)
        ax.text(sig[0] * 0.93, y[0], lab, color=INK, fontsize=8, ha="left", va="center")
    ax.axhline(0.10, color=INK2, ls="--", lw=1)
    ax.text(0.095, 0.112, "gate threshold", color=INK2, fontsize=8, ha="center")
    ax.axvspan(0.15, 0.45, color=RED, alpha=0.10)
    ax.text(0.20, 0.035, "light microscopy\noperates here", color=RED, fontsize=8, fontweight="bold")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.invert_xaxis()
    ax.set_xlabel("counting error of a blood film (log-scale σ)")
    ax.set_ylabel("CV bound on $k_{ring}$")
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_title("What it would take to measure ring-stage killing")
    fig.tight_layout(); fig.savefig(out / "fig5_noise.png"); plt.close(fig)


def draw_all(res, out: Path):
    from .workflow_figure import draw as draw_workflow
    draw_workflow(out / "results.json", out)
    fig_curves(res, out)
    fig_surface(res, out)
    fig_gate(res, out)
    fig_noise(res, out)
