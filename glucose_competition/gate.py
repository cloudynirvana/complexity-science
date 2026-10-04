"""Evidence-gate decision for one model and one declared experiment.

Thesis #2 keeps the gate closed for every CaseCard. This module states the condition
under which a single parameter of a specified mechanistic model may leave the
`refused` state:

    1. it is structurally identifiable from the declared observables (Fisher rank test);
    2. its Cramer-Rao CV bound is below `cv_threshold` at the declared noise and sampling;
    3. its expected profile likelihood crosses the 95% threshold on both sides.

Passing all three gives `open`. The decision is about the experiment, not about the
biology: the same parameter can be open under one design and refused under another.
Nothing here emits a dose, a schedule, or a prediction for a person.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .identifiability import observe as observe_states
from .model import Params

from evidence_gate.core import ONE_SIDED, OPEN, PRACTICAL, STRUCTURAL  # noqa: F401
from evidence_gate.core import GateDecision as _CoreDecision
from evidence_gate.core import decide as _core_decide

from .identifiability import PARAM_NAMES


@dataclass(frozen=True)
class Experiment:
    observables: tuple[str, ...]
    times: tuple[float, ...]
    sigma: float = 0.05
    arms_T0: tuple[float, ...] = (0.05,)


@dataclass
class GateDecision:
    experiment: Experiment
    status: dict[str, str] = field(default_factory=dict)
    cv: dict[str, float] = field(default_factory=dict)
    rank: int = 0

    def opened(self):
        return sorted(k for k, v in self.status.items() if v == OPEN)


def decide(p: Params, exp: Experiment, cv_threshold=0.10, confirm_with_profile=True) -> GateDecision:
    """Apply the shared evidence gate to this model under a declared experiment."""
    t = np.asarray(exp.times, float)
    arms = list(exp.arms_T0)

    def observe(theta: dict) -> np.ndarray:
        q = Params(**theta)
        return np.concatenate([observe_states(q, t, exp.observables, a) for a in arms])

    core: _CoreDecision = _core_decide(observe, p.__dict__, PARAM_NAMES, sigma=exp.sigma,
                                       cv_threshold=cv_threshold,
                                       confirm_with_profile=confirm_with_profile)
    return GateDecision(experiment=exp, status=dict(core.status), cv=dict(core.cv), rank=core.rank)
