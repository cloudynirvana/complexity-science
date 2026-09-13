"""Shared honesty strings and a lightweight language guard.

Banned promotional / regulatory phrasing is rejected in generated reports.
This is a documentation control, not a legal device.
"""

from __future__ import annotations

import re
from typing import Iterable

DISCLAIMER_SHORT = (
    "In-silico research output only. Not a medical device, not clinical "
    "decision support, not dosing advice, and not externally validated. "
    "Official NSTG text is not redistributed; cite FMoH NSTG 2022."
)

NON_CLAIMS = [
    "Does not diagnose, treat, prevent, or manage disease.",
    "Does not recommend a biologic product, dose, or schedule for a person.",
    "Does not claim clinical validation, Phase II status, or FDA/NAFDAC readiness.",
    "Does not encode NSTG as an executable care protocol.",
    "Ranked items are computational hypotheses awaiting falsification.",
]

# Surface forms we refuse to *claim*. Mentions under an explicit negation
# (non-claims lists, "must not", "awaiting") are allowed.
_BANNED_PATTERNS = (
    re.compile(r"\bcure[sd]?\b", re.IGNORECASE),
    re.compile(r"\bphase\s*ii\b", re.IGNORECASE),
    re.compile(r"\bphase\s*2\b", re.IGNORECASE),
    re.compile(r"\bfda[-\s]?ready\b", re.IGNORECASE),
    re.compile(r"\bfda[-\s]?approved\b", re.IGNORECASE),
    re.compile(r"\bclinically\s+validated\b", re.IGNORECASE),
    re.compile(r"\bclinically\s+proven\b", re.IGNORECASE),
)

_NEGATION = re.compile(
    r"\b("
    r"not|never|no|without|banned|ban|refuse|avoid|"
    r"does\s+not|do\s+not|must\s+not|cannot|can't|don't|"
    r"non-?claims?|awaiting|unvalidated"
    r")\b",
    re.IGNORECASE,
)


def _negated(text: str, start: int) -> bool:
    window = text[max(0, start - 220) : start]
    return _NEGATION.search(window) is not None


def banned_hits(text: str) -> list[str]:
    """Return affirmative banned claims (empty if clean or only negated)."""
    hits: list[str] = []
    for pat in _BANNED_PATTERNS:
        for match in pat.finditer(text):
            if _negated(text, match.start()):
                continue
            hits.append(match.group(0))
    return hits


def assert_honest(text: str, *, label: str = "text") -> None:
    """Raise ``ValueError`` if banned phrasing appears."""
    hits = banned_hits(text)
    if hits:
        raise ValueError(f"{label} contains banned phrasing: {hits}")


def assert_honest_many(chunks: Iterable[str], *, label: str = "bundle") -> None:
    assert_honest("\n".join(chunks), label=label)
