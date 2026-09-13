"""Toxicity + NSTG-informed comorbidity constraints (computational)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from complexity_science.nstg.models import ConstraintHints
from complexity_science.nstg.retriever import RetrievalResult


@dataclass(frozen=True)
class SearchConstraints:
    """Hard/soft caps used by the pathway search — not prescribing limits."""

    x_cap: float = 1.15
    max_immune_depletion: float = 0.55
    infection_risk_weight: float = 0.0
    max_classes: int = 2
    flags: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "x_cap": self.x_cap,
            "max_immune_depletion": self.max_immune_depletion,
            "infection_risk_weight": self.infection_risk_weight,
            "max_classes": self.max_classes,
            "flags": list(self.flags),
            "rationale": list(self.rationale),
            "role": "computational_constraint_not_dose_limit",
        }


def build_constraints(
    retrieval: RetrievalResult | None = None,
    *,
    base_x_cap: float = 1.15,
    base_max_immune_depletion: float = 0.55,
    extra_flags: Sequence[str] = (),
) -> SearchConstraints:
    hints = retrieval.merged_hints() if retrieval is not None else ConstraintHints()
    flags = list(hints.flags)
    for flag in extra_flags:
        if flag not in flags:
            flags.append(flag)
    rationale = [
        "x_cap is a modelling box, not a laboratory alert threshold.",
        "infection_risk_weight penalises immune-stimulatory exposure when the index says infection themes matter.",
    ]
    if retrieval is not None and retrieval.hits:
        names = ", ".join(hit.entry.id for hit in retrieval.hits)
        rationale.append(f"Index hits shaping scales: {names}.")
    if retrieval is not None and retrieval.unmatched:
        rationale.append(
            "Unmatched queries were ignored for constraints: "
            + ", ".join(retrieval.unmatched)
        )
    return SearchConstraints(
        x_cap=base_x_cap * hints.x_cap_scale,
        max_immune_depletion=base_max_immune_depletion
        * hints.max_immune_depletion_scale,
        infection_risk_weight=hints.infection_risk_weight,
        flags=tuple(flags),
        rationale=tuple(rationale),
    )


def depletion_load(weights: list[tuple[Any, float]]) -> float:
    """Scalar ψ-like load used against max_immune_depletion."""
    total = 0.0
    for effector, weight in weights:
        total += float(getattr(effector, "immune_deplete", 0.0)) * float(weight)
    return total
