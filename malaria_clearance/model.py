"""Age-structured within-host Plasmodium falciparum model under artemisinin.

Biology encoded (all of it published; none of it fitted here):

* The asexual cycle lasts ~48 h. Parasites age, then burst and re-invade with a
  parasite multiplication rate `pmr`.
* Only young (ring) stages circulate. Mature stages sequester in the
  microvasculature, so a blood film counts circulating parasites only. The
  circulating fraction is modelled as a smooth logistic fall around `a_seq`.
* Artemisinin killing is stage-specific and concentration-dependent. Reduced
  *ring-stage* killing is the proposed basis of artemisinin partial resistance.
* Dihydroartemisinin is eliminated fast (hour-scale), so exposure is a daily
  spike, not a plateau.

State is the parasite age distribution over 48 one-hour bins, in parasites/uL.
Units are hours and parasites/uL. No parameter here is fitted to patient data;
the model exists to ask what a clearance curve could identify.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace

import numpy as np

CYCLE = 48  # hours
AGES = np.arange(CYCLE) + 0.5  # bin midpoints, 0.5 .. 47.5 h


@dataclass(frozen=True)
class Params:
    k_ring: float = 0.10    # max kill rate of ring stages (/h)
    k_mature: float = 0.55  # max kill rate of mature stages (/h)
    ec50: float = 0.30      # concentration at half-maximal killing (arb. units)
    pmr: float = 8.0        # parasite multiplication rate per cycle
    mu0: float = 12.0       # mean age of the initial parasite population (h)
    sd0: float = 6.0        # spread of the initial age distribution (h)
    a_seq: float = 26.0     # age at which parasites sequester (h)
    ke: float = 0.69        # drug elimination rate (/h), t1/2 ~ 1 h

    def with_(self, **kw) -> "Params":
        return replace(self, **kw)

    def as_dict(self) -> dict:
        return asdict(self)


def kill_profile(p: Params) -> np.ndarray:
    """Max kill rate by parasite age: rings, then mature stages, smoothly joined."""
    w = 2.0
    ring_weight = 1.0 / (1.0 + np.exp((AGES - 26.0) / w))
    return p.k_ring * ring_weight + p.k_mature * (1.0 - ring_weight)


def circulating_fraction(p: Params) -> np.ndarray:
    """Fraction of parasites of each age that are still in circulation."""
    return 1.0 / (1.0 + np.exp((AGES - p.a_seq) / 1.5))


def concentration(t, p: Params, doses=(0.0, 24.0, 48.0), dose=1.0):
    """Drug concentration: an instantaneous input at each dose, then decay."""
    t = np.atleast_1d(np.asarray(t, float))
    c = np.zeros_like(t)
    for td in doses:
        m = t >= td
        c[m] += dose * np.exp(-p.ke * (t[m] - td))
    return c


def initial_distribution(p: Params, total=50_000.0) -> np.ndarray:
    """Gaussian age distribution, wrapped to the cycle, scaled to `total` parasites/uL."""
    # Stabilised: the exponent is shifted before exponentiating, so a very narrow
    # or far-displaced distribution cannot underflow to all zeros during a fit.
    z = -0.5 * ((AGES - p.mu0) / max(p.sd0, 1e-6)) ** 2
    d = np.exp(z - z.max())
    return total * d / d.sum()


def simulate(p: Params, hours=48, total0=50_000.0, substeps=12):
    """Hourly march of the age distribution. Returns (times, P[t, age])."""
    P = initial_distribution(p, total0)
    kmax = kill_profile(p)
    out = [P.copy()]
    for h in range(hours):
        # Average killing over the hour, sampled finely because the drug decays fast.
        ts = h + (np.arange(substeps) + 0.5) / substeps
        c = concentration(ts, p)
        eff = (c / (c + p.ec50)).mean()
        P = P * np.exp(-kmax * eff)
        # Age by one hour; the oldest bin bursts and re-invades.
        burst = P[-1]
        P = np.roll(P, 1)
        P[0] = p.pmr * burst
        out.append(P.copy())
    return np.arange(hours + 1, dtype=float), np.array(out)


def observables(p: Params, times, which=("circ",), hours=None, total0=50_000.0):
    """Log-observations at integer `times`.

    circ  — circulating parasitaemia, i.e. what a blood film actually counts
    stage — mean age of circulating parasites, i.e. ring/trophozoite composition
    total — total parasite biomass, circulating plus sequestered (not clinically
            observable; included only to show what it would buy)
    """
    times = np.asarray(times, float)
    hours = int(times.max()) if hours is None else hours
    t, P = simulate(p, hours=hours, total0=total0)
    idx = np.searchsorted(t, times)
    f = circulating_fraction(p)
    circ = (P * f).sum(axis=1)
    out = []
    for name in which:
        if name == "circ":
            v = circ[idx]
        elif name == "total":
            v = P.sum(axis=1)[idx]
        elif name == "stage":
            num = (P * f * AGES).sum(axis=1)
            v = (num / np.maximum(circ, 1e-300))[idx]
        else:
            raise ValueError(name)
        out.append(np.log(np.maximum(v, 1e-300)))
    return np.concatenate(out)


def clearance_half_life(p: Params, hours=48, total0=50_000.0, lod=10.0):
    """Slope half-life of log circulating parasitaemia, as therapeutic-efficacy
    studies report it.

    The log-linear decline is fitted between the peak of the observed curve (so
    any initial lag is excluded) and the first of: the curve's minimum, or the
    point where it falls below the detection limit `lod`. Re-invasion after the
    nadir is excluded, as it is in practice. This follows the intent of the
    WWARN parasite clearance estimator, not its implementation.
    """
    t, P = simulate(p, hours=hours, total0=total0)
    circ = (P * circulating_fraction(p)).sum(axis=1)
    y = np.log(np.maximum(circ, 1e-300))
    start = int(np.argmax(y))
    stop = start + int(np.argmin(y[start:]))
    below = np.where(circ[start:] < lod)[0]
    if below.size:
        stop = min(stop, start + int(below[0]))
    if stop - start < 3:
        return np.nan
    tt, yy = t[start:stop + 1], y[start:stop + 1]
    slope = np.polyfit(tt, yy, 1)[0]
    return np.nan if slope >= 0 else np.log(2) / -slope
