"""Regenerate every number and figure in Thesis #4.

    python -m malaria_clearance.analysis

Deterministic: fixed grids, fixed designs. Takes a few minutes.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from evidence_gate.core import decide, profile, report
from .model import Params, clearance_half_life, observables

OUT = Path(__file__).resolve().parents[1] / "docs" / "manuscript" / "thesis_04_figures"

# Reference phenotype: partial ring-stage resistance on a background of full
# mature-stage killing. Chosen so the clearance half-life (3.1 h) sits inside the
# published range, NOT fitted to any patient data.
REFERENCE = Params(k_ring=0.25, k_mature=1.0, ec50=0.1, ke=0.35)
NAMES = list(REFERENCE.as_dict())

# sigma is the multiplicative counting error of a blood film on the log scale.
# 0.20 is generous for light microscopy; 0.05 is better than any field laboratory.
SIGMA_FIELD = 0.20
SIGMA_IDEAL = 0.05
GATE_CV = 0.10

DESIGNS = [
    ("standard", ("circ",), 6, 48, SIGMA_FIELD, "6-hourly films to 48 h",
     "the routine therapeutic-efficacy protocol"),
    ("intensive", ("circ",), 4, 72, SIGMA_FIELD, "4-hourly films to 72 h",
     "denser and longer sampling of the same observable"),
    ("stage", ("circ", "stage"), 6, 48, SIGMA_FIELD, "6-hourly films + stage",
     "routine sampling plus ring/trophozoite composition"),
    ("stage_intensive", ("circ", "stage"), 4, 72, SIGMA_FIELD, "4-hourly + stage, 72 h",
     "the best design a microscopy-only study could run"),
    ("idealised", ("circ", "stage", "total"), 2, 96, SIGMA_IDEAL, "2-hourly + biomass, \u03c3 5%",
     "adds total biomass, which is not observable in a patient"),
]


def observer(which, step, hours):
    ts = np.arange(0, hours + 1, step)
    return (lambda th: observables(Params(**th), ts, which, hours=hours)), ts


def gate_table():
    out = {}
    for key, which, step, hours, sigma, short, label in DESIGNS:
        obs, ts = observer(which, step, hours)
        d = decide(obs, REFERENCE.as_dict(), NAMES, sigma=sigma, confirm_with_profile=False)
        out[key] = {"label": label, "short": short, "observables": list(which), "step_h": step,
                    "hours": hours, "sigma": sigma, "n_obs": len(ts) * len(which),
                    "rank": d.rank, "cv": {k: _f(v) for k, v in d.cv.items()},
                    "status": d.status}
    return out


def noise_scaling():
    rows = []
    for sigma in [0.40, 0.30, 0.20, 0.15, 0.10, 0.07, 0.05, 0.03, 0.02, 0.01]:
        row = {"sigma": sigma}
        for key, which, step, hours, _s, _sh, _l in DESIGNS[:4]:
            obs, _ = observer(which, step, hours)
            r = report(obs, REFERENCE.as_dict(), NAMES, sigma=sigma)
            row[key] = _f(r["cv"]["k_ring"])
        rows.append(row)
    return rows


def half_life_surface():
    """Clearance half-life over ring-stage killing and infection staging."""
    k = np.logspace(np.log10(0.02), np.log10(1.0), 28)
    mu = np.linspace(2.0, 26.0, 25)
    z = [[clearance_half_life(REFERENCE.with_(k_ring=float(kk), mu0=float(mm))) for kk in k]
         for mm in mu]
    return {"k_ring": k.tolist(), "mu0": mu.tolist(), "t_half": z}


def confounded_pair(target=3.1, tol=0.05):
    """Two parameter sets with near-identical half-life but very different biology."""
    found = []
    for mu in np.linspace(2, 26, 49):
        for kk in np.logspace(np.log10(0.02), np.log10(1.0), 60):
            p = REFERENCE.with_(k_ring=float(kk), mu0=float(mu))
            t = clearance_half_life(p)
            if np.isfinite(t) and abs(t - target) < tol:
                found.append({"k_ring": float(kk), "mu0": float(mu), "t_half": float(t)})
    if not found:
        return {"target": target, "matches": []}
    lo = min(found, key=lambda d: d["k_ring"])
    hi = max(found, key=lambda d: d["k_ring"])
    return {"target": target, "n_matches": len(found), "lowest_k_ring": lo, "highest_k_ring": hi,
            "fold_range": hi["k_ring"] / lo["k_ring"]}


def curves():
    ts = np.arange(0, 49, 1)
    out = {"t": ts.tolist()}
    for name, p in [("sensitive", REFERENCE.with_(k_ring=1.0)),
                    ("reference", REFERENCE),
                    ("resistant", REFERENCE.with_(k_ring=0.05))]:
        out[name] = {"log_circ": observables(p, ts, ("circ",)).tolist(),
                     "t_half": _f(clearance_half_life(p)), "k_ring": p.k_ring}
    return out


def profile_k_ring():
    out = {}
    for key in ("standard", "stage_intensive"):
        spec = next(d for d in DESIGNS if d[0] == key)
        obs, _ = observer(spec[1], spec[2], spec[3])
        pr = profile(obs, REFERENCE.as_dict(), "k_ring", NAMES, sigma=spec[4])
        out[key] = [{"dlog_k_ring": d, "chi2": c} for d, c in pr]
    return out


def _f(v):
    v = float(v)
    return None if not np.isfinite(v) else v


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {
        "reference": REFERENCE.as_dict(),
        "reference_half_life_h": _f(clearance_half_life(REFERENCE)),
        "sensitive_half_life_h": _f(clearance_half_life(REFERENCE.with_(k_ring=1.0))),
        "resistant_half_life_h": _f(clearance_half_life(REFERENCE.with_(k_ring=0.05))),
        "gate": gate_table(),
        "noise_scaling": noise_scaling(),
        "half_life_surface": half_life_surface(),
        "confounded": confounded_pair(),
        "curves": curves(),
        "profile_k_ring": profile_k_ring(),
    }
    (OUT / "results.json").write_text(json.dumps(res, indent=1))
    from .figures import draw_all
    draw_all(res, OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
