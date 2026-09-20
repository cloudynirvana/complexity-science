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
    thesis = ROOT / "docs" / "manuscript" / "thesis_02_complexity_nstg_pathology.md"
    thesis_pdf = ROOT / "docs" / "manuscript" / "thesis_02_complexity_nstg_pathology.pdf"
    scholar = ROOT / "scholar" / "thesis_02.html"
    scholar_doc = ROOT / "docs" / "SCHOLAR_THESIS_02.md"
    assert thesis.is_file()
    assert thesis_pdf.is_file() and thesis_pdf.stat().st_size > 10_000
    assert scholar.is_file()
    assert scholar_doc.is_file()
    texts.append(thesis.read_text(encoding="utf-8"))
    texts.append(scholar.read_text(encoding="utf-8"))
    blob = "\n".join(texts).lower()
    assert "not a medical device" in blob
    assert "not dosing" in blob
    assert "not a cure" in blob
    assert "never auto-translated" in blob
    for path in iter_case_paths(CASES):
        card = load_case(path)
        lowered = card.disclaimer.lower()
        assert "not a medical device" in lowered
        assert "not a cure" in lowered


def test_thesis_02_scholar_highwire_tags() -> None:
    html = (ROOT / "scholar" / "thesis_02.html").read_text(encoding="utf-8")
    for tag in (
        'name="citation_title"',
        'name="citation_author"',
        'name="citation_publication_date"',
        'name="citation_pdf_url"',
        'name="citation_fulltext_html_url"',
        "Ogbonna, Kelechi Emeka",
        "2026/09/20",
        "thesis_02_complexity_nstg_pathology.pdf",
    ):
        assert tag in html
    assert "github.io/complexity-science" in html
    assert "raw.githubusercontent.com" in html
