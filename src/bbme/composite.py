from dataclasses import dataclass
from itertools import combinations

import numpy as np

from bbme.components.gap import mean_defined

COMPONENTS = ("transport", "building", "poi")


@dataclass
class Draws:
    """Joint predictive draws for one component across tracts.

    `values` and `defined` are (n, S); `values` is ignored where `defined` is false. `point`
    is the plug-in gap given the component is defined, `p_defined` its definedness probability.
    """

    values: np.ndarray
    defined: np.ndarray
    point: np.ndarray
    p_defined: np.ndarray


def plug_in(draws: dict[str, Draws]) -> np.ndarray:
    """Hard definedness (p >= 0.5) and point estimates; the likeliest component if none pass."""
    p = np.stack([draws[c].p_defined for c in COMPONENTS], axis=1)
    point = np.stack([draws[c].point for c in COMPONENTS], axis=1)
    flags = p >= 0.5
    none = ~flags.any(axis=1)
    flags[none, p[none].argmax(axis=1)] = True
    return mean_defined(point, flags, axis=1)[0]


def monte_carlo(draws: dict[str, Draws]) -> tuple[np.ndarray, np.ndarray]:
    """E[y | at least one component defined] from joint draws, and the kept-draw count.

    Each draw takes the mean of its defined components, so the divisor varies per draw. Draws
    with every component undefined are discarded: every scored tract has at least one defined
    component, so the expectation is conditional on that event. A tract that keeps no draw
    falls back to the plug-in value.
    """
    values = np.stack([draws[c].values for c in COMPONENTS], axis=2)
    flags = np.stack([draws[c].defined for c in COMPONENTS], axis=2)
    per_draw, kept = mean_defined(values, flags, axis=2)
    n_kept = kept.sum(axis=1)
    total = np.where(kept, per_draw, 0.0).sum(axis=1)
    y = np.divide(total, n_kept, out=plug_in(draws), where=n_kept > 0)
    return y, n_kept


def analytic(p_defined: np.ndarray, mean_given_defined: np.ndarray) -> np.ndarray:
    """Exact E[y | at least one defined] when components are mutually independent.

    Sums over the seven non-empty definedness patterns; inputs are (n, 3).
    """
    n, k = p_defined.shape
    num = np.zeros(n)
    for size in range(1, k + 1):
        for subset in combinations(range(k), size):
            mask = np.zeros(k, dtype=bool)
            mask[list(subset)] = True
            prob = np.prod(np.where(mask, p_defined, 1 - p_defined), axis=1)
            num += prob * mean_given_defined[:, mask].mean(axis=1)
    p_any = 1 - np.prod(1 - p_defined, axis=1)
    return np.divide(num, p_any, out=np.zeros(n), where=p_any > 0)


def bernoulli(rng: np.random.Generator, p: np.ndarray, n_draws: int) -> np.ndarray:
    return rng.random((len(p), n_draws)) < p[:, None]


def shrink(y: np.ndarray, alpha: float) -> np.ndarray:
    return np.clip(alpha * y + (1 - alpha) * y.mean(), 0.0, 1.0)
