import numpy as np

from evidence_gate.core import decide
from malaria_clearance.analysis import NAMES, REFERENCE, observer
from malaria_clearance.model import (Params, circulating_fraction, clearance_half_life,
                                     initial_distribution, simulate)


def test_parasite_counts_stay_finite_and_nonnegative():
    _t, P = simulate(REFERENCE, hours=96)
    assert np.all(np.isfinite(P)) and np.all(P >= 0)


def test_only_young_parasites_circulate():
    f = circulating_fraction(REFERENCE)
    assert f[0] > 0.99 and f[-1] < 0.01
    assert np.all(np.diff(f) <= 0)


def test_initial_distribution_is_stable_for_extreme_parameters():
    # A very narrow or displaced distribution must not underflow during a fit.
    for p in (REFERENCE.with_(sd0=0.05), REFERENCE.with_(mu0=47.0), REFERENCE.with_(mu0=0.2)):
        d = initial_distribution(p)
        assert np.isfinite(d).all() and d.sum() > 0


def test_reduced_ring_killing_prolongs_clearance():
    fast = clearance_half_life(REFERENCE.with_(k_ring=1.0))
    slow = clearance_half_life(REFERENCE.with_(k_ring=0.05))
    assert 1.5 < fast < 2.5          # published fastest half-lives are ~1.9 h
    assert slow > fast


def test_half_life_confounds_ring_killing_with_staging():
    # The same half-life is reachable with very different ring-stage killing.
    target = clearance_half_life(REFERENCE)
    matches = []
    for mu in np.linspace(2, 26, 25):
        for k in np.logspace(np.log10(0.02), 0, 30):
            t = clearance_half_life(REFERENCE.with_(k_ring=float(k), mu0=float(mu)))
            if np.isfinite(t) and abs(t - target) < 0.05:
                matches.append(k)
    assert matches and max(matches) / min(matches) > 10


def test_standard_protocol_refuses_the_resistance_parameter():
    obs, _ts = observer(("circ",), 6, 48)
    dec = decide(obs, REFERENCE.as_dict(), NAMES, sigma=0.20, confirm_with_profile=False)
    assert dec.status["k_ring"].startswith("refused")
    assert dec.opened() == []


def test_enriched_design_identifies_staging_but_not_killing():
    obs, _ts = observer(("circ", "stage"), 4, 72)
    dec = decide(obs, REFERENCE.as_dict(), NAMES, sigma=0.20, confirm_with_profile=False)
    assert "a_seq" in dec.opened()
    assert dec.status["k_ring"].startswith("refused")
