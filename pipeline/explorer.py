"""Stub NSTG-guided biologics pathway explorer.

Input: CaseCard (data-only YAML).
Output: PathwaySketch (ranked hypotheses + required evidence + refusals).
No patient data. No ODE import. No auto-translated NSTG parameters.
"""

from __future__ import annotations

from pathlib import Path

from pathology_cases.loader import load_case, load_cases
from pathology_cases.schema import CaseCard, CandidateMechanism
from pipeline.evidence_gate import refuse_parameterization, required_evidence_for
from pipeline.nstg_layer import axis_penalty, constraints_for
from pipeline.sketches import PathwaySketch, RankedHypothesis


def _score(card: CaseCard, mechanism: CandidateMechanism) -> tuple[int, list[str], str]:
    notes: list[str] = []
    score = 0
    status = "hypothesis"

    n_cite = len(mechanism.supporting_citation_ids)
    score += 2 * n_cite
    notes.append(f"+{2 * n_cite} from {n_cite} supporting citation(s) (knowledge pointers)")

    n_fals = sum(1 for item in card.falsifiers if mechanism.id in item.mechanism_ids)
    if n_fals:
        score += 3
        notes.append(f"+3 falsifiable ({n_fals} linked falsifier(s))")
    else:
        status = "blocked_pending_evidence"
        notes.append("blocked: mechanism has no falsifier")

    if not mechanism.supporting_citation_ids:
        status = "blocked_pending_evidence"
        notes.append("blocked: mechanism has no citations")

    penalty, penalty_notes = axis_penalty(card, mechanism)
    if penalty:
        score -= penalty
        notes.extend(penalty_notes)

    score += 1  # present on a validated card
    notes.append("+1 validated CaseCard membership (not an efficacy credit)")
    return score, notes, status


def explore(card: CaseCard) -> PathwaySketch:
    refused = refuse_parameterization(card)
    nstg = constraints_for(card)
    ranked: list[tuple[int, str, RankedHypothesis]] = []

    for mechanism in card.candidate_mechanisms:
        score, notes, status = _score(card, mechanism)
        evidence = required_evidence_for(card, mechanism)
        applied = [
            touch.constraint_statement
            for touch in card.nstg_touchpoints
            if touch.id in mechanism.nstg_touchpoint_ids
        ]
        ranked.append(
            (
                score if status == "hypothesis" else -10_000 + score,
                mechanism.id,
                RankedHypothesis(
                    rank=0,
                    mechanism_id=mechanism.id,
                    statement=mechanism.statement,
                    biologic_axis=mechanism.biologic_axis,
                    status=status,  # type: ignore[arg-type]
                    research_score=score,
                    score_notes=notes,
                    nstg_constraints_applied=applied,
                    required_evidence=evidence,
                ),
            )
        )

    ranked.sort(key=lambda item: (-item[0], item[1]))
    hypotheses = []
    for index, (_, _, hypothesis) in enumerate(ranked, start=1):
        hypotheses.append(hypothesis.model_copy(update={"rank": index}))

    union_evidence: list[str] = []
    for hypothesis in hypotheses:
        for item in hypothesis.required_evidence:
            if item not in union_evidence:
                union_evidence.append(item)

    return PathwaySketch(
        case_id=card.id,
        title=card.title,
        ranked_hypotheses=hypotheses,
        required_evidence=union_evidence,
        refused_non_parameters=refused,
        nstg_constraints=nstg,
        notes=[
            "Explorer is a stub: ranking is bibliographic + falsifiability + NSTG flags.",
            "No ODE was integrated. Do not treat research_score as an effect size.",
            "No patient record was read.",
        ],
    )


def explore_path(path: Path | str) -> PathwaySketch:
    return explore(load_case(path))


def explore_all(directory: Path | None = None) -> list[PathwaySketch]:
    return [explore(card) for card in load_cases(directory)]
