import numpy as np
import pandas as pd

from bbme.components.gap import gap
from bbme.composite import Draws, bernoulli

RUCA_CLASSES = [(1, 3, "metro"), (4, 6, "micro"), (7, 9, "small_town"), (10, 10, "rural")]


def ruca_class(ruca_primary: pd.Series) -> pd.Series:
    out = pd.Series("unknown", index=ruca_primary.index)
    for lo, hi, name in RUCA_CLASSES:
        out[(ruca_primary >= lo) & (ruca_primary <= hi)] = name
    return out


def structures_per_unit_floor(df: pd.DataFrame, cfg: dict) -> pd.Series:
    """Low quantile of footprints per housing unit among ML-dominated tracts, per tract's stratum.

    Where Overture is almost all ML footprints its count is close to an ML-only product, so this
    floor is what a reference count per housing unit is unlikely to fall below. Strata with too
    few ML-dominated tracts fall back to the region, then to all regions.
    """
    b = cfg["building"]
    stratum = df["region"] + "/" + ruca_class(df["ruca_primary"])
    hu = df["acs_housing_units"]
    ml = (df["bld_ml_share"] >= b["ml_dominated_share"]) & (hu > 0) & (df["bld_n"] > 0)
    ratio = (df["bld_n"] / hu)[ml]
    q = b["hu_ratio_quantile"]
    pooled = ratio.quantile(q)
    by_region = ratio.groupby(df.loc[ml, "region"]).quantile(q)
    by_region = by_region[ratio.groupby(df.loc[ml, "region"]).size() >= b["min_ml_tracts"]]
    by_stratum = ratio.groupby(stratum[ml]).quantile(q)
    by_stratum = by_stratum[ratio.groupby(stratum[ml]).size() >= b["min_ml_tracts"]]
    return stratum.map(by_stratum).fillna(df["region"].map(by_region)).fillna(pooled)


def usfs_reference(df: pd.DataFrame, cfg: dict) -> tuple[np.ndarray, np.ndarray]:
    """H-B3: reference count k * U and the log-scale spread, learned on ML-dominated tracts.

    U is the USFS building count. Where Overture is almost all ML footprints its count stands in
    for the reference, so the region's median of N_O / U there gives k and the MAD of
    log(N_O / (k U)) gives the spread. Regions with too few such tracts use the pooled values.
    """
    b = cfg["building"]
    u = df[b["usfs_column"]].fillna(0).to_numpy(float)
    n = df["bld_n"].to_numpy(float)
    ml = ((df["bld_ml_share"] >= b["ml_dominated_share"]) & (u > 0) & (n > 0)).to_numpy()
    log_ratio = pd.Series(np.log(np.where(ml, n / np.where(u > 0, u, 1), np.nan)))
    region = df["region"].to_numpy()
    enough = log_ratio.groupby(region).count() >= b["min_ml_tracts"]
    centre = log_ratio.groupby(region).median().where(enough).fillna(log_ratio.median())
    mad = (log_ratio - pd.Series(region).map(centre)).abs().groupby(region).median()
    spread = 1.4826 * mad.where(enough).fillna(
        1.4826 * (log_ratio - log_ratio.median()).abs().median()
    )
    k = np.exp(pd.Series(region).map(centre).to_numpy())
    return k * u, pd.Series(region).map(spread).to_numpy()


def building_draws(df: pd.DataFrame, cfg: dict, rng: np.random.Generator, n_draws: int) -> Draws:
    """B as max(baseline, deficit against the per-unit floor); 1 where Overture has no footprint.

    The deficit term is used only when `use_hu_deficit` is set. With `reference: usfs` (H-B3)
    tracts with a USFS building count use E[gap(N_O, k U e^z)] instead, z ~ N(0, spread^2).
    """
    b = cfg["building"]
    n = df["bld_n"].to_numpy(float)
    hu = df["acs_housing_units"].fillna(0).to_numpy(float)
    deficit = np.zeros(len(df))
    if b["use_hu_deficit"]:
        floor = structures_per_unit_floor(df, cfg).to_numpy()
        deficit = np.where(hu > 0, np.nan_to_num(gap(n, floor * hu)), 0.0)
    point = np.where(n == 0, 1.0, np.maximum(b["baseline_gap"], deficit))
    p = np.where((n > 0) | (hu > 0), b["p_defined_with_evidence"], b["p_defined_without"])
    values = np.broadcast_to(point[:, None], (len(df), n_draws))
    if b["reference"] == "usfs":
        ref, spread = usfs_reference(df, cfg)
        noise = np.exp(spread[:, None] * rng.standard_normal((len(df), n_draws)))
        drawn = np.nan_to_num(gap(n[:, None], ref[:, None] * noise))
        values = np.where((ref > 0)[:, None], drawn, values)
        point = values.mean(axis=1)
    return Draws(values, bernoulli(rng, p, n_draws), point, p)
