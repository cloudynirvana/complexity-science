import numpy as np

from complexity_science.dynamics.archetypes import get_archetype, list_archetypes
from complexity_science.dynamics.simulate import Schedule, simulate


def test_three_archetypes_exist():
    ids = {item.id for item in list_archetypes()}
    assert ids == {
        "exhausted_high_burden",
        "inflammatory_fragile",
        "comorbidity_constrained",
    }


def test_untreated_trajectory_finite_and_nonnegative():
    arch = get_archetype("exhausted_high_burden")
    traj = simulate(arch.params, arch.y0, horizon_days=21.0)
    assert traj.success
    assert np.all(np.isfinite(traj.y))
    assert np.all(traj.y >= -1e-12)
    assert traj.b[-1] > 0.2  # endemic-ish basin, not a miracle collapse


def test_pulsed_infusion_changes_exposure():
    arch = get_archetype("inflammatory_fragile")
    off = simulate(
        arch.params,
        arch.y0,
        horizon_days=14.0,
        schedule=Schedule(kind="continuous", intensity=0.0),
    )
    on = simulate(
        arch.params,
        arch.y0,
        horizon_days=14.0,
        schedule=Schedule(kind="pulsed", intensity=1.0, period_days=7.0, duty=0.4),
    )
    assert off.success and on.success
    assert on.metrics()["e_auc"] > off.metrics()["e_auc"]
