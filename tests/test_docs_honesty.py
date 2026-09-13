from pathlib import Path

from complexity_science.honesty import banned_hits

ROOT = Path(__file__).resolve().parents[1]
DOC_PATHS = [
    ROOT / "README.md",
    ROOT / "DISCLAIMER.md",
    ROOT / "docs" / "AWAITING_EXTERNAL_VALIDATION.md",
    ROOT / "docs" / "PROFESSOR_EMAIL.md",
    ROOT / "web" / "index.html",
]


def test_public_docs_have_required_headings_and_no_banned_phrasing():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    for heading in ("problem", "method", "outputs", "non-claims"):
        assert heading in readme
    for path in DOC_PATHS:
        text = path.read_text(encoding="utf-8")
        hits = banned_hits(text)
        assert hits == [], f"{path} has banned phrasing: {hits}"
