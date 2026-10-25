import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from bbme.features import load_tracts
from bbme.features.buildings import building_features
from bbme.features.infrastructure import infrastructure_features
from bbme.features.places import place_features
from bbme.features.roads import road_features
from bbme.features.strata import strata_features
from bbme.geoid import assert_geoids
from bbme.regions import scored_tracts

ZERO_FILLED = ("road_", "bld_n", "bld_osm_large_", "bld_suppressed_", "poi_", "infra_", "rail_")
DESCRIPTIONS = {
    "road_len_": "clipped drivable road length of one Overture class, metres",
    "road_named_": "clipped length of classes motorway, trunk, primary, secondary, metres",
    "road_route_": "clipped length of segments on a route network group, metres",
    "road_ref": "clipped length of a reference proxy set (mt: plus motorway and trunk), metres",
    "road_buf": "length inside the tract grown outward by the stated metres",
    "road_": "road summary",
    "bld_": "Overture building footprints by centroid (intersects where stated)",
    "poi_": "Overture places by point in polygon",
    "infra_": "Overture infrastructure features",
    "rail_": "clipped Overture rail length, metres",
    "acs_": "ACS 2020-2024 housing units (B25001)",
    "mtbs_": "MTBS burned share of land",
    "nifc_": "NIFC burned share of land",
}


def region_features(
    con: duckdb.DuckDBPyConnection, raw: Path, region: str, scored: pd.DataFrame, cfg: dict
) -> pd.DataFrame:
    load_tracts(con, raw, region)
    df = scored[scored["region"] == region][["GEOID", "region"]]
    parts = {
        "roads": lambda: road_features(con, raw, region, cfg["features"]),
        "buildings": lambda: building_features(con, raw, region, cfg["features"]),
        "places": lambda: place_features(con, raw, region, cfg["poi"], cfg["features"]),
        "infrastructure": lambda: infrastructure_features(con, raw, region),
        "strata": lambda: strata_features(con, raw, region, cfg["features"]),
    }
    for name, build in parts.items():
        started = time.time()
        df = df.merge(build(), on="GEOID", how="left", validate="1:1")
        print(f"{region} {name}: {time.time() - started:.0f}s", flush=True)
    return df


def build(con: duckdb.DuckDBPyConnection, raw: Path, cfg: dict) -> pd.DataFrame:
    """One row per scored GEOID.

    Explicit zeros mean "no features found"; NULL means "not applicable".
    """
    scored = scored_tracts(raw, cfg["data"]["regions"])
    df = pd.concat(
        [region_features(con, raw, r, scored, cfg) for r in cfg["data"]["regions"]],
        ignore_index=True,
    )
    df = df.sort_values("GEOID", ignore_index=True)
    assert_geoids(df["GEOID"])
    if not df["GEOID"].equals(scored["GEOID"]):
        raise ValueError("feature rows do not match the scored tract list")
    zero = [c for c in df.columns if c.startswith(ZERO_FILLED)]
    df[zero] = df[zero].fillna(0)
    return df


def calibration(df: pd.DataFrame, cfg: dict) -> dict:
    """Road ratios and implied transport-undefined rates per region for each reference proxy.

    Compared without the leaderboard against the published facts: undefined rates of 21%
    (eastern-ok), 37% (northern-ca), 28% (south-central-tx), 55% (maricopa-az) and region
    ratios of named Overture length to reference length between 0.71 and 1.59.
    """
    taus = [0, 50, 100, 250, 500, 1000, 2000]
    out: dict = {}
    for region, g in df.groupby("region"):
        rows = {}
        for name in cfg["reference_sets"]:
            for variant, col in [
                ("", f"road_ref{name}mt_len"),
                ("_buf25", f"road_buf25_ref{name}mt_len"),
            ]:
                ref = g[col]
                rows[f"{name}{variant}"] = {
                    "named_over_ref": float(g["road_named_len"].sum() / ref.sum()),
                    "share_ref_le_tau": {str(t): float((ref <= t).mean()) for t in taus},
                }
        out[region] = {"tracts": len(g), "sets": rows}
    return out


def column_doc(df: pd.DataFrame) -> str:
    lines = [
        "# Feature columns",
        "",
        "| Column | Dtype | Null rate | Meaning |",
        "|---|---|---|---|",
    ]
    for col in df.columns:
        meaning = next((v for k, v in DESCRIPTIONS.items() if col.startswith(k)), "context")
        null = float(df[col].isna().mean())
        lines.append(f"| {col} | {df[col].dtype} | {null:.3f} | {meaning} |")
    return "\n".join(lines) + "\n"


def summary(df: pd.DataFrame) -> dict:
    numeric = df.select_dtypes(include=[np.number])
    return {
        "rows": len(df),
        "columns": df.shape[1],
        "rows_per_region": df["region"].value_counts().to_dict(),
        "non_finite_numeric_cells": int((~np.isfinite(numeric.fillna(0))).sum().sum()),
    }
