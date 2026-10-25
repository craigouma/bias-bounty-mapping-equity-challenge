from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.features import layer_path


def _in(values: list[str]) -> str:
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)


def place_features(
    con: duckdb.DuckDBPyConnection, raw: Path, region: str, poi_cfg: dict, cfg: dict
) -> pd.DataFrame:
    """Per-tract place counts: total, open, by mapped category group and by first source.

    Requires table `tracts`. Groups match on `categories.primary`, the field the organisers
    match HIFLD facilities against; `basic_groups` give the same counts on `basic_category`.
    NULL confidence means the provider did not report one, never low confidence.
    """
    con.sql(
        f"""
        CREATE OR REPLACE TEMP TABLE pt AS
        SELECT t.GEOID, p.categories.primary AS cat, p.basic_category AS basic,
               p.confidence, p.operating_status, p.sources[1].dataset AS dataset
        FROM {db.scan(layer_path(raw, region, "pois"))} p
        JOIN tracts t ON ST_Intersects(t.geometry, p.geometry)
        """
    )
    cols = [
        "count(*) AS poi_n",
        "count(*) FILTER (WHERE operating_status IS NULL OR operating_status = 'open') "
        "AS poi_n_open",
        "count(*) FILTER (WHERE confidence IS NULL OR confidence >= 0.5) AS poi_n_conf50",
        "count(*) FILTER (WHERE confidence IS NULL) AS poi_n_no_confidence",
    ]
    cols += [
        f"count(*) FILTER (WHERE cat IN ({_in(members)})) AS poi_{name}"
        for name, members in poi_cfg["groups"].items()
    ]
    cols += [
        f"count(*) FILTER (WHERE basic IN ({_in(members)})) AS poi_basic_{name}"
        for name, members in poi_cfg.get("basic_groups", {}).items()
    ]
    cols += [
        f"count(*) FILTER (WHERE dataset ILIKE '{pattern}') AS poi_src_{key}"
        for key, pattern in cfg["place_datasets"].items()
    ]
    return con.sql(f"SELECT GEOID, {', '.join(cols)} FROM pt GROUP BY GEOID").df()
