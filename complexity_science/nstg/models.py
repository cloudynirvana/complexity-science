"""Dataclasses for the NSTG research index."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ConstraintHints:
    """Soft computational hints derived from an index entry — not care rules."""

    x_cap_scale: float = 1.0
    infection_risk_weight: float = 0.0
    max_immune_depletion_scale: float = 1.0
    flags: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> ConstraintHints:
        raw = raw or {}
        flags = tuple(raw.get("flags") or ())
        return cls(
            x_cap_scale=float(raw.get("x_cap_scale", 1.0)),
            infection_risk_weight=float(raw.get("infection_risk_weight", 0.0)),
            max_immune_depletion_scale=float(
                raw.get("max_immune_depletion_scale", 1.0)
            ),
            flags=flags,
        )


@dataclass(frozen=True)
class NstgEntry:
    id: str
    name: str
    category: str
    aliases: tuple[str, ...]
    themes: tuple[str, ...]
    cautions: tuple[str, ...]
    comorbidities: tuple[str, ...]
    constraint_hints: ConstraintHints
    status: str = "PLACEHOLDER_RESEARCH_INDEX"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "aliases": list(self.aliases),
            "themes": list(self.themes),
            "cautions": list(self.cautions),
            "comorbidities": list(self.comorbidities),
            "constraint_hints": {
                "x_cap_scale": self.constraint_hints.x_cap_scale,
                "infection_risk_weight": self.constraint_hints.infection_risk_weight,
                "max_immune_depletion_scale": (
                    self.constraint_hints.max_immune_depletion_scale
                ),
                "flags": list(self.constraint_hints.flags),
            },
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> NstgEntry:
        return cls(
            id=str(raw["id"]),
            name=str(raw["name"]),
            category=str(raw.get("category", "unknown")),
            aliases=tuple(raw.get("aliases") or ()),
            themes=tuple(raw.get("themes") or ()),
            cautions=tuple(raw.get("cautions") or ()),
            comorbidities=tuple(raw.get("comorbidities") or ()),
            constraint_hints=ConstraintHints.from_dict(raw.get("constraint_hints")),
        )
