"""Shared honesty strings for CaseCards and PathwaySketches.

Documentation control only — not a legal device and not a care protocol.
"""

from __future__ import annotations

import re

EPISTEMIC_BOUNDARY = (
    "Knowledge ≠ Evidence ≠ Mechanism ≠ Parameter ≠ Prediction"
)

DISCLAIMER_SHORT = (
    "In-silico / computational research only. Not a medical device, not "
    "clinical decision support, not dosing advice, and not a cure. NSTG is a "
    "structured clinical-knowledge constraint layer and is never "
    "auto-translated into model parameters. "
    + EPISTEMIC_BOUNDARY
    + "."
)

NON_CLAIMS = [
    "Does not diagnose, treat, prevent, cure, or manage disease.",
    "Does not recommend a biologic product, dose, or schedule for a person.",
    "Does not claim clinical validation, Phase II status, or regulator readiness.",
    "Does not encode NSTG as an executable care protocol.",
    "Does not emit ODE, PK, or PD parameters from a CaseCard.",
    "Ranked items are computational hypotheses awaiting falsification.",
]

REQUIRED_DISCLAIMER_PHRASES = (
    "not a medical device",
    "not dosing",
    "not a cure",
)

_DEVICE_OR_CDS = re.compile(
    r"not (a )?clinical decision|not cds|not clinical decision support",
    re.IGNORECASE,
)


def disclaimer_gaps(text: str) -> list[str]:
    """Return required honesty phrases missing from a disclaimer string."""
    lowered = text.lower()
    gaps = [phrase for phrase in REQUIRED_DISCLAIMER_PHRASES if phrase not in lowered]
    if _DEVICE_OR_CDS.search(text) is None:
        gaps.append("not clinical decision support / not CDS")
    return gaps
