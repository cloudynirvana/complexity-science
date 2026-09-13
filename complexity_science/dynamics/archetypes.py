"""Computational archetypes — basins, not diagnoses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from complexity_science.dynamics.ode import HostBurdenParams


@dataclass(frozen=True)
class Archetype:
    id: str
    name: str
    summary: str
    params: HostBurdenParams
    y0: tuple[float, float, float, float]
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "summary": self.summary,
            "y0": {"B": self.y0[0], "I": self.y0[1], "X": self.y0[2], "E": self.y0[3]},
            "notes": list(self.notes),
            "kind": "computational_basin_not_diagnosis",
        }


def _exhausted() -> Archetype:
    return Archetype(
        id="exhausted_high_burden",
        name="Exhausted high-burden basin",
        summary=(
            "High initial burden, suppressed immune setpoint coupling, and "
            "strong burden-on-immune inhibition. A computational stand-in for "
            "an immune-weary high-load attractor — not a named cancer."
        ),
        params=HostBurdenParams(
            r=0.34,
            i_star=0.55,
            gamma_b=3.6,
            eps_i=0.22,
            alpha_i=1.1,
        ),
        y0=(0.72, 0.22, 0.18, 0.0),
        notes=(
            "Untreated trajectories typically remain in a high-B endemic region.",
            "Checkpoint-like classes act mainly by lifting I, not by direct kill.",
        ),
    )


def _inflammatory() -> Archetype:
    return Archetype(
        id="inflammatory_fragile",
        name="Inflammatory-fragile basin",
        summary=(
            "Moderate burden with elevated host-stress coupling: toxicity "
            "feeds back onto immune decline (η_X, χ terms). Not a clinical "
            "inflammatory-disease diagnosis."
        ),
        params=HostBurdenParams(
            r=0.24,
            chi_b=0.22,
            eta_x=1.6,
            delta_x=0.12,
            alpha_x=0.7,
            i_star=0.8,
        ),
        y0=(0.42, 0.48, 0.36, 0.0),
        notes=(
            "High χ_IE effectors can enter a toxic-stress regime.",
            "Useful for testing whether a rank is bought with peak X.",
        ),
    )


def _comorbidity() -> Archetype:
    return Archetype(
        id="comorbidity_constrained",
        name="Comorbidity-constrained basin",
        summary=(
            "Reduced immune setpoint and slower toxicity clearance — a "
            "computational host with less reserve. Pair with NSTG comorbidity "
            "queries (malaria, HIV, sickle cell, anaemia). Not a patient."
        ),
        params=HostBurdenParams(
            r=0.26,
            i_star=0.48,
            sigma=0.14,
            delta_x=0.1,
            gamma_b=2.8,
            eps_i=0.28,
        ),
        y0=(0.55, 0.3, 0.22, 0.0),
        notes=(
            "Search should usually bind a tighter X cap from the NSTG index.",
            "Do not map I_star to CD4, haemoglobin, or parasite density.",
        ),
    )


_REGISTRY: dict[str, Archetype] = {
    item.id: item
    for item in (_exhausted(), _inflammatory(), _comorbidity())
}


def list_archetypes() -> list[Archetype]:
    return list(_REGISTRY.values())


def get_archetype(archetype_id: str) -> Archetype:
    try:
        return _REGISTRY[archetype_id]
    except KeyError as exc:
        known = ", ".join(_REGISTRY)
        raise KeyError(f"Unknown archetype '{archetype_id}'. Known: {known}") from exc
