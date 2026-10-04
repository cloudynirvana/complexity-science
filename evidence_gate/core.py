"""Model-agnostic identifiability gate.

The caller supplies `observe(theta: dict) -> np.ndarray`, returning the
*log* of every observation the declared experiment would produce, stacked in a
fixed order. Everything here is then independent of the model: sensitivities are
taken with respect to log-parameters, so the Cramer-Rao bound on log(theta_j) is
approximately the coefficient of variation of theta_j.

A parameter is admissible only if it clears three tests, in order:

    1. structural — it is off the null space of the sensitivity matrix;
    2. practical  — its Cramer-Rao CV bound is below a stated threshold;
    3. shape      — its profile likelihood crosses the 95% level on both sides.

The verdict belongs to the declared experiment, not to the biology: the same
parameter can be admissible under one design and refused under another.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import least_squares

STRUCTURAL = "refused:structural"
PRACTICAL = "refused:practical"
ONE_SIDED = "refused:one_sided_profile"
OPEN = "open"
Verdict = str

CHI2_95_1DF = 3.841


def sensitivity(observe, theta: dict, names, rel=1e-4) -> np.ndarray:
    """d log(observation) / d log(theta), by central differences."""
    cols = []
    for n in names:
        up = dict(theta); up[n] = theta[n] * np.exp(rel)
        dn = dict(theta); dn[n] = theta[n] * np.exp(-rel)
        cols.append((np.asarray(observe(up)) - np.asarray(observe(dn))) / (2 * rel))
    return np.column_stack(cols)


def report(observe, theta: dict, names, sigma=0.05, cv_threshold=0.10, rel=1e-4) -> dict:
    S = sensitivity(observe, theta, names, rel) / sigma
    F = S.T @ S
    sv = np.linalg.svd(S, compute_uv=False)
    tol = sv[0] * 1e-6 if sv.size else 0.0
    rank = int(np.sum(sv > tol))
    cv = np.sqrt(np.clip(np.diag(np.linalg.pinv(F, rcond=1e-12)), 0, None))
    if rank < len(names):
        # A parameter loading on the null space is not determined at all.
        _, _, Vt = np.linalg.svd(S)
        load = np.sqrt((Vt[rank:] ** 2).sum(axis=0))
        cv = np.where(load > 1e-3, np.inf, cv)
    return {"rank": rank, "n_params": len(names), "singular_values": sv,
            "cv": dict(zip(names, cv)),
            "open": {n: bool(np.isfinite(c) and c < cv_threshold) for n, c in zip(names, cv)}}


def profile(observe, theta: dict, name, names, sigma=0.05, grid=None):
    """Expected profile likelihood of log(theta[name]) on noise-free synthetic data."""
    grid = np.linspace(-1.5, 1.5, 13) if grid is None else grid
    data = np.asarray(observe(theta))
    free = [n for n in names if n != name]
    x0 = np.log([theta[n] for n in free])
    out = []
    for dl in grid:
        fixed = {name: theta[name] * float(np.exp(dl))}

        def resid(x):
            q = dict(theta); q.update(fixed)
            q.update({n: float(np.exp(v)) for n, v in zip(free, x)})
            try:
                return (np.asarray(observe(q)) - data) / sigma
            except (RuntimeError, FloatingPointError, ValueError):
                return np.full(data.shape, 1e3)

        fit = least_squares(resid, x0, method="trf", max_nfev=400)
        out.append((float(dl), float(2 * fit.cost)))
    return out


def two_sided(prof, level=CHI2_95_1DF) -> bool:
    left = [c for d, c in prof if d < 0]
    right = [c for d, c in prof if d > 0]
    return bool(left and right and max(left) > level and max(right) > level)


@dataclass
class GateDecision:
    status: dict = field(default_factory=dict)
    cv: dict = field(default_factory=dict)
    rank: int = 0
    n_params: int = 0

    def opened(self):
        return sorted(k for k, v in self.status.items() if v == OPEN)


def decide(observe, theta: dict, names=None, sigma=0.05, cv_threshold=0.10,
           confirm_with_profile=True) -> GateDecision:
    names = list(theta) if names is None else list(names)
    r = report(observe, theta, names, sigma=sigma, cv_threshold=cv_threshold)
    dec = GateDecision(cv=dict(r["cv"]), rank=r["rank"], n_params=len(names))
    for n, cv in r["cv"].items():
        if not np.isfinite(cv):
            dec.status[n] = STRUCTURAL
        elif cv >= cv_threshold:
            dec.status[n] = PRACTICAL
        elif confirm_with_profile:
            dec.status[n] = OPEN if two_sided(profile(observe, theta, n, names, sigma)) else ONE_SIDED
        else:
            dec.status[n] = OPEN
    return dec
