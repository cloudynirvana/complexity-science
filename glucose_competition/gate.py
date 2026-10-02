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

from .identifiability import profile, report, two_sided
from .model import Params

STRUCTURAL = "refused:structural"
PRACTICAL = "refused:practical"
ONE_SIDED = "refused:one_sided_profile"
OPEN = "open"


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
    t = np.asarray(exp.times, float)
    r = report(p, t, exp.observables, sigma=exp.sigma, cv_threshold=cv_threshold, T0=list(exp.arms_T0))
    dec = GateDecision(experiment=exp, rank=r["rank"], cv=dict(r["cv"]))
    for name, cv in r["cv"].items():
        if not np.isfinite(cv):
            dec.status[name] = STRUCTURAL
        elif cv >= cv_threshold:
            dec.status[name] = PRACTICAL
        elif confirm_with_profile and len(exp.arms_T0) == 1:
            prof = profile(p, name, t, exp.observables, sigma=exp.sigma, T0=exp.arms_T0[0])
            dec.status[name] = OPEN if two_sided(prof) else ONE_SIDED
        else:
            dec.status[name] = OPEN
    return dec
