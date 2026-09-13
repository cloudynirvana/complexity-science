"""JSON contract for future Project Confluence calls.

This module is a *seam*: inputs and outputs only. It does not import
Confluence, copy Confluence UI, or depend on connectome / flybody code.

Identity of this project remains complexity-science (attractors, multi-scale
dynamics, constrained pathway search). Confluence may later POST a
``ConfluenceRequest`` and receive a ``ConfluenceResponse``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from complexity_science.honesty import DISCLAIMER_SHORT, NON_CLAIMS
from complexity_science.pipeline import PipelineResult, run_pipeline

SCHEMA_ID = "complexity_science.confluence.v1"


@dataclass
class ConfluenceRequest:
    """Inbound contract (Confluence → this package)."""

    request_id: str
    archetype_id: str = "exhausted_high_burden"
    conditions: list[str] = field(default_factory=lambda: ["oncology_supportive"])
    horizon_days: float = 42.0
    max_candidates: int = 24
    allow_combinations: bool = True
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA_ID,
            "request_id": self.request_id,
            "query": {
                "archetype_id": self.archetype_id,
                "conditions": list(self.conditions),
                "horizon_days": self.horizon_days,
                "search": {
                    "max_candidates": self.max_candidates,
                    "allow_combinations": self.allow_combinations,
                },
            },
            "optional_context": {
                "notes": self.notes,
                "role": "research_bridge_not_cds",
            },
        }


@dataclass
class ConfluenceResponse:
    """Outbound contract (this package → Confluence)."""

    request_id: str
    status: str
    payload: dict[str, Any]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "schema": SCHEMA_ID,
            "request_id": self.request_id,
            "status": self.status,
            "disclaimer": DISCLAIMER_SHORT,
            "non_claims": list(NON_CLAIMS),
        }
        if self.status == "ok":
            body["result"] = self.payload
        else:
            body["error"] = self.error
        return body


def parse_request(raw: dict[str, Any]) -> ConfluenceRequest:
    query = raw.get("query") or {}
    search = query.get("search") or {}
    conditions = query.get("conditions") or ["oncology_supportive"]
    if isinstance(conditions, str):
        conditions = [part.strip() for part in conditions.split(",") if part.strip()]
    return ConfluenceRequest(
        request_id=str(raw.get("request_id") or uuid4()),
        archetype_id=str(query.get("archetype_id") or "exhausted_high_burden"),
        conditions=list(conditions),
        horizon_days=float(query.get("horizon_days") or 42.0),
        max_candidates=int(search.get("max_candidates") or 24),
        allow_combinations=bool(search.get("allow_combinations", True)),
        notes=str((raw.get("optional_context") or {}).get("notes") or ""),
    )


def from_pipeline_result(request_id: str, result: PipelineResult) -> ConfluenceResponse:
    return ConfluenceResponse(
        request_id=request_id,
        status="ok",
        payload=result.to_dict(),
    )


def to_confluence_payload(result: PipelineResult, *, request_id: str | None = None) -> dict[str, Any]:
    """Wrap a local run in the outbound contract."""
    rid = request_id or f"local-{result.created_at}"
    return from_pipeline_result(rid, result).to_dict()


def execute_request(raw: dict[str, Any]) -> dict[str, Any]:
    """Convenience: parse, run, wrap. Still no Confluence import."""
    try:
        req = parse_request(raw)
        result = run_pipeline(
            archetype_id=req.archetype_id,
            conditions=req.conditions,
            horizon_days=req.horizon_days,
            allow_combinations=req.allow_combinations,
            max_candidates=req.max_candidates,
        )
        return from_pipeline_result(req.request_id, result).to_dict()
    except Exception as exc:  # noqa: BLE001
        return ConfluenceResponse(
            request_id=str(raw.get("request_id") or "unknown"),
            status="error",
            payload={},
            error=f"{type(exc).__name__}: {exc}",
        ).to_dict()


# Example documents for humans reading the seam.
EXAMPLE_REQUEST: dict[str, Any] = ConfluenceRequest(
    request_id="example-req-001",
    archetype_id="comorbidity_constrained",
    conditions=["malaria", "hiv", "sickle_cell", "anaemia"],
    horizon_days=42.0,
    notes="research only",
).to_dict()

EXAMPLE_RESPONSE_SHAPE: dict[str, Any] = {
    "schema": SCHEMA_ID,
    "request_id": "example-req-001",
    "status": "ok",
    "disclaimer": DISCLAIMER_SHORT,
    "non_claims": list(NON_CLAIMS),
    "result": {
        "schema": "complexity_science.report.v1",
        "archetype": {"id": "comorbidity_constrained"},
        "nstg": {"hits": ["…"]},
        "constraints": {"x_cap": "float", "flags": ["…"]},
        "hypotheses": ["ranked in-silico hypotheses"],
        "falsification_checklist": ["…"],
    },
}


def contract_doc() -> str:
    return (
        "Confluence seam v1: POST ConfluenceRequest JSON, receive "
        "ConfluenceResponse JSON. No shared UI. No shared runtime. "
        "Honesty fields are mandatory on every successful payload."
    )
