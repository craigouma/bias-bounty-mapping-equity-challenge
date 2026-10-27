import shutil
import urllib.request
from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.features import load_tracts

HEADERS = {"User-Agent": "bbme-reference/1.0"}


def download(cfg: dict, dest: Path) -> list[Path]:
    """USGS National Structures Dataset per state (GeoPackage), from the National Map."""
    ext = cfg["external_reference"]
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for state in ext["facility_states"]:
        url = ext["facility_url"].format(state=state)
        path = dest / url.rsplit("/", 1)[1]
        request = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(request, timeout=3600) as r, path.open("wb") as f:
            shutil.copyfileobj(r, f, 8 * 1024 * 1024)
        paths.append(path)
        print(f"facilities: downloaded {path.name}", flush=True)
    return paths


def load_points(con: duckdb.DuckDBPyConnection, zips: list[Path], fcodes: dict) -> None:
    """Create table `facility`: structure points of the configured types, labelled by type."""
    case = " ".join(
        f"WHEN fcode IN ({', '.join(str(c) for c in codes)}) THEN '{name}'"
        for name, codes in fcodes.items()
    )
    every = ", ".join(str(c) for codes in fcodes.values() for c in codes)
    parts = [
        f"SELECT CASE {case} END AS kind, fcode, ST_SetCRS(Shape, 'OGC:CRS84') AS geometry "
        f"FROM {db.scan_zipped_vector(z, z.name.replace('.zip', '.gpkg'), 'Struct_Point')} "
        f"WHERE fcode IN ({every})"
        for z in zips
    ]
    con.sql(f"CREATE OR REPLACE TABLE facility AS {' UNION ALL '.join(parts)}")


def tract_counts(
    con: duckdb.DuckDBPyConnection,
    raw: Path,
    regions: list[str],
    scored: pd.DataFrame,
    kinds: list[str],
) -> pd.DataFrame:
    cols = ", ".join(f"count(*) FILTER (WHERE f.kind = '{k}') AS ref_{k}" for k in kinds)
    frames = []
    for region in regions:
        load_tracts(con, raw, region)
        frames.append(
            con.sql(
                f"SELECT t.GEOID, {cols} FROM facility f "
                "JOIN tracts t ON ST_Intersects(t.geometry, f.geometry) GROUP BY t.GEOID"
            ).df()
        )
    counts = pd.concat(frames, ignore_index=True).groupby("GEOID", as_index=False).sum()
    out = scored[["GEOID", "region"]].merge(counts, on="GEOID", how="left")
    return out.fillna({f"ref_{k}": 0 for k in kinds})
