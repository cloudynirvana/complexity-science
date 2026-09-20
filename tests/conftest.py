from __future__ import annotations

from pathlib import Path

import pytest

from pathology_cases.honesty import DISCLAIMER_SHORT

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "pathology_cases" / "cases"


@pytest.fixture
def disclaimer() -> str:
    return DISCLAIMER_SHORT


def minimal_payload(disclaimer: str) -> dict:
    """A tiny valid CaseCard payload for mutation tests."""
    return {
        "schema_version": "1.0.0",
        "id": "test_minimal_card",
        "title": "Minimal valid research card",
        "disclaimer": disclaimer,
        "disease": {
            "name": "Synthetic research disease",
            "abbreviations": ["SRD"],
            "framing": "Research framing only — not a care pathway.",
        },
        "systemic_axes": [
            {
                "id": "axis_a",
                "layer": "metabolism",
                "role": "driver",
                "description": "First systemic axis for the test card.",
            },
            {
                "id": "axis_b",
                "layer": "host",
                "role": "constraint",
                "description": "Host constraint axis for the test card.",
            },
        ],
        "observables": [
            {
                "id": "obs_a",
                "name": "Observable A",
                "modality": "research assay",
                "research_only": True,
            },
            {
                "id": "obs_b",
                "name": "Observable B",
                "modality": "research imaging",
                "research_only": True,
            },
        ],
        "candidate_mechanisms": [
            {
                "id": "mech_one",
                "statement": "First candidate mechanism used only for schema tests.",
                "biologic_axis": "metabolic_checkpoint",
                "supporting_citation_ids": ["cite_one"],
                "nstg_touchpoint_ids": ["nstg_one"],
                "status": "hypothesis",
            },
            {
                "id": "mech_two",
                "statement": "Second candidate mechanism used only for schema tests.",
                "biologic_axis": "host_comorbidity",
                "supporting_citation_ids": ["cite_one"],
                "nstg_touchpoint_ids": ["nstg_one"],
                "status": "hypothesis",
            },
        ],
        "falsifiers": [
            {
                "id": "fals_one",
                "if_observed": "An orthogonal assay contradicts mechanism one.",
                "then_reject": "Mechanism one as a sufficient explanation.",
                "mechanism_ids": ["mech_one"],
            },
            {
                "id": "fals_two",
                "if_observed": "An orthogonal assay contradicts mechanism two.",
                "then_reject": "Mechanism two as a sufficient explanation.",
                "mechanism_ids": ["mech_two"],
            },
        ],
        "nstg_touchpoints": [
            {
                "id": "nstg_one",
                "theme": "infection",
                "constraint_statement": (
                    "Infection theme constrains exploration and must not "
                    "become a numeric scale."
                ),
                "source_citation_id": "nstg_cite",
                "role": "constraint",
            }
        ],
        "citations": [
            {
                "id": "cite_one",
                "kind": "review",
                "epistemic": "knowledge",
                "doi": "10.1038/nrc2256",
                "pmid": "17957189",
                "vancouver": (
                    "Aguirre-Ghiso JA. Models, mechanisms and clinical evidence "
                    "for cancer dormancy. Nat Rev Cancer. 2007;7(11):834-846. "
                    "doi:10.1038/nrc2256"
                ),
            },
            {
                "id": "cite_two",
                "kind": "review",
                "epistemic": "knowledge",
                "doi": "10.1038/nrc3793",
                "pmid": "25118602",
                "vancouver": (
                    "Sosa MS, Bragado P, Aguirre-Ghiso JA. Mechanisms of "
                    "disseminated cancer cell dormancy: an awakening field. "
                    "Nat Rev Cancer. 2014;14(9):611-622. doi:10.1038/nrc3793"
                ),
            },
            {
                "id": "nstg_cite",
                "kind": "guideline",
                "epistemic": "knowledge",
                "vancouver": (
                    "Federal Ministry of Health, Nigeria. Nigeria Standard "
                    "Treatment Guidelines. 3rd ed. Abuja: Federal Ministry of "
                    "Health; 2022."
                ),
            },
        ],
    }
