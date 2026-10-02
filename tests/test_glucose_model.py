import numpy as np

from glucose_competition.model import Params, endpoint, rhs, steady_states


def test_state_stays_nonnegative():
    y = endpoint(Params(), [0.8, 0.5, 0.1])
    assert np.all(y >= 0)


def test_steady_states_are_roots():
    for y, _stable, _ev in steady_states(Params(), n_starts=30):
        assert np.max(np.abs(rhs(0, y, Params()))) < 1e-7


def test_tumour_free_state_exists_without_tumour():
    # With T=0 the glucose and effector equations must settle to a fixed point.
    y = endpoint(Params(), [0.8, 0.0, 0.1])
    assert y[1] == 0.0
