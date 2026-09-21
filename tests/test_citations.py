"""Thesis #2 Vancouver integrity: in-text ↔ references, Scholar metas."""

from __future__ import annotations

import re
from html.parser import HTMLParser

from tests.conftest import ROOT

THESIS = ROOT / "docs" / "manuscript" / "thesis_02_complexity_nstg_pathology.md"
SCHOLAR = ROOT / "scholar" / "thesis_02.html"
STYLE = ROOT / "docs" / "CITATION_STYLE.md"

# Ignore code indexes such as candidate_mechanisms[0].
CITE_RE = re.compile(
    r"(?<![A-Za-z0-9_])\[(\d+(?:\s*[–-]\s*\d+)?(?:\s*,\s*\d+(?:\s*[–-]\s*\d+)?)*)\]"
)
REF_RE = re.compile(r"^(\d+)\. (.+)$", re.M)


def _expand(inner: str) -> set[int]:
    out: set[int] = set()
    for part in re.split(r"\s*,\s*", inner):
        if re.search(r"[–-]", part):
            start_s, end_s = re.split(r"\s*[–-]\s*", part, maxsplit=1)
            if start_s.isdigit() and end_s.isdigit():
                out.update(range(int(start_s), int(end_s) + 1))
        elif part.isdigit():
            out.add(int(part))
    return out


def _cited_and_listed() -> tuple[set[int], dict[int, str]]:
    text = THESIS.read_text(encoding="utf-8")
    body, _, refs = text.partition("# References")
    cited: set[int] = set()
    for match in CITE_RE.finditer(body):
        cited.update(_expand(match.group(1)))
    listed = {int(n): line for n, line in REF_RE.findall(refs)}
    return cited, listed


def test_citation_style_policy_exists() -> None:
    text = STYLE.read_text(encoding="utf-8")
    assert "Vancouver" in text
    assert "Do not invent DOIs" in text
    assert "et al." in text
    assert "PMID" in text


def test_in_text_and_references_are_bijective() -> None:
    cited, listed = _cited_and_listed()
    assert cited, "no in-text citations found"
    assert cited == set(listed)
    assert max(listed) == len(listed) == 64
    assert min(listed) == 1


def test_journal_items_have_doi_and_pmid() -> None:
    _, listed = _cited_and_listed()
    books = {15, 16, 17}
    gov = {49, 50, 51, 52, 53}
    weaver = {1}  # verified PMID, no DOI
    for n, line in listed.items():
        assert not re.search(r"10\.0{3,}/|fake|example\.com", line, re.I)
        if n in books:
            assert "doi:" not in line
            continue
        if n in gov:
            assert "[Internet]" in line
            assert "[cited 2026 Sep 20]" in line
            assert "Available from:" in line or "available from:" in line
            assert "doi:" not in line
            continue
        if n in weaver:
            assert "PMID: 18882675" in line
            assert "doi:" not in line
            continue
        assert "doi:10." in line
        assert "PMID:" in line
        assert re.search(r"\d{4};", line)


def test_scholar_citation_reference_metas_match() -> None:
    _, listed = _cited_and_listed()
    html = SCHOLAR.read_text(encoding="utf-8")

    class _Meta(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.refs: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            ad = dict(attrs)
            if tag == "meta" and ad.get("name") == "citation_reference":
                self.refs.append(ad.get("content") or "")

    parser = _Meta()
    parser.feed(html)
    assert len(parser.refs) == 64
    for n, line in listed.items():
        assert parser.refs[n - 1] == line
