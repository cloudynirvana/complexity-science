"""Constrained / multi-objective search over class-level effectors."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Sequence

from complexity_science.biologics.catalog import Effector, blend, load_catalog
from complexity_science.biologics.constraints import SearchConstraints, depletion_load
from complexity_science.dynamics.archetypes import Archetype
from complexity_science.dynamics.ode import HostBurdenParams
from complexity_science.dynamics.simulate import Schedule, Trajectory, simulate

INTENSITIES = (0.3, 0.6, 1.0)
SCHEDULE_KINDS = ("continuous", "pulsed")


@dataclass
class Hypothesis:
    rank: int
    label: str
    effector_ids: tuple[str, ...]
    weights: tuple[float, ...]
    schedule: Schedule
    metrics: dict[str, float]
    score: float
    objectives: dict[str, float]
    feasible: bool
    violations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    trajectory_preview: dict[str, list[float]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "label": self.label,
            "kind": "in_silico_hypothesis",
            "effector_ids": list(self.effector_ids),
            "weights": list(self.weights),
            "schedule": self.schedule.to_dict(),
            "metrics": self.metrics,
            "score": self.score,
            "objectives": self.objectives,
            "feasible": self.feasible,
            "violations": list(self.violations),
            "notes": list(self.notes),
            "trajectory_preview": self.trajectory_preview,
        }


def _label(effectors: Sequence[Effector], schedule: Schedule) -> str:
    names = " + ".join(item.class_label for item in effectors)
    return f"{names} / {schedule.kind} @ {schedule.intensity:.2f}"


def _objectives(metrics: dict[str, float]) -> dict[str, float]:
    # Lower burden and toxicity are better; higher immune competence is better.
    return {
        "burden": metrics["b_final"] + 0.35 * metrics["b_mean"],
        "toxicity": metrics["x_peak"] + 0.25 * metrics["x_mean"],
        "immune_deficit": max(0.0, 1.0 - metrics["i_final"]),
    }


def _score(
    objectives: dict[str, float],
    *,
    constraints: SearchConstraints,
    immune_stim_load: float,
    feasible: bool,
) -> float:
    # Scalarisation is explicit and crude on purpose.
    raw = (
        1.15 * (1.0 - min(objectives["burden"], 1.5) / 1.5)
        + 0.65 * (1.0 - min(objectives["immune_deficit"], 1.0))
        - 0.9 * min(objectives["toxicity"], 2.0)
        - constraints.infection_risk_weight * immune_stim_load
    )
    if not feasible:
        raw -= 1.5
    return float(raw)


def _evaluate(
    archetype: Archetype,
    combo: list[tuple[Effector, float]],
    schedule: Schedule,
    constraints: SearchConstraints,
    horizon_days: float,
) -> tuple[Hypothesis, Trajectory]:
    params: HostBurdenParams = blend(combo, archetype.params)
    traj = simulate(
        params,
        archetype.y0,
        horizon_days=horizon_days,
        schedule=schedule,
    )
    effectors = [item for item, _w in combo]
    weights = tuple(w for _e, w in combo)
    violations: list[str] = []
    if not traj.success:
        violations.append(f"integrator:{traj.message}")
        metrics = {
            "b_final": 1.0,
            "i_final": 0.0,
            "x_peak": 9.0,
            "x_mean": 9.0,
            "b_mean": 1.0,
            "e_auc": 0.0,
        }
    else:
        metrics = traj.metrics()
        if metrics["x_peak"] > constraints.x_cap:
            violations.append(
                f"x_peak {metrics['x_peak']:.3f} > x_cap {constraints.x_cap:.3f}"
            )
    deplete = depletion_load(combo)
    if deplete > constraints.max_immune_depletion:
        violations.append(
            f"immune_depletion_load {deplete:.3f} > "
            f"{constraints.max_immune_depletion:.3f}"
        )
    feasible = not violations
    objectives = _objectives(metrics)
    stim_load = sum(e.immune_stim * w for e, w in combo)
    score = _score(
        objectives,
        constraints=constraints,
        immune_stim_load=stim_load,
        feasible=feasible,
    )
    notes = [
        "Score is a transparent scalarisation, not a clinical utility.",
        f"Depletion load={deplete:.3f}; immune-stim load={stim_load:.3f}.",
    ]
    for effector in effectors:
        notes.extend(effector.nstg_notes)
    hyp = Hypothesis(
        rank=0,
        label=_label(effectors, schedule),
        effector_ids=tuple(e.id for e in effectors),
        weights=weights,
        schedule=schedule,
        metrics=metrics,
        score=score,
        objectives=objectives,
        feasible=feasible,
        violations=violations,
        notes=notes,
        trajectory_preview=traj.downsample(18) if traj.success else {},
    )
    return hyp, traj


def _candidate_combos(
    catalog: Sequence[Effector],
    *,
    allow_combinations: bool,
    max_classes: int,
) -> list[list[tuple[Effector, float]]]:
    singles = [[(e, 1.0)] for e in catalog]
    if not allow_combinations or max_classes < 2:
        return singles
    pairs: list[list[tuple[Effector, float]]] = []
    for left, right in combinations(catalog, 2):
        # Reduced per-class weight: additive caricature, not synergy claim.
        pairs.append([(left, 0.55), (right, 0.55)])
    return singles + pairs


def search_pathways(
    archetype: Archetype,
    constraints: SearchConstraints,
    *,
    catalog: Sequence[Effector] | None = None,
    horizon_days: float = 42.0,
    allow_combinations: bool = True,
    max_candidates: int = 36,
    include_untreated: bool = True,
) -> tuple[list[Hypothesis], SearchConstraints]:
    catalog = list(catalog) if catalog is not None else load_catalog()
    combos = _candidate_combos(
        catalog,
        allow_combinations=allow_combinations,
        max_classes=constraints.max_classes,
    )
    hypotheses: list[Hypothesis] = []
    effective = constraints
    if include_untreated:
        untreated_sched = Schedule(kind="continuous", intensity=0.0)
        untreated, _traj = _evaluate(
            archetype, [], untreated_sched, constraints, horizon_days
        )
        untreated.label = "untreated baseline"
        # If untreated already sits above the absolute cap, constrain *excess*
        # host-stress instead of declaring the whole basin infeasible.
        x_ref = float(untreated.metrics.get("x_peak") or constraints.x_cap)
        if x_ref > constraints.x_cap:
            slack = 0.06
            new_cap = x_ref + slack
            effective = SearchConstraints(
                x_cap=new_cap,
                max_immune_depletion=constraints.max_immune_depletion,
                infection_risk_weight=constraints.infection_risk_weight,
                max_classes=constraints.max_classes,
                flags=constraints.flags,
                rationale=constraints.rationale
                + (
                    "Absolute x_cap was below untreated X_peak; "
                    f"using excess-stress cap {new_cap:.3f} = untreated + {slack}.",
                ),
            )
            untreated.violations = [
                v for v in untreated.violations if not v.startswith("x_peak")
            ]
            untreated.feasible = not untreated.violations
            untreated.score = _score(
                untreated.objectives,
                constraints=effective,
                immune_stim_load=0.0,
                feasible=untreated.feasible,
            )
        untreated.notes = [
            "Reference trajectory with u(t)=0. Not a 'watch and wait' recommendation."
        ]
        hypotheses.append(untreated)

    for combo in combos:
        for intensity in INTENSITIES:
            for kind in SCHEDULE_KINDS:
                schedule = Schedule(
                    kind=kind,
                    intensity=intensity,
                    period_days=7.0,
                    duty=0.35,
                )
                hyp, _traj = _evaluate(
                    archetype, combo, schedule, effective, horizon_days
                )
                hypotheses.append(hyp)

    hypotheses.sort(key=lambda h: (-h.feasible, -h.score))
    limit = max(int(max_candidates), 1)
    trimmed = hypotheses[:limit]
    untreated = [h for h in hypotheses if not h.effector_ids]
    if untreated and all(h.effector_ids for h in trimmed):
        trimmed = trimmed[:-1] + untreated if len(trimmed) >= limit else trimmed + untreated
        trimmed.sort(key=lambda h: (-h.feasible, -h.score))
    for index, hyp in enumerate(trimmed, start=1):
        hyp.rank = index
    return trimmed, effective
