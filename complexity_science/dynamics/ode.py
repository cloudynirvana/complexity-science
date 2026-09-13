"""MHBD-4 right-hand side.

See ``docs/DYNAMICS.md`` for the documented equations. States are
``[B, I, X, E]``: burden, immune competence, toxicity, exposure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import NDArray

State = NDArray[np.float64]


@dataclass(frozen=True)
class HostBurdenParams:
    """Structural parameters of the untreated (or effector-modified) host."""

    r: float = 0.28
    k_capacity: float = 1.0
    alpha_i: float = 1.4
    alpha_x: float = 0.45
    h_x: float = 0.4
    k_clear: float = 0.55
    eps_i: float = 0.35
    h_i: float = 0.25
    sigma: float = 0.22
    i_star: float = 0.85
    gamma_b: float = 2.4
    delta_i: float = 0.08
    eta_x: float = 0.9
    chi_b: float = 0.12
    delta_x: float = 0.18
    # Effector-overridable PD knobs (defaults = untreated / no class loaded)
    k_el: float = 0.2
    immune_stim: float = 0.0
    immune_deplete: float = 0.0
    direct_clearance: float = 0.0
    growth_suppress: float = 0.0
    tox_direct: float = 0.0
    tox_immune: float = 0.0
    ec50_clearance: float = 0.3
    ec50_immune: float = 0.3

    def with_updates(self, **kwargs: float) -> HostBurdenParams:
        data = self.__dict__.copy()
        data.update(kwargs)
        return HostBurdenParams(**data)


def _hill(value: float, ec50: float) -> float:
    value = max(float(value), 0.0)
    return value / (value + max(ec50, 1e-9))


def mhbd4_rhs(
    params: HostBurdenParams,
    infusion: Callable[[float], float],
) -> Callable[[float, State], State]:
    """Return ``f(t, y)`` for ``solve_ivp``."""

    def f(t: float, y: State) -> State:
        b, immune, tox, exposure = (max(float(v), 0.0) for v in y)
        u = max(float(infusion(t)), 0.0)
        growth = (
            params.r
            * b
            * (1.0 - b / max(params.k_capacity, 1e-9))
            * (1.0 / (1.0 + params.alpha_i * immune))
            * (1.0 + params.alpha_x * tox / (tox + params.h_x))
            * (1.0 / (1.0 + params.growth_suppress * exposure))
        )
        clearance = (
            params.k_clear
            * (
                params.direct_clearance * _hill(exposure, params.ec50_clearance)
                + params.eps_i * _hill(immune, params.h_i)
            )
            * b
        )
        d_b = growth - clearance
        d_i = (
            params.sigma * (params.i_star - immune) / (1.0 + params.gamma_b * b)
            - params.delta_i * immune * (1.0 + params.eta_x * tox)
            + params.immune_stim * _hill(exposure, params.ec50_immune)
            - params.immune_deplete * exposure * immune
        )
        d_x = (
            params.tox_direct * exposure
            + params.chi_b * b
            + params.tox_immune * (immune * exposure) / (1.0 + immune)
            - params.delta_x * tox
        )
        d_e = -params.k_el * exposure + u
        return np.array([d_b, d_i, d_x, d_e], dtype=float)

    return f
