from __future__ import annotations

from pathology_cases.honesty import DISCLAIMER_SHORT, EPISTEMIC_BOUNDARY, NON_CLAIMS
from pathology_cases.loader import iter_case_paths, load_case
from tests.conftest import CASES, ROOT


def test_epistemic_boundary_is_explicit() -> None:
    assert "Knowledge" in EPISTEMIC_BOUNDARY
    assert "Parameter" in EPISTEMIC_BOUNDARY
    assert "Prediction" in EPISTEMIC_BOUNDARY


def test_seed_disclaimers_and_docs_are_honest() -> None:
    texts = [DISCLAIMER_SHORT, *NON_CLAIMS]
    texts.append((ROOT / "README.md").read_text(encoding="utf-8"))
    texts.append((ROOT / "DISCLAIMER.md").read_text(encoding="utf-8"))
    blob = "\n".join(texts).lower()
    assert "not a medical device" in blob
    assert "not dosing" in blob
    assert "not a cure" in blob
    for path in iter_case_paths(CASES):
        card = load_case(path)
        lowered = card.disclaimer.lower()
        assert "not a medical device" in lowered
        assert "not a cure" in lowered
