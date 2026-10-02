"""Regime classification from equilibria and their Jacobian spectra.

Regimes (stable equilibria only; T > 0 means tumour present):
    clearance      single stable state with T = 0
    immune_held    single stable state with low T and effectors above influx level
    escape         single stable state with effectors near influx level
    bistable       two or more stable states
    no_stable_eq   no stable equilibrium (candidate sustained oscillation; confirm by simulation)
"""
from __future__ import annotations

import numpy as np

from .model import Params, steady_states


def tumour_free_state(p: Params):
    """Closed form for the T = 0 equilibrium and the tumour invasion exponent."""
    E = p.s / p.m
    G = (-p.v * E + np.sqrt((p.v * E) ** 2 + 4)) / 2  # root of G^2 + vE G - 1 = 0
    invasion = G / (1 + G) - p.d - p.k * E * G / (p.h + G)
    return G, E, invasion


def classify(p: Params, n_starts: int = 120, seed: int = 0) -> str:
    stable = [y for y, ok, _ in steady_states(p, n_starts=n_starts, seed=seed) if ok]
    if not stable:
        return "no_stable_eq"
    if len(stable) >= 2:
        return "bistable"
    G, T, E = stable[0]
    if T < 1e-6:
        return "clearance"
    return "immune_held" if E > 2 * p.s / p.m else "escape"


def grid(base: Params, xname: str, xs, yname: str, ys, **kw):
    return [[classify(base.with_(**{xname: x, yname: y}), **kw) for x in xs] for y in ys]
