import csv
import math
import shutil
import urllib.request
from pathlib import Path

import duckdb
import pandas as pd

from bbme import guard
from bbme.features import load_tracts

HEADERS = {"User-Agent": "bbme-reference/1.0"}


def quadkeys(xmin: float, ymin: float, xmax: float, ymax: float, zoom: int) -> set[str]:
    """Web Mercator quadkeys at `zoom` whose tiles cover the lon/lat box."""

    def tile(lon: float, lat: float) -> tuple[int, int]:
        n = 2**zoom
        x = int((lon + 180) / 360 * n)
        y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
        return min(max(x, 0), n - 1), min(max(y, 0), n - 1)

    x0, y1 = tile(xmin, ymin)
    x1, y0 = tile(xmax, ymax)
    keys = set()
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            keys.add(
                "".join(
                    str(((x >> b) & 1) | (((y >> b) & 1) << 1)) for b in range(zoom - 1, -1, -1)
                )
            )
    return keys


def download(index_url: str, location: str, keys: set[str], dest: Path) -> list[Path]:
    """Global ML Building Footprints files for `location` whose quadkey is in `keys`."""
    dest.mkdir(parents=True, exist_ok=True)
    index = dest / "dataset-links.csv"
    with urllib.request.urlopen(urllib.request.Request(index_url, headers=HEADERS)) as r:
        index.write_bytes(r.read())
    paths = []
    with guard.raw(index).open() as f:
        for row in csv.DictReader(f):
            if row["Location"] != location or row["QuadKey"] not in keys:
                continue
            path = dest / f"{row['QuadKey']}-{row['Url'].rsplit('/', 1)[1]}"
            request = urllib.request.Request(row["Url"], headers=HEADERS)
            with urllib.request.urlopen(request, timeout=1800) as r, path.open("wb") as out:
                shutil.copyfileobj(r, out, 8 * 1024 * 1024)
            paths.append(path)
    return paths


def tract_counts(
    con: duckdb.DuckDBPyConnection,
    files: list[Path],
    raw: Path,
    regions: list[str],
    scored: pd.DataFrame,
) -> pd.DataFrame:
    """Global ML footprints per scored tract, assigned by true polygon centroid in lon/lat."""
    sources = ", ".join(f"'{guard.raw(p)}'" for p in files)
    con.sql(
        f"""
        CREATE OR REPLACE TABLE gml AS
        SELECT ST_Centroid(ST_GeomFromGeoJSON(geometry::VARCHAR)) AS centroid
        FROM read_json([{sources}], format = 'newline_delimited',
                       columns = {{'geometry': 'JSON'}}, compression = 'gzip')
        """
    )
    frames = []
    for region in regions:
        load_tracts(con, raw, region)
        frames.append(
            con.sql(
                "SELECT t.GEOID, count(*) AS ms_n_globalml FROM gml g "
                "JOIN tracts t ON ST_Intersects(t.geometry, g.centroid) GROUP BY t.GEOID"
            ).df()
        )
    counts = pd.concat(frames, ignore_index=True).groupby("GEOID", as_index=False).sum()
    out = scored[["GEOID", "region"]].merge(counts, on="GEOID", how="left")
    return out.fillna({"ms_n_globalml": 0})
