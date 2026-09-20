"""CaseCard data layer — YAML in, validated research objects out.

No ODE code lives here. Adding a pathology case is a data-only change.
"""

from pathology_cases.honesty import DISCLAIMER_SHORT, EPISTEMIC_BOUNDARY, NON_CLAIMS
from pathology_cases.loader import CASES_DIR, load_case, load_cases, iter_case_paths
from pathology_cases.schema import CaseCard
from pathology_cases.smuggling import ParameterSmugglingError, scan_for_smuggling

__all__ = [
    "CASES_DIR",
    "CaseCard",
    "DISCLAIMER_SHORT",
    "EPISTEMIC_BOUNDARY",
    "NON_CLAIMS",
    "ParameterSmugglingError",
    "iter_case_paths",
    "load_case",
    "load_cases",
    "scan_for_smuggling",
]
