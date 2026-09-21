"""Evidence gate: Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction.

NSTG and CaseCard content may constrain exploration. They may not become
model parameters unless a future, explicit evidence record opens that gate.
This stub never opens the gate.
"""

from __future__ import annotations

from pathology_cases.schema import CaseCard, CandidateMechanism
from pipeline.sketches import RefusedNonParameter

GATE_CLOSED_REASON = (
    "Evidence gate closed: NSTG and CaseCard content are not auto-translated "
    "into model parameters. A mechanism is not a coefficient."
)


def refuse_parameterization(card: CaseCard) -> list[RefusedNonParameter]:
    """Always-on refusals that prove the gate is doing work on clean cards."""
    refused = [
        RefusedNonParameter(
            source="nstg_touchpoints",
            attempted_kind="nstg_scale",
            reason=(
                "NSTG is a structured clinical-knowledge constraint layer. "
                "This stub will not emit x_cap, infection_risk_weight, doses, "
                "or any other numeric scale from a touchpoint."
            ),
        ),
        RefusedNonParameter(
            source="candidate_mechanisms",
            attempted_kind="parameter",
            reason=(
                "Candidate mechanisms remain hypotheses. Rate constants, "
                "EC50-like knobs, and ODE coefficients are refused."
            ),
        ),
        RefusedNonParameter(
            source="explorer",
            attempted_kind="prediction",
            reason=(
                "PathwaySketch ranks research hypotheses. It does not predict "
                "response, survival, or a care pathway for a person."
            ),
        ),
    ]
    if any(touch.role != "constraint" for touch in card.nstg_touchpoints):
        refused.append(
            RefusedNonParameter(
                source="nstg_touchpoints.role",
                attempted_kind="parameter",
                reason="Only role=constraint is admitted for NSTG touchpoints.",
            )
        )
    return refused


def required_evidence_for(card: CaseCard, mechanism: CandidateMechanism) -> list[str]:
    """Evidence still required before anyone may even discuss parameterization."""
    falsifiers = [
        item
        for item in card.falsifiers
        if mechanism.id in item.mechanism_ids
    ]
    items = [
        (
            "Independent experimental or clinical measurement of an observable "
            f"named on this card ({', '.join(obs.id for obs in card.observables)}) "
            "that can separate this mechanism from neighbouring hypotheses."
        ),
        (
            "An orthogonal assay (not the paper that suggested the mechanism) "
            "before any rate, dose, or ODE coefficient is proposed."
        ),
        GATE_CLOSED_REASON,
    ]
    for falsifier in falsifiers:
        items.append(
            f"Design a test of falsifier {falsifier.id}: if {falsifier.if_observed} "
            f"— then reject {falsifier.then_reject}."
        )
    return items
