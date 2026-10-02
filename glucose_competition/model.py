"""Minimal dimensionless tumour / effector-T-cell model with a shared glucose pool.

State (all dimensionless, non-negative):
    G  shared glucose
    T  tumour burden
    E  effector T cells

    dG/dt = 1 - G - (u * T + v * E) * G / (1 + G)
    dT/dt = T * (G / (1 + G) - d - k * E * G / (h + G))      # k term: kill needs fuel
    dE/dt = s + E * (b * G / (h + G) * T / (1 + T) - m)      # antigen-driven, fuel-gated

Glucose supply is scaled to 1. `u` is tumour glycolytic uptake, the competition
parameter. No value here is fitted to data or taken from a patient; the point of the
analysis is which *regimes* exist, not any number. Not a medical device.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve


@dataclass(frozen=True)
class Params:
    u: float = 2.0   # tumour glucose uptake (competition)
    v: float = 0.5   # effector glucose uptake
    d: float = 0.2   # tumour loss rate (growth is saturating G/(1+G) <= 1)
    k: float = 1.5   # kill rate, fuel-gated
    h: float = 0.5   # half-saturation of effector fuel use
    s: float = 0.02  # effector influx
    b: float = 1.2   # antigen-driven effector expansion
    m: float = 0.3   # effector loss

    def with_(self, **kw) -> "Params":
        return replace(self, **kw)


def rhs(_t, y, p: Params):
    G, T, E = y
    f = G / (1 + G)
    g = G / (p.h + G)
    return [
        1 - G - (p.u * T + p.v * E) * f,
        T * (f - p.d - p.k * E * g),
        p.s + E * (p.b * g * T / (1 + T) - p.m),
    ]


def simulate(p: Params, y0, t_end=400.0):
    sol = solve_ivp(rhs, (0, t_end), y0, args=(p,), method="LSODA",
                    rtol=1e-8, atol=1e-10)
    return sol


def endpoint(p: Params, y0, t_end=600.0):
    return np.maximum(simulate(p, y0, t_end).y[:, -1], 0.0)


def jacobian(y, p: Params, eps=1e-6):
    y = np.asarray(y, float)
    J = np.zeros((3, 3))
    for j in range(3):
        dy = np.zeros(3); dy[j] = eps * max(1.0, abs(y[j]))
        J[:, j] = (np.array(rhs(0, y + dy, p)) - np.array(rhs(0, y - dy, p))) / (2 * dy[j])
    return J


def steady_states(p: Params, n_starts=200, seed=0):
    """Distinct non-negative fixed points found from random starts, with stability."""
    rng = np.random.default_rng(seed)
    found = []
    for _ in range(n_starts):
        y0 = rng.uniform([0, 0, 0], [1.5, 6, 4])
        y, _info, ier, _ = fsolve(lambda z: rhs(0, z, p), y0, full_output=True, xtol=1e-12)
        if ier != 1 or np.any(y < -1e-9) or np.max(np.abs(rhs(0, y, p))) > 1e-8:
            continue
        y = np.maximum(y, 0.0)
        if not any(np.allclose(y, q[0], atol=1e-5) for q in found):
            ev = np.linalg.eigvals(jacobian(y, p))
            found.append((y, bool(np.all(ev.real < -1e-9)), ev))
    return sorted(found, key=lambda q: q[0][1])
