import numpy as np
import pandas as pd

from bbme.components.gap import gap
from bbme.composite import Draws, bernoulli


def reference_length(df: pd.DataFrame, cfg: dict) -> np.ndarray:
    """Proxy for the TIGER S1100 + S1200 length: the region's route set plus motorway and trunk.

    With `boundary_d_m` > 0 (H-T1) the proxy also counts route length lying within that distance
    outside the tract edge, as a reference drawn on the shared boundary would.
    """
    t = cfg["transport"]
    sets = df["region"].map(t["reference_set"])
    prefix = f"road_buf{t['boundary_d_m']}_" if t["boundary_d_m"] else "road_"
    out = np.zeros(len(df))
    for name in sets.unique():
        rows = (sets == name).to_numpy()
        out[rows] = df.loc[rows, f"{prefix}ref{name}mt_len"].to_numpy()
    return out


def calibrate(df: pd.DataFrame, ref: np.ndarray, cfg: dict) -> pd.DataFrame:
    """Per region: threshold tau and definedness probabilities matching the published rates.

    Tracts with reference length above tau get p_hi; the rest get the p_lo that makes the
    region's mean definedness equal 1 minus the published undefined rate (less the share
    attributed to building or POI). Eastern Washington has no published rate and borrows the
    median tau and median p_lo of the four calibrated regions.
    """
    t = cfg["transport"]
    rates = cfg["published_undefined_rate"]
    rows = []
    for region in df["region"].unique():
        r = ref[(df["region"] == region).to_numpy()]
        if region in rates:
            target = 1 - (rates[region] - cfg["undefined_other_components"])
            tau = float(np.quantile(r, 1 - target))
        else:
            target, tau = np.nan, np.nan
        rows.append({"region": region, "target_defined": target, "tau": tau, "ref": r})
    cal = pd.DataFrame(rows).set_index("region")
    cal.loc[cal["tau"].isna(), "tau"] = cal["tau"].median()
    p_lo = {}
    for region, row in cal.iterrows():
        above = float((row["ref"] > row["tau"]).mean())
        if np.isnan(row["target_defined"]):
            continue
        lo = (row["target_defined"] - t["p_defined_above_tau"] * above) / max(1 - above, 1e-9)
        p_lo[region] = float(np.clip(lo, t["p_defined_floor"], t["p_defined_above_tau"]))
    cal["p_lo"] = [p_lo.get(r, float(np.median(list(p_lo.values())))) for r in cal.index]
    cal["share_above_tau"] = [float((row["ref"] > row["tau"]).mean()) for _, row in cal.iterrows()]
    cal["fallback_length"] = [
        float(np.median(row["ref"][row["ref"] > row["tau"]])) for _, row in cal.iterrows()
    ]
    return cal.drop(columns="ref")


def transport_draws(
    df: pd.DataFrame, cfg: dict, cal: pd.DataFrame, rng: np.random.Generator, n_draws: int
) -> Draws:
    """Draws of T = gap(L_O, L_R) and its definedness.

    Above tau, L_R is the proxy with lognormal noise `sigma`. Below tau a tract is defined only
    by chance, and then its unseen reference length is drawn around the region's typical
    defined length with the wider `fallback_sigma`.
    """
    t = cfg["transport"]
    ref = reference_length(df, cfg)
    c = cal.loc[df["region"]]
    above = ref > c["tau"].to_numpy()
    p = np.where(above, t["p_defined_above_tau"], c["p_lo"].to_numpy())
    centre = np.where(above, ref, c["fallback_length"].to_numpy())
    sigma = np.where(above, t["sigma"], t["fallback_sigma"])
    noise = np.exp(sigma[:, None] * rng.standard_normal((len(df), n_draws)))
    values = gap(df["road_named_len"].to_numpy()[:, None], centre[:, None] * noise)
    return Draws(values, bernoulli(rng, p, n_draws), values.mean(axis=1), p)
