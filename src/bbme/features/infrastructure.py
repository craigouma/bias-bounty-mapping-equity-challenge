from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.features import layer_path


def infrastructure_features(con: duckdb.DuckDBPyConnection, raw: Path, region: str) -> pd.DataFrame:
    """Per-tract transit and airport feature counts by subtype, and clipped rail length.

    Requires table `tracts`.
    """
    infra = con.sql(
        f"""
        SELECT t.GEOID, count(*) AS infra_n,
               count(*) FILTER (WHERE f.subtype = 'transit') AS infra_transit,
               count(*) FILTER (WHERE f.subtype = 'airport') AS infra_airport
        FROM {db.scan(layer_path(raw, region, "infrastructure"))} f
        JOIN tracts t ON ST_Intersects(t.geometry, f.geometry)
        GROUP BY t.GEOID
        """
    ).df()
    clipped = "ST_CollectionExtract(ST_Intersection(f.geometry, t.geometry), 2)"
    rail = con.sql(
        f"""
        SELECT t.GEOID, sum({db.length_m(clipped)}) AS rail_len_m
        FROM {db.scan(layer_path(raw, region, "rail"))} f
        JOIN tracts t ON ST_Intersects(t.geometry, f.geometry)
        GROUP BY t.GEOID
        """
    ).df()
    return infra.merge(rail, on="GEOID", how="outer")
