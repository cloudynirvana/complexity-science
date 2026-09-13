"""Class-level biologic effector catalog (not products)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any

from complexity_science.dynamics.ode import HostBurdenParams


@dataclass(frozen=True)
class Effector:
    id: str
    name: str
    class_label: str
    k_el: float
    immune_stim: float
    immune_deplete: float
    direct_clearance: float
    growth_suppress: float
    tox_direct: float
    tox_immune: float
    ec50_clearance: float
    ec50_immune: float
    provenance: dict[str, Any]
    nstg_notes: tuple[str, ...]

    def apply(self, base: HostBurdenParams, *, weight: float = 1.0) -> HostBurdenParams:
        """Overlay this class onto host params. ``weight`` scales PD gains, not k_el."""
        w = max(float(weight), 0.0)
        return base.with_updates(
            k_el=self.k_el,
            immune_stim=base.immune_stim + w * self.immune_stim,
            immune_deplete=base.immune_deplete + w * self.immune_deplete,
            direct_clearance=base.direct_clearance + w * self.direct_clearance,
            growth_suppress=base.growth_suppress + w * self.growth_suppress,
            tox_direct=base.tox_direct + w * self.tox_direct,
            tox_immune=base.tox_immune + w * self.tox_immune,
            ec50_clearance=self.ec50_clearance,
            ec50_immune=self.ec50_immune,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "class_label": self.class_label,
            "pkpd": {
                "k_el": self.k_el,
                "immune_stim": self.immune_stim,
                "immune_deplete": self.immune_deplete,
                "direct_clearance": self.direct_clearance,
                "growth_suppress": self.growth_suppress,
                "tox_direct": self.tox_direct,
                "tox_immune": self.tox_immune,
                "ec50_clearance": self.ec50_clearance,
                "ec50_immune": self.ec50_immune,
            },
            "provenance": self.provenance,
            "nstg_notes": list(self.nstg_notes),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Effector:
        pk = raw["pkpd"]
        return cls(
            id=str(raw["id"]),
            name=str(raw["name"]),
            class_label=str(raw["class_label"]),
            k_el=float(pk["k_el"]),
            immune_stim=float(pk["immune_stim"]),
            immune_deplete=float(pk["immune_deplete"]),
            direct_clearance=float(pk["direct_clearance"]),
            growth_suppress=float(pk["growth_suppress"]),
            tox_direct=float(pk["tox_direct"]),
            tox_immune=float(pk["tox_immune"]),
            ec50_clearance=float(pk["ec50_clearance"]),
            ec50_immune=float(pk["ec50_immune"]),
            provenance=dict(raw.get("provenance") or {}),
            nstg_notes=tuple(raw.get("nstg_notes") or ()),
        )


@lru_cache(maxsize=1)
def _raw_catalog() -> dict[str, Any]:
    payload = (
        resources.files("complexity_science.data")
        .joinpath("biologics_catalog.json")
        .read_text(encoding="utf-8")
    )
    return json.loads(payload)


def load_catalog() -> list[Effector]:
    raw = _raw_catalog()
    return [Effector.from_dict(item) for item in raw.get("effectors") or []]


def get_effector(effector_id: str) -> Effector:
    for item in load_catalog():
        if item.id == effector_id:
            return item
    known = ", ".join(item.id for item in load_catalog())
    raise KeyError(f"Unknown effector '{effector_id}'. Known: {known}")


def blend(effectors: list[tuple[Effector, float]], base: HostBurdenParams) -> HostBurdenParams:
    """Additive class overlay with per-class weights. Elimination uses the slowest k_el."""
    if not effectors:
        return base
    params = base
    k_el = min(item.k_el for item, _w in effectors)
    for effector, weight in effectors:
        params = effector.apply(params, weight=weight)
    return params.with_updates(k_el=k_el)
