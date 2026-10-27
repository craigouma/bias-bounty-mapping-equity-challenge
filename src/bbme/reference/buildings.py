import shutil
import urllib.request
from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.features import load_tracts

HEADERS = {"User-Agent": "bbme-reference/1.0"}


def download(cfg: dict, dest: Path) -> list[Path]:
    """Microsoft US Building Footprints per state, from the public legacy release."""
    ext = cfg["external_reference"]
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for state in ext["building_states"]:
        url = ext["building_url"].format(state=state)
        path = dest / url.rsplit("/", 1)[1]
        request = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(request, timeout=1800) as r, path.open("wb") as f:
            shutil.copyfileobj(r, f, 8 * 1024 * 1024)
        paths.append(path)
    return paths


def tract_counts(
    con: duckdb.DuckDBPyConnection,
    zips: list[Path],
    raw: Path,
    regions: list[str],
    scored: pd.DataFrame,
) -> pd.DataFrame:
    """Reference footprints per scored tract, by centroid and by intersects.

    Each state file is read once and joined to every region's tracts; a tract only meets the
    footprints of its own state, so per-state partial counts add up.
    """
    frames = []
    for z in zips:
        member = z.name.removesuffix(".zip")
        con.sql(
            f"""
            CREATE OR REPLACE TEMP TABLE ms AS
            SELECT ST_SetCRS(geom, 'OGC:CRS84') AS geometry,
                   ST_Centroid(ST_SetCRS(geom, 'OGC:CRS84')) AS centroid
            FROM {db.scan_zipped_vector(z, member)}
            """
        )
        for region in regions:
            load_tracts(con, raw, region)
            centroid = con.sql(
                "SELECT t.GEOID, count(*) AS ms_n_centroid FROM ms m "
                "JOIN tracts t ON ST_Intersects(t.geometry, m.centroid) GROUP BY t.GEOID"
            ).df()
            touching = con.sql(
                "SELECT t.GEOID, count(*) AS ms_n_intersects FROM ms m "
                "JOIN tracts t ON ST_Intersects(t.geometry, m.geometry) GROUP BY t.GEOID"
            ).df()
            frames.append(centroid.merge(touching, on="GEOID", how="outer"))
        print(f"buildings: {member} done", flush=True)
    counts = pd.concat(frames, ignore_index=True).groupby("GEOID", as_index=False).sum()
    out = scored[["GEOID", "region"]].merge(counts, on="GEOID", how="left")
    return out.fillna({"ms_n_centroid": 0, "ms_n_intersects": 0})
