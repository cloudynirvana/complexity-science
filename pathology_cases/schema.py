"""CaseCard schema — the only object a contributor must author.

Layers that belong here: knowledge, cited pointers, candidate mechanisms,
falsifiers, qualitative NSTG constraints.

Layers that do not belong here: parameters, predictions, patient data.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from pathology_cases.honesty import DISCLAIMER_SHORT, disclaimer_gaps

SCHEMA_VERSION = "1.0.0"

ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
FAKE_DOI_RE = re.compile(r"10\.0{3,}/|fake|placeholder|example\.com|xxx", re.I)

AxisLayer = Literal[
    "metabolism",
    "immunity",
    "stroma",
    "hypoxia",
    "vasculature",
    "invasion",
    "dormancy",
    "host",
]
AxisRole = Literal["driver", "constraint", "context"]
BiologicAxis = Literal[
    "metabolic_checkpoint",
    "immune_exclusion",
    "immune_checkpoint",
    "stromal_barrier",
    "hypoxia_adaptation",
    "invasive_niche",
    "vascular_delivery",
    "dormancy_maintenance",
    "dormancy_awakening",
    "host_comorbidity",
]
CitationKind = Literal["review", "primary", "guideline", "policy"]
CitationEpistemic = Literal["knowledge", "evidence"]


def _check_id(value: str, *, field: str) -> str:
    if not ID_RE.match(value):
        raise ValueError(f"{field} must be snake_case starting with a letter: {value!r}")
    return value


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Disease(_Strict):
    name: str = Field(min_length=3)
    abbreviations: list[str] = Field(default_factory=list)
    framing: str = Field(min_length=12)
    notes: str = ""


class SystemicAxis(_Strict):
    id: str
    layer: AxisLayer
    description: str = Field(min_length=12)
    role: AxisRole

    @field_validator("id")
    @classmethod
    def _id(cls, value: str) -> str:
        return _check_id(value, field="systemic_axes.id")


class Observable(_Strict):
    id: str
    name: str = Field(min_length=3)
    modality: str = Field(min_length=3)
    research_only: Literal[True] = True
    notes: str = ""

    @field_validator("id")
    @classmethod
    def _id(cls, value: str) -> str:
        return _check_id(value, field="observables.id")


class CandidateMechanism(_Strict):
    id: str
    statement: str = Field(min_length=24)
    biologic_axis: BiologicAxis
    supporting_citation_ids: list[str] = Field(min_length=1)
    nstg_touchpoint_ids: list[str] = Field(default_factory=list)
    status: Literal["hypothesis"] = "hypothesis"

    @field_validator("id")
    @classmethod
    def _id(cls, value: str) -> str:
        return _check_id(value, field="candidate_mechanisms.id")


class Falsifier(_Strict):
    id: str
    if_observed: str = Field(min_length=12)
    then_reject: str = Field(min_length=12)
    mechanism_ids: list[str] = Field(min_length=1)

    @field_validator("id")
    @classmethod
    def _id(cls, value: str) -> str:
        return _check_id(value, field="falsifiers.id")


class NstgTouchpoint(_Strict):
    """Qualitative constraint only. No numeric scales. NSTG text is not copied."""

    id: str
    theme: str = Field(min_length=3)
    constraint_statement: str = Field(min_length=24)
    source_citation_id: str
    role: Literal["constraint"] = "constraint"

    @field_validator("id")
    @classmethod
    def _id(cls, value: str) -> str:
        return _check_id(value, field="nstg_touchpoints.id")


class Citation(_Strict):
    id: str
    vancouver: str = Field(min_length=20)
    doi: str | None = None
    pmid: str | None = None
    kind: CitationKind
    epistemic: CitationEpistemic

    @field_validator("id")
    @classmethod
    def _id(cls, value: str) -> str:
        return _check_id(value, field="citations.id")

    @field_validator("doi")
    @classmethod
    def _doi(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not DOI_RE.match(value) or FAKE_DOI_RE.search(value):
            raise ValueError(f"DOI looks invalid or placeholder: {value!r}")
        return value

    @field_validator("pmid")
    @classmethod
    def _pmid(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not value.isdigit():
            raise ValueError(f"pmid must be digits only: {value!r}")
        return value

    @model_validator(mode="after")
    def _guideline_may_omit_doi(self) -> Citation:
        if self.kind in {"guideline", "policy"}:
            return self
        if self.doi is None:
            raise ValueError(
                f"citation {self.id}: primary/review sources must include a real DOI"
            )
        return self


class CaseCard(_Strict):
    schema_version: Literal["1.0.0"] = SCHEMA_VERSION
    id: str
    title: str = Field(min_length=8)
    disease: Disease
    systemic_axes: list[SystemicAxis] = Field(min_length=2)
    observables: list[Observable] = Field(min_length=2)
    candidate_mechanisms: list[CandidateMechanism] = Field(min_length=2)
    falsifiers: list[Falsifier] = Field(min_length=2)
    nstg_touchpoints: list[NstgTouchpoint] = Field(min_length=1)
    citations: list[Citation] = Field(min_length=3)
    disclaimer: str = Field(min_length=40)

    @field_validator("id")
    @classmethod
    def _id(cls, value: str) -> str:
        return _check_id(value, field="id")

    @field_validator("disclaimer")
    @classmethod
    def _disclaimer(cls, value: str) -> str:
        gaps = disclaimer_gaps(value)
        if gaps:
            raise ValueError(
                "disclaimer is missing required honesty phrases: " + ", ".join(gaps)
            )
        return value

    @model_validator(mode="after")
    def _cross_links(self) -> CaseCard:
        citation_ids = {item.id for item in self.citations}
        touch_ids = {item.id for item in self.nstg_touchpoints}
        mechanism_ids = {item.id for item in self.candidate_mechanisms}
        axis_ids = [item.id for item in self.systemic_axes]
        obs_ids = [item.id for item in self.observables]
        _unique("systemic_axes.id", axis_ids)
        _unique("observables.id", obs_ids)
        _unique("candidate_mechanisms.id", list(mechanism_ids))
        _unique("falsifiers.id", [item.id for item in self.falsifiers])
        _unique("nstg_touchpoints.id", list(touch_ids))
        _unique("citations.id", list(citation_ids))

        for mechanism in self.candidate_mechanisms:
            missing = set(mechanism.supporting_citation_ids) - citation_ids
            if missing:
                raise ValueError(
                    f"mechanism {mechanism.id} cites unknown ids: {sorted(missing)}"
                )
            missing_t = set(mechanism.nstg_touchpoint_ids) - touch_ids
            if missing_t:
                raise ValueError(
                    f"mechanism {mechanism.id} nstg_touchpoint_ids unknown: "
                    f"{sorted(missing_t)}"
                )

        for touch in self.nstg_touchpoints:
            if touch.source_citation_id not in citation_ids:
                raise ValueError(
                    f"nstg_touchpoint {touch.id} source_citation_id "
                    f"{touch.source_citation_id!r} is not in citations"
                )

        covered: set[str] = set()
        for falsifier in self.falsifiers:
            missing_m = set(falsifier.mechanism_ids) - mechanism_ids
            if missing_m:
                raise ValueError(
                    f"falsifier {falsifier.id} mechanism_ids unknown: "
                    f"{sorted(missing_m)}"
                )
            covered.update(falsifier.mechanism_ids)

        uncovered = mechanism_ids - covered
        if uncovered:
            raise ValueError(
                "every candidate mechanism needs at least one falsifier; missing: "
                + ", ".join(sorted(uncovered))
            )
        return self

    def mechanism_map(self) -> dict[str, CandidateMechanism]:
        return {item.id: item for item in self.candidate_mechanisms}

    def citation_map(self) -> dict[str, Citation]:
        return {item.id: item for item in self.citations}


def _unique(label: str, values: list[str]) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label}")


def default_disclaimer() -> str:
    return DISCLAIMER_SHORT
