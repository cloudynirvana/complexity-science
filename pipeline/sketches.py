"""PathwaySketch — gated explorer output. Hypotheses, not parameters."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from pathology_cases.honesty import DISCLAIMER_SHORT, EPISTEMIC_BOUNDARY, NON_CLAIMS

SKETCH_VERSION = "1.0.0"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RankedHypothesis(_Strict):
    rank: int
    mechanism_id: str
    statement: str
    biologic_axis: str
    status: Literal["hypothesis", "blocked_pending_evidence"]
    research_score: int
    score_notes: list[str]
    nstg_constraints_applied: list[str]
    required_evidence: list[str]
    parameter_status: Literal["refused"] = "refused"
    prediction_status: Literal["not_emitted"] = "not_emitted"


class RefusedNonParameter(_Strict):
    source: str
    attempted_kind: Literal["parameter", "prediction", "dose", "nstg_scale"]
    reason: str


class PathwaySketch(_Strict):
    schema_version: Literal["1.0.0"] = SKETCH_VERSION
    case_id: str
    title: str
    disclaimer: str = DISCLAIMER_SHORT
    epistemic_boundary: str = EPISTEMIC_BOUNDARY
    non_claims: list[str] = Field(default_factory=lambda: list(NON_CLAIMS))
    ranked_hypotheses: list[RankedHypothesis]
    required_evidence: list[str]
    refused_non_parameters: list[RefusedNonParameter]
    nstg_constraints: list[str]
    notes: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
