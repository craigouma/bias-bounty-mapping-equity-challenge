import numpy as np
import pandas as pd

from bbme.components.gap import gap, mean_defined
from bbme.composite import Draws


def _share(values: pd.Series, region: pd.Series) -> pd.Series:
    values = values.fillna(0).clip(lower=0)
    return values / values.groupby(region).transform("sum").replace(0, np.nan)


def facility_prior(df: pd.DataFrame, group: str, driver: str) -> np.ndarray:
    """Prior mean reference count: the region's Overture total for the type, spread by a driver.

    `pop_area` spreads half by population and half by land area (fire and EMS stations cover
    territory as well as people); `pop` spreads by population (schools).
    """
    pop = _share(df["pop_total"], df["region"])
    weight = pop if driver == "pop" else 0.5 * pop + 0.5 * _share(df["ALAND"], df["region"])
    total = df[f"poi_{group}"].groupby(df["region"]).transform("sum")
    return (total * weight.fillna(0)).to_numpy()


def _conditional(values: np.ndarray, flags: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = flags.sum(axis=1)
    point = np.divide(np.where(flags, values, 0).sum(axis=1), n, out=np.zeros(len(n)), where=n > 0)
    return point, flags.mean(axis=1)


def poi_draws(
    df: pd.DataFrame, cfg: dict, rng: np.random.Generator, n_draws: int
) -> tuple[Draws, dict[str, tuple[np.ndarray, np.ndarray]]]:
    """Draws of P and per-sub-gap (point, p_defined) for fire, EMS, schools and establishments.

    Facilities: reference count ~ Poisson(kappa_F * kappa_t * (w * o + (1 - w) * prior)), kappa_t
    being the expected reference facilities per Overture place of the type; the type is
    defined when the draw is at least 1 and its gap is gap(o, draw). Establishments: reference
    count = kappa_E * population with lognormal spread, undefined at zero population.
    P is the mean of the defined halves, the facilities half the mean of the defined types.
    """
    p = cfg["poi"]
    n = len(df)
    sub: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    fac_values, fac_flags = [], []
    for name, spec in p["facility_types"].items():
        observed = df[f"poi_{spec['group']}"].to_numpy(float)
        prior = facility_prior(df, spec["group"], spec["driver"])
        w = p["facility_weight"]
        lam = p["kappa_F"] * spec["kappa"] * (w * observed + (1 - w) * prior)
        ref = rng.poisson(lam[:, None], (n, n_draws)).astype(float)
        flags = ref >= 1
        values = np.nan_to_num(gap(observed[:, None], ref))
        sub[name] = _conditional(values, flags)
        fac_values.append(values)
        fac_flags.append(flags)
    facilities, fac_defined = mean_defined(np.stack(fac_values, 2), np.stack(fac_flags, 2), axis=2)

    pop = df["pop_total"].fillna(0).to_numpy(float)
    cbp = p["kappa_E"] * pop[:, None] * np.exp(p["sigma_E"] * rng.standard_normal((n, n_draws)))
    est = np.nan_to_num(gap(df["poi_n"].to_numpy(float)[:, None], cbp))
    est_defined = np.broadcast_to((pop > 0)[:, None], (n, n_draws))
    sub["cbp"] = _conditional(est, est_defined)

    values, flags = mean_defined(
        np.stack([facilities, est], 2), np.stack([fac_defined, est_defined], 2), axis=2
    )
    point, p_defined = _conditional(values, flags)
    return Draws(values, flags, point, p_defined), sub
