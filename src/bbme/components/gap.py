import numpy as np


def gap(overture: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Capped coverage gap max(0, 1 - O / R); NaN where the reference is zero (undefined)."""
    overture = np.asarray(overture, dtype=float)
    reference = np.asarray(reference, dtype=float)
    ratio = np.divide(
        overture, reference, out=np.full(reference.shape, np.nan), where=reference > 0
    )
    return np.where(reference > 0, np.clip(1.0 - ratio, 0.0, 1.0), np.nan)


def defined(reference: np.ndarray) -> np.ndarray:
    return np.asarray(reference, dtype=float) > 0


def mean_defined(
    values: np.ndarray, is_defined: np.ndarray, axis: int
) -> tuple[np.ndarray, np.ndarray]:
    """Mean over the defined entries along `axis`, and whether any entry was defined.

    Undefined entries never enter the mean: the divisor is the number of defined entries.
    Where nothing is defined the mean is 0, the organisers' convention for "nothing to compare".
    """
    values = np.where(is_defined, values, 0.0)
    n = is_defined.sum(axis=axis)
    out = np.divide(values.sum(axis=axis), n, out=np.zeros(n.shape), where=n > 0)
    return out, n > 0
