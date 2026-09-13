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

# Surface forms we refuse to emit. Keep the list conservative and specific.
_BANNED_PATTERNS = (
    re.compile(r"\bcure[sd]?\b", re.IGNORECASE),
    re.compile(r"\bcures\b", re.IGNORECASE),
    re.compile(r"\bphase\s*ii\b", re.IGNORECASE),
    re.compile(r"\bphase\s*2\b", re.IGNORECASE),
    re.compile(r"\bfda[-\s]?ready\b", re.IGNORECASE),
    re.compile(r"\bfda[-\s]?approved\b", re.IGNORECASE),
    re.compile(r"\bclinically\s+validated\b", re.IGNORECASE),
    re.compile(r"\bclinically\s+proven\b", re.IGNORECASE),
)


def banned_hits(text: str) -> list[str]:
    """Return banned substrings found in ``text`` (empty if clean)."""
    hits: list[str] = []
    for pat in _BANNED_PATTERNS:
        for match in pat.finditer(text):
            hits.append(match.group(0))
    return hits


def assert_honest(text: str, *, label: str = "text") -> None:
    """Raise ``ValueError`` if banned phrasing appears."""
    hits = banned_hits(text)
    if hits:
        raise ValueError(f"{label} contains banned phrasing: {hits}")


def assert_honest_many(chunks: Iterable[str], *, label: str = "bundle") -> None:
    assert_honest("\n".join(chunks), label=label)
