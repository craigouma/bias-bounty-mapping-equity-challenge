"""H-D1: unnamed drivable roads in tribal tracts, a gap the length-based scorecard cannot see.

The Bias Scorecard compares road length and feature counts. A road segment counts the same
whether or not it carries a name, but dispatch, address matching and turn-by-turn routing need
the name. This module measures the share of drivable length with no `names.primary` and compares
tribal and non-tribal tracts within the same region and RUCA class.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from bbme import db
from bbme.components.building import ruca_class
from bbme.features import strata_path


def tract_context(raw: Path, regions: list[str]) -> pd.DataFrame:
    """Tract name, county and overlapping tribal area for naming the affected places."""
    con = db.connect()
    frames = []
    for region in regions:
        frames.append(
            con.sql(
                f"""
                SELECT c.GEOID, c.NAMELSAD AS tract_name, c.STATEFP || c.COUNTYFP AS county_fips,
                       t.aiannh_name, t.aiannh_kind, t.tribal_pct
                FROM {db.scan(strata_path(raw, region, "census-tracts"))} c
                LEFT JOIN {db.scan(strata_path(raw, region, "tribal-tract-table"))} t USING (GEOID)
                """
            ).df()
        )
    return pd.concat(frames, ignore_index=True)


MEASURES = {
    "all": "unnamed_share",
    "local": "local_unnamed_share",
    "named_class": "named_unnamed_share",
}


def _share(part: pd.Series, whole: pd.Series) -> pd.Series:
    return part / whole.where(whole > 0)


def unnamed_table(features: pd.DataFrame, context: pd.DataFrame) -> pd.DataFrame:
    """Unnamed shares per tract: all drivable classes, local classes (tertiary, residential,
    unclassified) and the named classes (motorway to secondary)."""
    df = features.merge(context, on="GEOID", how="left")
    df["ruca_class"] = ruca_class(df["ruca_primary"])
    df["tribal"] = df["tribal_any"].fillna(False).astype(bool)
    legal = df["tribal_legal"].fillna(False).astype(bool)
    df["tribal_kind"] = np.where(legal, "legal", np.where(df["tribal"], "statistical", "none"))
    df["unnamed_km"] = df["road_len_unnamed"] / 1000
    df["drivable_km"] = df["road_len_total"] / 1000
    df["unnamed_share"] = _share(df["unnamed_km"], df["drivable_km"])
    named, named_unnamed = df["road_named_len"], df["road_named_unnamed_len"]
    df["named_unnamed_share"] = _share(named_unnamed, named)
    df["local_unnamed_share"] = _share(
        df["road_len_unnamed"] - named_unnamed, df["road_len_total"] - named
    )
    return df[df["drivable_km"] > 0]


def contrast(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    """Tribal tracts of one kind (`legal` reservations and trust land, or `statistical` areas
    such as OTSAs) against non-tribal tracts; `any` keeps every tribal tract."""
    if kind == "any":
        return df
    keep = df[df["tribal_kind"].isin(["none", kind])].copy()
    keep["tribal"] = keep["tribal_kind"] == kind
    return keep


def matched_difference(df: pd.DataFrame, value: str = "unnamed_share") -> float:
    """Tribal minus non-tribal mean of `value` within region x RUCA cells, tribal-weighted.

    NaN when no cell holds both tribal and non-tribal tracts.
    """
    cells = df.pivot_table(
        index=["region", "ruca_class"], columns="tribal", values=value, aggfunc="mean"
    )
    if True not in cells or False not in cells:
        return float("nan")
    weights = df[df["tribal"]].groupby(["region", "ruca_class"]).size()
    cells = cells.dropna().join(weights.rename("w"), how="inner")
    if cells.empty:
        return float("nan")
    return float(((cells[True] - cells[False]) * cells["w"]).sum() / cells["w"].sum())


def bootstrap_by_county(
    df: pd.DataFrame, rng: np.random.Generator, n_boot: int = 1000, value: str = "unnamed_share"
) -> tuple[float, float]:
    """95% interval for the matched difference, resampling whole counties.

    Resamples with no tribal and non-tribal tracts in a shared cell are left out.
    """
    groups = {c: g for c, g in df.groupby("county_fips")}
    counties = np.array(list(groups))
    stats = []
    for _ in range(n_boot):
        pick = rng.choice(counties, size=len(counties), replace=True)
        sample = pd.concat([groups[c] for c in pick], ignore_index=True)
        stats.append(matched_difference(sample, value))
    return tuple(np.nanquantile(stats, [0.025, 0.975]))


def stratum_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["region", "ruca_class", "tribal"])
        .agg(
            tracts=("GEOID", "size"),
            mean_unnamed_share=("unnamed_share", "mean"),
            unnamed_km=("unnamed_km", "sum"),
            drivable_km=("drivable_km", "sum"),
        )
        .reset_index()
    )


def worst_tracts(df: pd.DataFrame, n: int = 25) -> pd.DataFrame:
    cols = ["GEOID", "region", "tract_name", "county_fips", "county_name", "aiannh_name"]
    cols += ["tribal_kind", "ruca_class", "drivable_km", "unnamed_km", "unnamed_share"]
    cols += ["local_unnamed_share", "pop_total"]
    tribal = df[df["tribal"] & (df["drivable_km"] >= 20)]
    return tribal.sort_values("unnamed_km", ascending=False)[cols].head(n)


def by_tribal_area(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[df["tribal"]]
        .groupby(["region", "aiannh_name", "tribal_kind"])
        .agg(
            tracts=("GEOID", "size"),
            unnamed_km=("unnamed_km", "sum"),
            drivable_km=("drivable_km", "sum"),
            population=("pop_total", "sum"),
        )
        .assign(unnamed_share=lambda t: t["unnamed_km"] / t["drivable_km"])
        .sort_values("unnamed_km", ascending=False)
        .reset_index()
    )
