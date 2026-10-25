from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.features import strata_path


def strata_features(
    con: duckdb.DuckDBPyConnection, raw: Path, region: str, cfg: dict
) -> pd.DataFrame:
    """Context per tract: strata columns, recent burned shares, ACS housing units and water area.

    Strata nulls stay null: a source that does not reach a tract is not a zero.
    """
    cols = ", ".join(f's."{c}"' for c in cfg["strata_columns"])
    acs = raw / "reference" / region / f"{region}-census-acs-housing.parquet"
    national = raw / "strata" / "national" / "national-census-tract-table.parquet"
    return con.sql(
        f"""
        SELECT s.GEOID, {cols},
               m.mtbs_wildfire_burned_pct_land_2015_2023 AS mtbs_burned_pct_2015,
               n.nifc_wildfire_burned_pct_land_2015_2025 AS nifc_burned_pct_2015,
               a.housing_units AS acs_housing_units,
               c.AWATER AS awater,
               c.AWATER / nullif(c.ALAND + c.AWATER, 0) AS water_share
        FROM {db.scan(strata_path(raw, region, "strata-tract-table"))} s
        LEFT JOIN {db.scan(strata_path(raw, region, "mtbs-tract-table"))} m USING (GEOID)
        LEFT JOIN {db.scan(strata_path(raw, region, "nifc-tract-table"))} n USING (GEOID)
        LEFT JOIN {db.scan(acs)} a USING (GEOID)
        LEFT JOIN {db.scan(national)} c USING (GEOID)
        """
    ).df()
