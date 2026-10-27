import urllib.request
from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.features import load_tracts

HEADERS = {"User-Agent": "bbme-reference/1.0"}
CLIP = "ST_CollectionExtract(ST_Intersection(g.geometry, t.geometry), 2)"


def download(cfg: dict, dest: Path) -> list[Path]:
    """TIGER/Line primary and secondary roads per state, from the Census public source."""
    ext = cfg["external_reference"]
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for state in ext["states"]:
        url = ext["tiger_prisecroads_url"].format(state=state)
        path = dest / url.rsplit("/", 1)[1]
        request = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(request, timeout=300) as r:
            path.write_bytes(r.read())
        paths.append(path)
    return paths


def load_roads(con: duckdb.DuckDBPyConnection, zips: list[Path]) -> None:
    """Create table `tiger`: S1100 and S1200 segments from every state file."""
    parts = [
        f"SELECT LINEARID, MTFCC, geom AS geometry "
        f"FROM {db.scan_zipped_vector(z, z.name.replace('.zip', '.shp'))} "
        f"WHERE MTFCC IN ('S1100', 'S1200')"
        for z in zips
    ]
    con.sql(f"CREATE OR REPLACE TABLE tiger AS {' UNION ALL '.join(parts)}")


def tract_lengths(
    con: duckdb.DuckDBPyConnection, raw: Path, regions: list[str], scored: pd.DataFrame
) -> pd.DataFrame:
    """TIGER S1100 + S1200 length clipped to each scored tract, in geodesic metres.

    A segment lying on a tract boundary intersects both neighbours and counts in full in each,
    as a clipped reference computation would count it.
    """
    frames = []
    for region in regions:
        load_tracts(con, raw, region)
        frames.append(
            con.sql(
                f"""
                SELECT t.GEOID,
                       sum({db.length_m(CLIP)}) AS tiger_len_m,
                       sum({db.length_m(CLIP)}) FILTER (WHERE g.MTFCC = 'S1100') AS tiger_s1100_m
                FROM tiger g JOIN tracts t ON ST_Intersects(t.geometry, g.geometry)
                GROUP BY t.GEOID
                """
            ).df()
        )
    lengths = pd.concat(frames, ignore_index=True).groupby("GEOID", as_index=False).sum()
    out = scored[["GEOID", "region"]].merge(lengths, on="GEOID", how="left")
    return out.fillna({"tiger_len_m": 0.0, "tiger_s1100_m": 0.0})
