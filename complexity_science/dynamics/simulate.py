"""Integrate MHBD-4 and summarise trajectories."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from complexity_science.dynamics.ode import HostBurdenParams, mhbd4_rhs

State = NDArray[np.float64]


@dataclass(frozen=True)
class Schedule:
    kind: str  # "continuous" | "pulsed"
    period_days: float = 7.0
    duty: float = 0.35
    intensity: float = 0.8

    def infusion(self) -> Callable[[float], float]:
        intensity = float(self.intensity)
        if self.kind == "continuous":
            return lambda _t: intensity

        period = max(float(self.period_days), 1e-6)
        on_for = max(min(float(self.duty), 1.0), 0.0) * period

        def u(t: float) -> float:
            phase = float(t) % period
            return intensity if phase < on_for else 0.0

        return u

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "period_days": self.period_days,
            "duty": self.duty,
            "intensity": self.intensity,
        }


@dataclass
class Trajectory:
    t: NDArray[np.float64]
    y: NDArray[np.float64]
    success: bool
    message: str

    @property
    def b(self) -> NDArray[np.float64]:
        return self.y[0]

    @property
    def immune(self) -> NDArray[np.float64]:
        return self.y[1]

    @property
    def tox(self) -> NDArray[np.float64]:
        return self.y[2]

    @property
    def exposure(self) -> NDArray[np.float64]:
        return self.y[3]

    def metrics(self) -> dict[str, float]:
        if self.t.size == 0:
            return {
                "b_final": float("nan"),
                "i_final": float("nan"),
                "x_peak": float("nan"),
                "x_mean": float("nan"),
                "b_mean": float("nan"),
                "e_auc": float("nan"),
            }
        dt = np.gradient(self.t)
        return {
            "b_final": float(self.b[-1]),
            "i_final": float(self.immune[-1]),
            "x_peak": float(np.max(self.tox)),
            "x_mean": float(np.mean(self.tox)),
            "b_mean": float(np.mean(self.b)),
            "e_auc": float(np.sum(self.exposure * dt)),
        }

    def downsample(self, max_points: int = 25) -> dict[str, list[float]]:
        n = self.t.size
        if n == 0:
            return {"t": [], "B": [], "I": [], "X": [], "E": []}
        idx = np.linspace(0, n - 1, num=min(max_points, n), dtype=int)
        return {
            "t": [float(self.t[i]) for i in idx],
            "B": [float(self.b[i]) for i in idx],
            "I": [float(self.immune[i]) for i in idx],
            "X": [float(self.tox[i]) for i in idx],
            "E": [float(self.exposure[i]) for i in idx],
        }


def simulate(
    params: HostBurdenParams,
    y0: tuple[float, float, float, float],
    *,
    horizon_days: float = 42.0,
    schedule: Schedule | None = None,
    n_eval: int = 241,
) -> Trajectory:
    """Integrate on ``[0, horizon_days]``. Reject non-finite runs."""
    schedule = schedule or Schedule(kind="continuous", intensity=0.0)
    rhs = mhbd4_rhs(params, schedule.infusion())
    t_span = (0.0, float(horizon_days))
    t_eval = np.linspace(t_span[0], t_span[1], num=max(int(n_eval), 5))
    max_step = 0.25 if schedule.kind == "pulsed" else 1.0
    try:
        sol = solve_ivp(
            rhs,
            t_span,
            y0=np.array(y0, dtype=float),
            t_eval=t_eval,
            method="RK45",
            rtol=1e-6,
            atol=1e-8,
            max_step=max_step,
            dense_output=False,
        )
    except Exception as exc:  # noqa: BLE001 — surface as failed trajectory
        return Trajectory(
            t=np.array([]),
            y=np.zeros((4, 0)),
            success=False,
            message=f"integrator_exception:{exc}",
        )
    y = np.maximum(sol.y, 0.0)
    finite = bool(sol.success) and bool(np.all(np.isfinite(y)))
    if finite and np.max(y) > 50.0:
        finite = False
        message = "left_finite_box"
    else:
        message = sol.message
    return Trajectory(t=sol.t, y=y, success=finite, message=str(message))
