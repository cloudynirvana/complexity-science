"""Fisher-information identifiability of the glucose-competition model.

A virtual experiment samples chosen observables at fixed times with multiplicative
(log-normal) noise. Sensitivities are taken with respect to log-parameters, so the
Cramer-Rao bound on log(theta_j) is approximately the coefficient of variation of
any unbiased estimate of theta_j. These are local, linearised bounds; profile
likelihoods check them where it matters.
"""
from __future__ import annotations

from dataclasses import asdict

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from .model import Params, rhs

PARAM_NAMES = tuple(asdict(Params()).keys())
STATE_INDEX = {"G": 0, "T": 1, "E": 2}


def initial_state(p: Params, T0: float = 0.05):
    # Glucose at supply level and effectors at their tumour-free baseline s/m.
    return [1.0, T0, p.s / p.m]


def observe(p: Params, times, observables, T0=0.05):
    sol = solve_ivp(rhs, (0, float(times[-1])), initial_state(p, T0), args=(p,),
                    t_eval=times, method="LSODA", rtol=1e-10, atol=1e-12)
    if not sol.success:
        raise RuntimeError(sol.message)
    return np.concatenate([np.log(np.maximum(sol.y[STATE_INDEX[o]], 1e-300)) for o in observables])


def sensitivity(p: Params, times, observables, names=PARAM_NAMES, rel=1e-4, T0=0.05):
    """d log(observation) / d log(theta), central differences.

    `T0` may be a sequence: each value is a separate experiment arm and the rows are stacked.
    """
    arms = np.atleast_1d(T0)
    cols = []
    for n in names:
        th = getattr(p, n)
        up = np.concatenate([observe(p.with_(**{n: th * np.exp(rel)}), times, observables, a) for a in arms])
        dn = np.concatenate([observe(p.with_(**{n: th * np.exp(-rel)}), times, observables, a) for a in arms])
        cols.append((up - dn) / (2 * rel))
    return np.column_stack(cols)


def fisher(p, times, observables, sigma=0.05, **kw):
    S = sensitivity(p, times, observables, **kw)
    return S.T @ S / sigma**2


def report(p, times, observables, sigma=0.05, names=PARAM_NAMES, cv_threshold=0.1, T0=0.05):
    S = sensitivity(p, times, observables, names=names, T0=T0)
    F = S.T @ S / sigma**2
    sv = np.linalg.svd(S / sigma, compute_uv=False)
    # Rank with a relative tolerance; a direction below it carries no usable information.
    tol = sv[0] * 1e-6
    rank = int(np.sum(sv > tol))
    cov = np.linalg.pinv(F, rcond=1e-12)
    cv = np.sqrt(np.clip(np.diag(cov), 0, None))
    if rank < len(names):
        # Parameters with weight on the null space are not identifiable at all.
        _, _, Vt = np.linalg.svd(S / sigma)
        null = Vt[rank:]
        load = np.sqrt((null**2).sum(axis=0))
        cv = np.where(load > 1e-3, np.inf, cv)
    return {
        "observables": list(observables),
        "n_obs": len(times) * len(observables) * len(np.atleast_1d(T0)),
        "rank": rank,
        "n_params": len(names),
        "singular_values": sv,
        "cv": dict(zip(names, cv)),
        "open": {n: bool(c < cv_threshold) for n, c in zip(names, cv)},
    }


CHI2_95_1DF = 3.841


def profile(p: Params, name, times, observables, sigma=0.05, grid=np.linspace(-1.5, 1.5, 13), T0=0.05):
    """Expected profile likelihood of log(theta_name) on noise-free synthetic data.

    Returns a list of (delta log theta, delta chi^2). Nuisance parameters are refitted
    in log space from the true values, so this is a local profile.
    """
    data = observe(p, times, observables, T0)
    free = [n for n in PARAM_NAMES if n != name]
    x0 = np.log([getattr(p, n) for n in free])
    out = []
    for dl in grid:
        fixed = {name: getattr(p, name) * float(np.exp(dl))}

        def resid(x):
            q = p.with_(**fixed, **{n: float(np.exp(v)) for n, v in zip(free, x)})
            try:
                return (observe(q, times, observables, T0) - data) / sigma
            except RuntimeError:
                return np.full(data.shape, 1e3)

        fit = least_squares(resid, x0, method="trf", max_nfev=400)
        out.append((float(dl), float(2 * fit.cost)))
    return out


def two_sided(prof, level=CHI2_95_1DF):
    """True if the profile crosses `level` on both sides of the optimum."""
    left = [c for d, c in prof if d < 0]
    right = [c for d, c in prof if d > 0]
    return bool(left and right and max(left) > level and max(right) > level)
