from pathlib import Path

import duckdb

from bbme import guard


def connect(
    memory_limit: str | None = None, threads: int | None = None, temp_dir: str | None = None
) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.sql("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;")
    con.sql("SET s3_region='us-west-2'; SET s3_url_style='path';")
    if memory_limit:
        con.sql(f"SET memory_limit='{memory_limit}'")
    if threads:
        con.sql(f"SET threads={threads}")
    if temp_dir:
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        con.sql(f"SET temp_directory='{temp_dir}'")
    return con


def scan(path: Path | str) -> str:
    return f"read_parquet('{guard.raw(path)}')"


def scan_artifact(path: Path | str) -> str:
    return f"read_parquet('{guard.artifact(path)}')"


# Every layer is lon/lat (OGC:CRS84). DuckDB follows the EPSG:4326 authority order (lat/lon):
# ST_Length_Spheroid on unflipped input returns NaN and ST_Transform without always_xy returns
# inf, both silently. These two fragments are the only sanctioned ways to measure.
def length_m(geom: str) -> str:
    return f"ST_Length_Spheroid(ST_FlipCoordinates({geom}))"


def area_m2(geom: str) -> str:
    return f"ST_Area(ST_Transform({geom}, 'EPSG:4326', 'EPSG:5070', always_xy := true))"


def to_albers(geom: str) -> str:
    return f"ST_Transform({geom}, 'EPSG:4326', 'EPSG:5070', always_xy := true)"


def assert_finite(con: duckdb.DuckDBPyConnection, relation: str, columns: list[str]) -> None:
    checks = ", ".join(f"count(*) FILTER (WHERE NOT isfinite({c}))" for c in columns)
    bad = con.sql(f"SELECT {checks} FROM {relation}").fetchone()
    offenders = {c: n for c, n in zip(columns, bad, strict=True) if n}
    if offenders:
        raise ValueError(f"non-finite values in {relation}: {offenders}")
