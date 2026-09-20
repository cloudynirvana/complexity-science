"""Load and validate CaseCard YAML. No ODE import path."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml
from pydantic import ValidationError

from pathology_cases.schema import CaseCard
from pathology_cases.smuggling import ParameterSmugglingError, scan_for_smuggling

PACKAGE_DIR = Path(__file__).resolve().parent
CASES_DIR = PACKAGE_DIR / "cases"


class CaseCardError(ValueError):
    """Schema or smuggling failure while loading a CaseCard."""


def iter_case_paths(directory: Path | None = None) -> list[Path]:
    root = directory or CASES_DIR
    return sorted(
        path
        for path in root.glob("*.yaml")
        if not path.name.startswith("_")
    )


def load_raw(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    payload = yaml.safe_load(text)
    if payload is None:
        raise CaseCardError(f"{path}: empty YAML")
    return payload


def parse_case(payload: object, *, source: str = "<memory>") -> CaseCard:
    try:
        scan_for_smuggling(payload)
    except ParameterSmugglingError as exc:
        raise CaseCardError(f"{source}: {exc}") from exc
    try:
        return CaseCard.model_validate(payload)
    except ValidationError as exc:
        raise CaseCardError(f"{source}: {exc}") from exc


def load_case(path: Path | str) -> CaseCard:
    path = Path(path)
    return parse_case(load_raw(path), source=str(path))


def load_cases(directory: Path | None = None) -> list[CaseCard]:
    cards = [load_case(path) for path in iter_case_paths(directory)]
    if not cards:
        raise CaseCardError(f"no CaseCard YAML files in {directory or CASES_DIR}")
    return cards


def iter_named_cases(directory: Path | None = None) -> Iterable[tuple[Path, CaseCard]]:
    for path in iter_case_paths(directory):
        yield path, load_case(path)
