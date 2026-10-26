import numpy as np
import pandas as pd

from bbme.components.gap import gap
from bbme.composite import Draws, bernoulli

TIERS = ("high", "mid", "low")


def reference_lengths(df: pd.DataFrame, cfg: dict) -> tuple[np.ndarray, np.ndarray]:
    """Proxies for the TIGER S1100 + S1200 length: the primary and the secondary route set.

    Both include motorway and trunk. With `boundary_d_m` > 0 (H-T1) they also count route
    length lying within that distance outside the tract edge, as a reference drawn on the
    shared boundary would. `exclude_links` (H-T4) removes ramps, which TIGER classes apart;
    `unclipped` (H-T5) counts whole segments touching the tract.
    """
    t = cfg["transport"]
    out = []
    for name in (t["reference_set"], t["secondary_set"]):
        clipped = df[f"road_ref{name}mt_len"].to_numpy(float)
        length = (
            df[f"road_buf{t['boundary_d_m']}_ref{name}mt_len"].to_numpy(float)
            if t["boundary_d_m"]
            else clipped.copy()
        )
        if t["exclude_links"]:
            length = length - (clipped - df[f"road_ref{name}mt_nolink_len"].to_numpy(float))
        if t["unclipped"]:
            length = length + df[f"road_ref{name}mt_unclipped_len"].to_numpy(float) - clipped
        out.append(np.maximum(length, 0.0))
    return out[0], np.maximum(out[1], out[0])


def overture_length(df: pd.DataFrame, cfg: dict) -> np.ndarray:
    column = "road_named_unclipped_len" if cfg["transport"]["unclipped"] else "road_named_len"
    return df[column].to_numpy(float)


def tiers(primary: np.ndarray, secondary: np.ndarray) -> np.ndarray:
    return np.where(primary > 0, "high", np.where(secondary > 0, "mid", "low"))


def calibrate(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Per region definedness by tier, matching the published undefined rates.

    High-tier tracts get p_high. With p_low at the floor, p_mid is solved so the region's mean
    definedness equals 1 minus the published undefined rate (less the share attributed to
    building or POI); if that needs p_mid outside [floor, p_high] it is clipped and p_low
    absorbs the rest. q = p_mid / p_high is the chance a high-tier tract's reference also holds
    its secondary routes. Eastern Washington has no published rate and borrows the medians.
    """
    t = cfg["transport"]
    rates = cfg["published_undefined_rate"]
    primary, secondary = reference_lengths(df, cfg)
    tier = pd.Series(tiers(primary, secondary), index=df.index)
    rows = []
    for region, g in tier.groupby(df["region"]):
        share = {k: float((g == k).mean()) for k in TIERS}
        row = {"region": region, **{f"share_{k}": v for k, v in share.items()}}
        if region in rates:
            target = 1 - (rates[region] - cfg["undefined_other_components"])
            rest = target - t["p_defined_high"] * share["high"]
            p_low = t["p_defined_floor"]
            p_mid = (rest - p_low * share["low"]) / max(share["mid"], 1e-9)
            p_mid = float(np.clip(p_mid, p_low, t["p_defined_high"]))
            p_low = (rest - p_mid * share["mid"]) / max(share["low"], 1e-9)
            row.update(target_defined=target, p_mid=p_mid, p_low=float(np.clip(p_low, 0, 1)))
        rows.append(row)
    cal = pd.DataFrame(rows).set_index("region")
    for col in ["p_mid", "p_low"]:
        cal[col] = cal[col].fillna(cal[col].median())
    cal["p_high"] = t["p_defined_high"]
    cal["q_secondary"] = cal["p_mid"] / cal["p_high"]
    lengths = pd.Series(primary, index=df.index).where(primary > 0)
    cal["fallback_length"] = lengths.groupby(df["region"]).median()
    cal["mean_p_defined"] = [
        sum(cal.loc[r, f"share_{k}"] * cal.loc[r, f"p_{k}"] for k in TIERS) for r in cal.index
    ]
    return cal


def transport_draws(
    df: pd.DataFrame, cfg: dict, cal: pd.DataFrame, rng: np.random.Generator, n_draws: int
) -> Draws:
    """Draws of T = gap(L_O, L_R) and its definedness.

    High tier: L_R is the primary proxy, replaced with probability q by the secondary proxy.
    Mid tier: L_R is the secondary proxy. Both carry lognormal noise `sigma`. Low tier: defined
    only by chance, and then the unseen reference length is drawn around the region's typical
    length with the wider `fallback_sigma`.
    """
    t = cfg["transport"]
    n = len(df)
    primary, secondary = reference_lengths(df, cfg)
    tier = tiers(primary, secondary)
    c = cal.loc[df["region"]]
    high, mid = tier == "high", tier == "mid"
    p = np.select([high, mid], [c["p_high"], c["p_mid"]], c["p_low"])
    centre = np.select([high, mid], [primary, secondary], c["fallback_length"].to_numpy())
    with_secondary = high[:, None] & bernoulli(rng, c["q_secondary"].to_numpy(), n_draws)
    centre = np.where(with_secondary, secondary[:, None], centre[:, None])
    sigma = np.where(tier == "low", t["fallback_sigma"], t["sigma"])
    noise = np.exp(sigma[:, None] * rng.standard_normal((n, n_draws)))
    values = gap(overture_length(df, cfg)[:, None], centre * noise)
    values = np.clip(values * t["value_scale"], 0.0, 1.0)
    return Draws(values, bernoulli(rng, p, n_draws), values.mean(axis=1), p)
