from __future__ import annotations

from copy import deepcopy

import pytest

from pathology_cases.loader import CaseCardError, iter_case_paths, load_case, parse_case
from pathology_cases.schema import CaseCard, SCHEMA_VERSION
from tests.conftest import CASES, minimal_payload


SEED_IDS = {
    "tnbc_metabolic_immune_exclusion",
    "gbm_invasive_niche_hypoxia",
    "pdac_stromal_barrier",
    "dormant_occult_disease",
}


def test_four_seed_cases_validate() -> None:
    paths = iter_case_paths(CASES)
    assert {path.stem for path in paths} == SEED_IDS
    cards = [load_case(path) for path in paths]
    assert {card.id for card in cards} == SEED_IDS
    for card in cards:
        assert card.schema_version == SCHEMA_VERSION
        assert card.disclaimer
        assert len(card.citations) >= 3
        assert len(card.nstg_touchpoints) >= 1


@pytest.mark.parametrize("path", iter_case_paths(CASES), ids=lambda p: p.stem)
def test_seed_citations_are_well_formed(path) -> None:
    card = load_case(path)
    for citation in card.citations:
        assert "Federal Ministry" in citation.vancouver or citation.doi
        if citation.kind in {"primary", "review"}:
            assert citation.doi and citation.doi.startswith("10.")
            assert "fake" not in citation.doi.lower()


def test_minimal_payload_roundtrip(disclaimer: str) -> None:
    card = parse_case(minimal_payload(disclaimer))
    assert isinstance(card, CaseCard)
    assert card.id == "test_minimal_card"


def test_missing_falsifier_is_rejected(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["falsifiers"] = payload["falsifiers"][:1]
    with pytest.raises(CaseCardError, match="falsifier"):
        parse_case(payload)


def test_unknown_citation_id_is_rejected(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["candidate_mechanisms"][0]["supporting_citation_ids"] = ["missing_cite"]
    with pytest.raises(CaseCardError, match="unknown ids"):
        parse_case(payload)


def test_fake_doi_is_rejected(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["citations"][0]["doi"] = "10.0000/fake-doi"
    with pytest.raises(CaseCardError, match="DOI"):
        parse_case(payload)


def test_disclaimer_must_carry_non_claims(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["disclaimer"] = "A research note without the required honesty phrases."
    with pytest.raises(CaseCardError, match="disclaimer"):
        parse_case(payload)


def test_json_schema_file_exists() -> None:
    schema = CASES.parent / "schema" / "case_card.schema.json"
    assert schema.is_file()
    text = schema.read_text(encoding="utf-8")
    assert "CaseCard" in text or "disease" in text
    assert "candidate_mechanisms" in text
