import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from bbme import guard
from bbme.geoid import assert_geoids

HEADERS = {"User-Agent": "bbme-reference/1.0"}


def download(url: str, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    path = guard.raw(dest / url.rsplit("/", 1)[1])
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=600) as r:
        path.write_bytes(r.read())
    return path


def zip_establishments(path: Path) -> pd.Series:
    """Establishments per 5-digit ZIP from the ZIP Code Business Patterns totals file."""
    df = pd.read_csv(guard.raw(path), compression="zip", dtype={"zip": str}, usecols=["zip", "est"])
    return df.set_index(df["zip"].str.zfill(5))["est"]


def tract_establishments(zbp: pd.Series, relation: Path, tracts: pd.DataFrame) -> pd.DataFrame:
    """ZIP establishments apportioned to tracts through the 2020 ZCTA-tract relationship.

    `est_area`: by the share of the ZCTA's land in the tract. `est_pop`: by tract population
    times the tract's land fraction inside the ZCTA, normalised within each ZCTA.
    """
    rel = pd.read_csv(
        guard.raw(relation),
        sep="|",
        dtype={"GEOID_ZCTA5_20": str, "GEOID_TRACT_20": str},
        usecols=[
            "GEOID_ZCTA5_20",
            "GEOID_TRACT_20",
            "AREALAND_PART",
            "AREALAND_ZCTA5_20",
            "AREALAND_TRACT_20",
        ],
    ).dropna(subset=["GEOID_ZCTA5_20"])
    rel = rel.rename(columns={"GEOID_ZCTA5_20": "zcta", "GEOID_TRACT_20": "GEOID"})
    rel["est"] = rel["zcta"].map(zbp).fillna(0)
    rel = rel.merge(tracts[["GEOID", "pop_total"]], on="GEOID", how="left").fillna({"pop_total": 0})
    land = rel["AREALAND_PART"].clip(lower=0)
    rel["w_area"] = land / rel["AREALAND_ZCTA5_20"].replace(0, np.nan)
    rel["w_pop"] = rel["pop_total"] * land / rel["AREALAND_TRACT_20"].replace(0, np.nan)
    rel["w_pop"] = rel["w_pop"] / rel.groupby("zcta")["w_pop"].transform("sum").replace(0, np.nan)
    rel["est_area"] = (rel["est"] * rel["w_area"]).fillna(0)
    rel["est_pop"] = (rel["est"] * rel["w_pop"]).fillna(0)
    out = rel.groupby("GEOID", as_index=False)[["est_area", "est_pop"]].sum()
    out = (
        tracts[["GEOID", "region"]]
        .merge(out, on="GEOID", how="left")
        .fillna({"est_area": 0, "est_pop": 0})
    )
    assert_geoids(out["GEOID"])
    return out
