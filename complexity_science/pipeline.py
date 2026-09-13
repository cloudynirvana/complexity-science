"""End-to-end in-silico pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Sequence

from complexity_science.version import __version__
from complexity_science.biologics.catalog import load_catalog
from complexity_science.biologics.constraints import SearchConstraints, build_constraints
from complexity_science.biologics.search import Hypothesis, search_pathways
from complexity_science.dynamics.archetypes import Archetype, get_archetype
from complexity_science.honesty import DISCLAIMER_SHORT, NON_CLAIMS
from complexity_science.nstg.retriever import NstgRetriever, RetrievalResult


FALSIFICATION = [
    "If an independent burden series falls while E is below the model's EC50 and I is flat, reject immune-only clearance for that class.",
    "If peak host-stress (labs, not X) occurs with undetectable exposure, reject χ_E as the toxicity channel.",
    "If a comorbidity cohort violates the tighter X cap but shows no extra harm signal, reject the NSTG-hint scale as a sufficient proxy.",
    "If a two-class rank is super-additive in silico but additive or antagonistic in an orthogonal assay, reject the blend() assumption.",
    "If sparse sampling cannot identify r versus ε_I separately, do not treat ranked gaps as effect sizes.",
    "If malaria fever or HIV opportunistic infection appears, the four-state model is misspecified — stop analogising X to that event.",
]


@dataclass
class PipelineResult:
    created_at: str
    version: str
    disclaimer: str
    non_claims: list[str]
    archetype: Archetype
    retrieval: RetrievalResult
    constraints: SearchConstraints
    hypotheses: list[Hypothesis]
    falsification: list[str] = field(default_factory=lambda: list(FALSIFICATION))
    horizon_days: float = 42.0
    notes: list[str] = field(default_factory=list)

    def top(self) -> Hypothesis | None:
        return self.hypotheses[0] if self.hypotheses else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "complexity_science.report.v1",
            "created_at": self.created_at,
            "version": self.version,
            "disclaimer": self.disclaimer,
            "non_claims": list(self.non_claims),
            "horizon_days": self.horizon_days,
            "archetype": self.archetype.to_dict(),
            "nstg": self.retrieval.to_dict(),
            "constraints": self.constraints.to_dict(),
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "falsification_checklist": list(self.falsification),
            "notes": list(self.notes),
        }


def run_pipeline(
    *,
    archetype_id: str = "exhausted_high_burden",
    conditions: Sequence[str] | str | None = None,
    horizon_days: float = 42.0,
    allow_combinations: bool = True,
    max_candidates: int = 24,
    retriever: NstgRetriever | None = None,
) -> PipelineResult:
    """Run retrieval → constraints → dynamics search → ranked hypotheses."""
    archetype = get_archetype(archetype_id)
    retriever = retriever or NstgRetriever()
    if conditions is None:
        conditions = ["oncology_supportive"]
    retrieval = retriever.retrieve(conditions)
    constraints = build_constraints(retrieval)
    hypotheses, constraints = search_pathways(
        archetype,
        constraints,
        catalog=load_catalog(),
        horizon_days=horizon_days,
        allow_combinations=allow_combinations,
        max_candidates=max_candidates,
    )
    notes = [
        "MHBD-4 parameters are computational, not fitted to a named cohort.",
        "Biologic effectors are class-level caricatures with provenance tags.",
        "Awaiting external validation — see docs/AWAITING_EXTERNAL_VALIDATION.md.",
    ]
    if retrieval.unmatched:
        notes.append("Unmatched condition queries: " + ", ".join(retrieval.unmatched))
    return PipelineResult(
        created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        version=__version__,
        disclaimer=DISCLAIMER_SHORT,
        non_claims=list(NON_CLAIMS),
        archetype=archetype,
        retrieval=retrieval,
        constraints=constraints,
        hypotheses=hypotheses,
        horizon_days=float(horizon_days),
        notes=notes,
    )
