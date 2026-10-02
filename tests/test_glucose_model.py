import numpy as np
import pytest

from glucose_competition.analysis import REFERENCE, TIMES
from glucose_competition.gate import OPEN, STRUCTURAL, Experiment, decide
from glucose_competition.identifiability import observe, report
from glucose_competition.model import Params, endpoint, rhs, steady_states
from glucose_competition.regimes import classify, tumour_free_state


def test_state_stays_nonnegative():
    assert np.all(endpoint(Params(), [0.8, 0.5, 0.1]) >= 0)


def test_steady_states_are_roots():
    for y, _stable, _ev in steady_states(Params(), n_starts=30):
        assert np.max(np.abs(rhs(0, y, Params()))) < 1e-7


def test_tumour_free_closed_form_is_an_equilibrium():
    G, E, _ = tumour_free_state(REFERENCE)
    assert np.max(np.abs(rhs(0, [G, 0.0, E], REFERENCE))) < 1e-12


def test_reference_point_is_bistable():
    assert classify(REFERENCE, n_starts=150) == "bistable"


@pytest.mark.parametrize("c", [0.3, 3.0, 10.0])
def test_tumour_only_observation_has_exact_scaling_symmetry(c):
    q = REFERENCE.with_(v=REFERENCE.v / c, k=REFERENCE.k / c, s=REFERENCE.s * c)
    assert np.max(np.abs(observe(REFERENCE, TIMES, ("T",)) - observe(q, TIMES, ("T",)))) < 1e-7


def test_measuring_effectors_restores_full_rank():
    assert report(REFERENCE, TIMES, ("T",))["rank"] == 7
    assert report(REFERENCE, TIMES, ("T", "E"))["rank"] == 8


def test_gate_refuses_kill_rate_structurally_on_tumour_data():
    dec = decide(REFERENCE, Experiment(("T",), tuple(TIMES)), confirm_with_profile=False)
    assert dec.status["k"] == STRUCTURAL
    assert dec.opened() == []


def test_gate_never_opens_kill_rate_even_with_full_observation():
    dec = decide(REFERENCE, Experiment(("T", "G", "E"), tuple(TIMES)), confirm_with_profile=False)
    assert dec.status["k"] != OPEN
    assert "u" in dec.opened()
