"""Regenerate every number and figure in Thesis #3.

    python -m glucose_competition.analysis            # writes docs/manuscript/thesis_03_figures/ and results.json

Deterministic: fixed seeds, fixed grids. Takes a few minutes on a laptop.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from .gate import Experiment, decide
from .identifiability import observe, profile, report
from .model import Params, simulate
from .regimes import classify, tumour_free_state

OUT = Path(__file__).resolve().parents[1] / "docs" / "manuscript" / "thesis_03_figures"

# Reference parameter set: found by the random regime sweep (regime_sweep.py) as the
# one draw with two stable states. Dimensionless; not fitted to any data.
REFERENCE = Params(u=0.685, v=0.0886, d=0.0958, k=2.893, h=1.584, s=0.0011, b=6.288, m=0.894)
TIMES = np.linspace(2, 60, 20)
OBS_SETS = [("T",), ("T", "G"), ("T", "E"), ("T", "G", "E")]
SIGMA = 0.05
GATE_CV = 0.10

REGIME_ORDER = ["clearance", "immune_held", "bistable", "escape", "no_stable_eq"]
# Validated categorical slots 1-3 (all-pairs safe) + neutral grey for clearance.
REGIME_COLOURS = {"immune_held": "#2a78d6", "bistable": "#eb6834", "escape": "#1baf7a",
                  "clearance": "#c9c8c2", "no_stable_eq": "#52514e"}


def regime_maps():
    us = np.logspace(np.log10(0.03), 1, 36)
    hs = np.logspace(np.log10(0.2), np.log10(6), 30)
    bs = np.logspace(0, np.log10(20), 30)
    uh = [[classify(REFERENCE.with_(u=u, h=h), n_starts=80) for u in us] for h in hs]
    ub = [[classify(REFERENCE.with_(u=u, b=b), n_starts=80) for u in us] for b in bs]
    return {"u": us.tolist(), "h": hs.tolist(), "b": bs.tolist(), "u_h": uh, "u_b": ub}


def u_continuation():
    """Stable tumour burdens along u at the reference point."""
    from .model import steady_states
    rows = []
    for u in np.logspace(np.log10(0.03), 1, 60):
        p = REFERENCE.with_(u=u)
        st = [y for y, ok, _ in steady_states(p, n_starts=150) if ok]
        rows.append({"u": float(u), "stable": [
            {"T": float(y[1]), "E": float(y[2]), "branch": "immune_held" if y[2] > 2 * p.s / p.m else "escape"}
            for y in sorted(st, key=lambda y: y[1])]})
    return rows


def basin_map():
    T0s = np.logspace(-2, 1.3, 40)
    E0s = np.logspace(-3, 0.5, 40)
    out = []
    for E0 in E0s:
        row = []
        for T0 in T0s:
            E_end = simulate(REFERENCE, [1.0, T0, E0], 500).y[2, -1]
            row.append("immune_held" if E_end > 2 * REFERENCE.s / REFERENCE.m else "escape")
        out.append(row)
    return {"T0": T0s.tolist(), "E0": E0s.tolist(), "outcome": out}


def identifiability_tables():
    single = {",".join(o): _clean(report(REFERENCE, TIMES, o, sigma=SIGMA, cv_threshold=GATE_CV))
              for o in OBS_SETS}
    arms = {",".join(o): _clean(report(REFERENCE, TIMES, o, sigma=SIGMA, cv_threshold=GATE_CV,
                                       T0=[0.05, 1.0, 20.0])) for o in OBS_SETS}
    scaling = []
    for n in [10, 20, 40, 80, 160, 320, 640]:
        r = report(REFERENCE, np.linspace(2, 60, n), ("T", "G", "E"), sigma=SIGMA)
        scaling.append({"n_times": n, "cv": {k: _f(v) for k, v in r["cv"].items()}})
    return {"single_arm": single, "three_arms": arms, "sample_scaling": scaling}


def symmetry_check(c=3.0):
    """Exact scaling symmetry under tumour-only observation: E->cE, v->v/c, k->k/c, s->cs."""
    p2 = REFERENCE.with_(v=REFERENCE.v / c, k=REFERENCE.k / c, s=REFERENCE.s * c)
    a = observe(REFERENCE, TIMES, ("T",))
    b = observe(p2, TIMES, ("T",))
    e1 = observe(REFERENCE, TIMES, ("E",))
    e2 = observe(p2, TIMES, ("E",))
    return {"c": c, "max_abs_dlogT": float(np.max(np.abs(a - b))),
            "max_abs_dlogE_minus_logc": float(np.max(np.abs(e2 - e1 - np.log(c))))}


def profile_k(observables):
    """Expected profile likelihood of log k (noise-free synthetic data)."""
    return [{"dlog_k": d, "chi2": c} for d, c in profile(REFERENCE, "k", TIMES, observables, sigma=SIGMA)]


def gate_decisions():
    out = {}
    for obs in OBS_SETS:
        dec = decide(REFERENCE, Experiment(obs, tuple(TIMES), SIGMA), cv_threshold=GATE_CV)
        out[",".join(obs)] = dec.status
    return out


def _f(v):
    return None if not np.isfinite(v) else float(v)


def _clean(r):
    return {"rank": r["rank"], "n_params": r["n_params"], "n_obs": r["n_obs"],
            "singular_values": [float(s) for s in r["singular_values"]],
            "cv": {k: _f(v) for k, v in r["cv"].items()}, "open": r["open"]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    G0, E0, lam = tumour_free_state(REFERENCE)
    res = {
        "reference": REFERENCE.__dict__,
        "tumour_free_state": {"G": G0, "E": E0, "invasion_exponent": lam},
        "reference_regime": classify(REFERENCE, n_starts=200),
        "symmetry": symmetry_check(),
        "identifiability": identifiability_tables(),
        "profile_k": {"T": profile_k(("T",)), "T,G,E": profile_k(("T", "G", "E"))},
        "gate": gate_decisions(),
        "u_continuation": u_continuation(),
        "regime_maps": regime_maps(),
        "basin": basin_map(),
    }
    (OUT / "results.json").write_text(json.dumps(res, indent=1))
    from .figures import draw_all
    draw_all(res, OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
