"""Refuse parameter smuggling in CaseCard YAML.

A CaseCard may carry knowledge, cited evidence, candidate mechanisms, and
qualitative NSTG constraints. It may not carry doses, rate constants, ODE
knobs, PK/PD coefficients, or numeric 'constraint scales'.
"""

from __future__ import annotations

import re
from typing import Any

FORBIDDEN_KEYS = frozenset(
    {
        "alpha",
        "auc",
        "beta",
        "calibrated",
        "clearance",
        "cmax",
        "cmin",
        "constraint_hints",
        "dosage",
        "dose",
        "doses",
        "dosing",
        "dt",
        "ec50",
        "ed50",
        "fitted",
        "half_life",
        "ic50",
        "infection_risk_weight",
        "infusion_rate",
        "initial_conditions",
        "kcat",
        "kd",
        "ki",
        "km",
        "kon",
        "koff",
        "k_off",
        "k_on",
        "max_immune_depletion",
        "max_immune_depletion_scale",
        "mg_per_kg",
        "ode",
        "ode_params",
        "parameter",
        "parameters",
        "params",
        "pk",
        "pk_pd",
        "pd",
        "rate",
        "rate_constant",
        "rate_constants",
        "rates",
        "regimen",
        "rhs",
        "schedule",
        "solver",
        "t_half",
        "theta",
        "timestep",
        "tmax",
        "vmax",
        "x_cap",
        "x_cap_scale",
        "y0",
    }
)

# Citation strings legitimately contain years, volumes, and DOIs.
_SKIP_VALUE_SCAN_KEYS = frozenset(
    {"vancouver", "doi", "pmid", "url", "id", "schema_version"}
)

_DOSE_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|ug|ng)\s*(?:/\s*(?:kg|m2|m\^2|m²))?\b",
    re.IGNORECASE,
)
_PK_TOKEN_RE = re.compile(
    r"\b("
    r"ec50|ic50|ed50|kcat|k_on|k_off|"
    r"x_cap(?:_scale)?|infection_risk_weight|max_immune_depletion(?:_scale)?|"
    r"half[-\s]?life|t1/?2|cmax|cmin|tmax|auc0?"
    r")\b",
    re.IGNORECASE,
)
_Q_SCHEDULE_RE = re.compile(r"\bq(?:[1-4]w|d|24h)\b", re.IGNORECASE)


class ParameterSmugglingError(ValueError):
    """Raised when a CaseCard tries to carry a non-parameter as a parameter."""


def _norm_key(key: str) -> str:
    return str(key).strip().lower().replace("-", "_")


def scan_for_smuggling(payload: Any, *, path: str = "$") -> None:
    """Walk raw YAML and raise if parameter-like keys or values appear."""
    if isinstance(payload, dict):
        for key, value in payload.items():
            norm = _norm_key(str(key))
            child = f"{path}.{key}"
            if norm in FORBIDDEN_KEYS:
                raise ParameterSmugglingError(
                    f"{child}: key '{key}' is a refused non-parameter. "
                    "CaseCards cannot carry doses, ODE/PK/PD knobs, or "
                    "NSTG-derived numeric scales."
                )
            if norm not in _SKIP_VALUE_SCAN_KEYS:
                scan_for_smuggling(value, path=child)
        return
    if isinstance(payload, list):
        for index, item in enumerate(payload):
            scan_for_smuggling(item, path=f"{path}[{index}]")
        return
    if isinstance(payload, str):
        _scan_string(payload, path)
        return
    if isinstance(payload, (int, float)) and not isinstance(payload, bool):
        # Bare numbers are allowed only as schema_version-adjacent metadata
        # never appears here; any numeric leaf is a smuggled parameter.
        raise ParameterSmugglingError(
            f"{path}: numeric leaf {payload!r} is a refused non-parameter. "
            "Put quantities in later evidence-gated work, not in a CaseCard."
        )


def _scan_string(text: str, path: str) -> None:
    if _DOSE_RE.search(text):
        raise ParameterSmugglingError(
            f"{path}: dose-like quantity is a refused non-parameter."
        )
    if _PK_TOKEN_RE.search(text):
        raise ParameterSmugglingError(
            f"{path}: PK/PD or ODE token is a refused non-parameter."
        )
    if _Q_SCHEDULE_RE.search(text):
        raise ParameterSmugglingError(
            f"{path}: dosing-schedule token is a refused non-parameter."
        )
