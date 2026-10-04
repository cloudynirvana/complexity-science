"""Unit tests for the model-agnostic gate, on models whose answer is known."""
import numpy as np

from evidence_gate.core import OPEN, STRUCTURAL, decide, report

TIMES = np.linspace(0.5, 5.0, 12)


def _decay(theta):
    """y = a exp(-b t): both parameters are identifiable from y alone."""
    return np.log(theta["a"] * np.exp(-theta["b"] * TIMES))


def _product(theta):
    """y = (a b) exp(-t): only the product is identifiable, so a and b are not."""
    return np.log(theta["a"] * theta["b"] * np.exp(-TIMES))


def test_identifiable_model_is_full_rank_and_opens():
    theta = {"a": 2.0, "b": 0.7}
    r = report(_decay, theta, list(theta), sigma=0.02)
    assert r["rank"] == 2
    assert decide(_decay, theta, sigma=0.02).opened() == ["a", "b"]


def test_product_degeneracy_is_caught_structurally():
    theta = {"a": 2.0, "b": 3.0}
    r = report(_product, theta, list(theta), sigma=0.02)
    assert r["rank"] == 1
    dec = decide(_product, theta, sigma=0.02)
    assert dec.status == {"a": STRUCTURAL, "b": STRUCTURAL}
    assert dec.opened() == []


def test_bound_tightens_as_noise_falls():
    theta = {"a": 2.0, "b": 0.7}
    loose = report(_decay, theta, list(theta), sigma=0.10)["cv"]["b"]
    tight = report(_decay, theta, list(theta), sigma=0.01)["cv"]["b"]
    assert tight < loose
    assert np.isclose(loose / tight, 10.0, rtol=0.05)


def test_verdict_depends_on_the_declared_experiment():
    theta = {"a": 2.0, "b": 0.7}
    assert decide(_decay, theta, sigma=0.01, confirm_with_profile=False).opened() == ["a", "b"]
    assert decide(_decay, theta, sigma=5.0, confirm_with_profile=False).opened() == []
