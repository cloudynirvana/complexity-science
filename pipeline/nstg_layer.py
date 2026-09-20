"""NSTG as a qualitative constraint layer — never a parameter source.

Official FMoH NSTG 2022 is cited, not redistributed. This module only
attaches theme flags to hypotheses.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from pathology_cases.schema import CaseCard, CandidateMechanism

DATA_DIR = Path(__file__).resolve().parent / "data"
CATALOG_PATH = DATA_DIR / "nstg_constraint_catalog.yaml"

# Class-level axes that are infection- or immune-sensitive under NSTG themes.
_IMMUNE_AXES = frozenset(
    {"immune_exclusion", "immune_checkpoint", "dormancy_awakening"}
)
_INFECTION_THEMES = frozenset(
    {"infection", "hiv", "malaria", "tb", "febrile_neutropenia", "immunosuppression"}
)


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    payload = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{CATALOG_PATH} must be a mapping")
    if payload.get("role") != "constraint_catalog":
        raise ValueError("NSTG catalog role must remain 'constraint_catalog'")
    if "constraint_hints" in payload or "parameters" in payload:
        raise ValueError("NSTG catalog must not carry numeric constraint hints")
    return payload


def catalog_flags() -> dict[str, list[str]]:
    flags: dict[str, list[str]] = {}
    for entry in load_catalog().get("entries", []):
        flags[str(entry["id"])] = list(entry.get("flags") or [])
    return flags


def constraints_for(card: CaseCard) -> list[str]:
    statements = [touch.constraint_statement for touch in card.nstg_touchpoints]
    catalog = catalog_flags()
    for touch in card.nstg_touchpoints:
        extra = catalog.get(touch.id) or catalog.get(touch.theme)
        if extra:
            statements.append(
                f"Catalog flags for {touch.id}: " + ", ".join(extra)
            )
    return statements


def axis_penalty(card: CaseCard, mechanism: CandidateMechanism) -> tuple[int, list[str]]:
    """Qualitative down-rank when an axis collides with an infection theme.

    Penalty is a ranking heuristic, not a model parameter and not a dose cap.
    """
    notes: list[str] = []
    penalty = 0
    themes = {touch.theme.lower() for touch in card.nstg_touchpoints}
    touched = themes | {touch.id.lower() for touch in card.nstg_touchpoints}
    infectionish = any(
        any(token in item for token in _INFECTION_THEMES) for item in touched
    )
    if infectionish and mechanism.biologic_axis in _IMMUNE_AXES:
        penalty = 2
        notes.append(
            "NSTG infection / immunosuppression theme: immune-axis hypothesis "
            "is kept but down-ranked. This is not a contraindication and not "
            "a parameter."
        )
    return penalty, notes
