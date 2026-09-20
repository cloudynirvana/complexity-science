"""Export the CaseCard JSON Schema for non-Python contributors."""

from __future__ import annotations

import json
from pathlib import Path

from pathology_cases.schema import CaseCard

SCHEMA_PATH = Path(__file__).resolve().parent / "schema" / "case_card.schema.json"


def case_card_json_schema() -> dict:
    schema = CaseCard.model_json_schema()
    schema["title"] = "CaseCard"
    schema["description"] = (
        "In-silico research CaseCard. Knowledge, evidence pointers, "
        "mechanisms, falsifiers, and NSTG constraints — never parameters."
    )
    return schema


def write_json_schema(path: Path | None = None) -> Path:
    target = path or SCHEMA_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(case_card_json_schema(), indent=2) + "\n",
        encoding="utf-8",
    )
    return target
