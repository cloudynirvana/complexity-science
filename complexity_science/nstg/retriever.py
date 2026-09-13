"""Condition → themes / cautions / comorbidities research retriever."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from importlib import resources
from typing import Any, Iterable, Sequence

from complexity_science.nstg.models import ConstraintHints, NstgEntry


def _normalize(text: str) -> str:
    return " ".join(text.lower().replace("_", " ").replace("-", " ").split())


@lru_cache(maxsize=1)
def load_default_index() -> dict[str, Any]:
    payload = (
        resources.files("complexity_science.data")
        .joinpath("nstg_index.json")
        .read_text(encoding="utf-8")
    )
    return json.loads(payload)


@dataclass
class RetrievalHit:
    entry: NstgEntry
    score: float
    matched_on: str

    def to_dict(self) -> dict[str, Any]:
        data = self.entry.to_dict()
        data["score"] = self.score
        data["matched_on"] = self.matched_on
        return data


@dataclass
class RetrievalResult:
    query: tuple[str, ...]
    hits: list[RetrievalHit]
    provenance: dict[str, Any]
    unmatched: list[str] = field(default_factory=list)

    def entries(self) -> list[NstgEntry]:
        return [hit.entry for hit in self.hits]

    def merged_hints(self) -> ConstraintHints:
        """Intersect scales (min) and union flags — conservative for research."""
        if not self.hits:
            return ConstraintHints()
        x_cap = min(h.entry.constraint_hints.x_cap_scale for h in self.hits)
        infect = max(h.entry.constraint_hints.infection_risk_weight for h in self.hits)
        deplete = min(
            h.entry.constraint_hints.max_immune_depletion_scale for h in self.hits
        )
        flags: list[str] = []
        for hit in self.hits:
            for flag in hit.entry.constraint_hints.flags:
                if flag not in flags:
                    flags.append(flag)
        return ConstraintHints(
            x_cap_scale=x_cap,
            infection_risk_weight=infect,
            max_immune_depletion_scale=deplete,
            flags=tuple(flags),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": list(self.query),
            "unmatched": list(self.unmatched),
            "provenance": self.provenance,
            "merged_hints": {
                "x_cap_scale": self.merged_hints().x_cap_scale,
                "infection_risk_weight": self.merged_hints().infection_risk_weight,
                "max_immune_depletion_scale": (
                    self.merged_hints().max_immune_depletion_scale
                ),
                "flags": list(self.merged_hints().flags),
            },
            "hits": [hit.to_dict() for hit in self.hits],
        }


class NstgRetriever:
    """In-memory research index. Not a point-of-care NSTG lookup."""

    def __init__(self, index: dict[str, Any] | None = None) -> None:
        raw = index if index is not None else load_default_index()
        self.provenance = dict(raw.get("provenance") or {})
        self.status = str(raw.get("status", "PLACEHOLDER_RESEARCH_INDEX"))
        self.entries: list[NstgEntry] = [
            NstgEntry.from_dict(item) for item in raw.get("entries") or []
        ]
        self._by_id = {entry.id: entry for entry in self.entries}

    def get(self, condition_id: str) -> NstgEntry | None:
        return self._by_id.get(condition_id)

    def list_ids(self) -> list[str]:
        return [entry.id for entry in self.entries]

    def retrieve(self, conditions: Sequence[str] | str) -> RetrievalResult:
        if isinstance(conditions, str):
            queries = [part.strip() for part in conditions.split(",") if part.strip()]
        else:
            queries = [str(item).strip() for item in conditions if str(item).strip()]
        if not queries:
            queries = ["oncology_supportive"]

        hits: list[RetrievalHit] = []
        unmatched: list[str] = []
        seen: set[str] = set()
        for query in queries:
            hit = self._match_one(query)
            if hit is None:
                unmatched.append(query)
                continue
            if hit.entry.id in seen:
                continue
            seen.add(hit.entry.id)
            hits.append(hit)
        return RetrievalResult(
            query=tuple(queries),
            hits=hits,
            unmatched=unmatched,
            provenance={
                **self.provenance,
                "index_status": self.status,
                "role": "research_index_not_cds",
            },
        )

    def _match_one(self, query: str) -> RetrievalHit | None:
        needle = _normalize(query)
        if not needle:
            return None
        if needle in self._by_id:
            return RetrievalHit(self._by_id[needle], 1.0, "id")
        # compact id form (sickle cell → sickle_cell)
        compact = needle.replace(" ", "_")
        if compact in self._by_id:
            return RetrievalHit(self._by_id[compact], 0.98, "id_compact")
        best: RetrievalHit | None = None
        for entry in self.entries:
            candidates: Iterable[tuple[str, str]] = (
                (entry.id, "id_substr"),
                (entry.name, "name"),
                *[(alias, "alias") for alias in entry.aliases],
            )
            for text, kind in candidates:
                norm = _normalize(text)
                if needle == norm:
                    return RetrievalHit(entry, 0.95, kind)
                if needle in norm or norm in needle:
                    score = 0.7 + 0.2 * (min(len(needle), len(norm)) / max(len(norm), 1))
                    if best is None or score > best.score:
                        best = RetrievalHit(entry, score, kind)
        return best
