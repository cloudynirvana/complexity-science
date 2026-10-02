"""Static figures for Thesis #3 (PDF manuscript). Colours follow a CVD-validated palette."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap  # noqa: E402

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3de"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
    "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "savefig.dpi": 200, "savefig.bbox": "tight",
})

LABELS = {"clearance": "clearance", "immune_held": "immune-held", "bistable": "bistable",
          "escape": "escape", "no_stable_eq": "no stable eq."}


def _regime_panel(ax, xs, ys, cells, colours, xlabel, ylabel, ref=None):
    order = list(colours)
    idx = np.array([[order.index(c) for c in row] for row in cells])
    cmap = ListedColormap([colours[k] for k in order])
    ax.pcolormesh(xs, ys, idx, cmap=cmap, norm=BoundaryNorm(np.arange(len(order) + 1) - 0.5, len(order)),
                  shading="nearest", edgecolors="none")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    for k in set(c for row in cells for c in row):
        ii, jj = np.where(idx == order.index(k))
        ax.text(np.exp(np.mean(np.log(np.asarray(xs)[jj]))), np.exp(np.mean(np.log(np.asarray(ys)[ii]))),
                LABELS[k], ha="center", va="center", fontsize=8, color=INK,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))
    if ref:
        ax.plot(*ref, marker="o", ms=6, mfc="white", mec=INK, mew=1.5)


def fig_regimes(res, out: Path, colours):
    rm = res["regime_maps"]; ref = res["reference"]
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.3))
    ax = axs[0]
    for row in res["u_continuation"]:
        for st in row["stable"]:
            ax.plot(row["u"], max(st["T"], 1e-4), "o", ms=3.5, color=S1 if st["branch"] == "immune_held" else S3)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("tumour glucose uptake u"); ax.set_ylabel("stable tumour burden T*")
    ax.axvline(ref["u"], color=GRID, lw=1, zorder=0)
    ax.text(0.04, 1.6, "immune-held branch", color=INK2, fontsize=8)
    ax.text(0.04, 30, "escape branch", color=INK2, fontsize=8)
    ax.set_title("a  Stable states along u")
    _regime_panel(axs[1], rm["u"], rm["h"], rm["u_h"], colours, "tumour glucose uptake u",
                  "effector fuel half-saturation h", (ref["u"], ref["h"]))
    axs[1].set_title("b  Regimes in (u, h)")
    _regime_panel(axs[2], rm["u"], rm["b"], rm["u_b"], colours, "tumour glucose uptake u",
                  "antigen-driven expansion b", (ref["u"], ref["b"]))
    axs[2].set_title("c  Regimes in (u, b)")
    fig.tight_layout(); fig.savefig(out / "fig1_regimes.png"); plt.close(fig)


def fig_basin(res, out: Path):
    b = res["basin"]
    idx = np.array([[0 if c == "immune_held" else 1 for c in row] for row in b["outcome"]])
    fig, ax = plt.subplots(figsize=(4.2, 3.4))
    ax.pcolormesh(b["T0"], b["E0"], idx, cmap=ListedColormap([S1, S3]), shading="nearest")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("initial tumour burden T0"); ax.set_ylabel("initial effector level E0")
    ax.axhline(res["tumour_free_state"]["E"], color="white", lw=1, ls="--")
    ax.text(b["T0"][1], res["tumour_free_state"]["E"] * 1.3, "naive baseline s/m", color="white", fontsize=7)
    ii, jj = np.where(idx == 0)
    if len(ii):
        ax.text(b["T0"][int(np.median(jj))], b["E0"][int(np.median(ii))], "immune-held", ha="center",
                fontsize=8, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.text(b["T0"][2], b["E0"][-4], "escape", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.set_title("Basin of immune control")
    fig.tight_layout(); fig.savefig(out / "fig2_basin.png"); plt.close(fig)


def fig_identifiability(res, out: Path):
    tab = res["identifiability"]["single_arm"]
    cols = list(tab); names = list(tab[cols[0]]["cv"])
    M = np.array([[tab[c]["cv"][n] if tab[c]["cv"][n] is not None else np.nan for c in cols] for n in names])
    L = np.log10(np.where(np.isnan(M), 1e3, M))
    fig, ax = plt.subplots(figsize=(5.2, 4.0))
    im = ax.imshow(L, cmap="Blues_r", vmin=-2, vmax=2.5, aspect="auto")
    for i, n in enumerate(names):
        for j, c in enumerate(cols):
            v = M[i, j]
            txt = "struct." if np.isnan(v) else (f"{v:.2f}" if v < 10 else f"{v:.0f}")
            opened = (not np.isnan(v)) and v < 0.10
            ax.text(j, i, txt + (" ✓" if opened else ""), ha="center", va="center", fontsize=8,
                    color="white" if (not np.isnan(v) and v < 0.3) else INK,
                    fontweight="bold" if opened else "normal")
    ax.set_xticks(range(len(cols)), ["{" + c + "}" for c in cols])
    ax.set_yticks(range(len(names)), names)
    ax.set_xlabel("observables measured"); ax.set_title("CV bound per parameter (✓ = gate opens, CV < 0.10)")
    cb = fig.colorbar(im, ax=ax, shrink=0.8); cb.set_label("log10 CV bound")
    for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout(); fig.savefig(out / "fig3_identifiability.png"); plt.close(fig)


def fig_scaling(res, out: Path):
    sc = res["identifiability"]["sample_scaling"]
    n = [r["n_times"] for r in sc]
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    for name, col in [("u", S1), ("b", S2), ("h", S3), ("k", S4)]:
        y = [r["cv"][name] for r in sc]
        ax.plot(n, y, "-o", color=col, lw=2, ms=4)
        ax.text(n[-1] * 1.12, y[-1], name, color=INK, va="center", fontsize=9)
    ax.axhline(0.10, color=INK2, ls="--", lw=1); ax.text(n[0], 0.108, "gate CV = 0.10", color=INK2, fontsize=8)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("sample times per observable (T, G, E measured)"); ax.set_ylabel("CV bound")
    ax.grid(True, color=GRID, lw=0.6); ax.set_title("Cost of opening the gate grows as 1/√n")
    fig.tight_layout(); fig.savefig(out / "fig5_scaling.png"); plt.close(fig)


def fig_profile(res, out: Path):
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    for key, col, lab in [("T", S2, "tumour burden only"), ("T,G,E", S1, "T, G and E")]:
        pr = res["profile_k"][key]
        ax.plot([p["dlog_k"] for p in pr], [p["chi2"] for p in pr], "-o", color=col, lw=2, ms=4)
        ax.text(pr[-1]["dlog_k"] + 0.05, pr[-1]["chi2"], lab, color=INK, fontsize=8, va="center")
    ax.axhline(3.84, color=INK2, ls="--", lw=1); ax.text(-1.5, 4.3, "95% threshold (χ²₁ = 3.84)", color=INK2, fontsize=8)
    ax.set_xlabel("Δ log k from true value"); ax.set_ylabel("profile Δχ²")
    ax.grid(True, color=GRID, lw=0.6); ax.set_title("Profile likelihood of kill rate k")
    ax.set_xlim(-1.6, 2.4)
    fig.tight_layout(); fig.savefig(out / "fig4_profile_k.png"); plt.close(fig)


def draw_all(res, out: Path):
    from .analysis import REGIME_COLOURS
    fig_regimes(res, out, REGIME_COLOURS)
    fig_basin(res, out)
    fig_identifiability(res, out)
    fig_scaling(res, out)
    fig_profile(res, out)
