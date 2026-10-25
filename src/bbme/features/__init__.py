from pathlib import Path

import duckdb

from bbme import db


def layer_path(raw: Path, region: str, layer: str) -> Path:
    return raw / "reference" / region / f"{region}-overture-{layer}.parquet"


def strata_path(raw: Path, region: str, table: str) -> Path:
    return raw / "strata" / region / f"{region}-{table}.parquet"


def load_tracts(con: duckdb.DuckDBPyConnection, raw: Path, region: str) -> None:
    """Create table `tracts` (GEOID, geometry) for one region."""
    con.sql(
        "CREATE OR REPLACE TABLE tracts AS SELECT GEOID, geometry "
        f"FROM {db.scan(strata_path(raw, region, 'census-tracts'))}"
    )
