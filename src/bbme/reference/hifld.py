import urllib.request
from pathlib import Path

import duckdb
import pandas as pd

from bbme import db
from bbme.features import load_tracts

HEADERS = {"User-Agent": "bbme-reference/1.0"}


def download(cfg: dict, dest: Path) -> dict[str, Path]:
    """HIFLD Open layers (fire/EMS stations, public and private schools) from the archive."""
    ext = cfg["external_reference"]
    dest.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, key in ext["hifld_layers"].items():
        path = dest / f"hifld_{name}.parquet"
        request = urllib.request.Request(f"{ext['hifld_base']}/{key}", headers=HEADERS)
        with urllib.request.urlopen(request, timeout=900) as r:
            path.write_bytes(r.read())
        paths[name] = path
    return paths


def tract_counts(
    con: duckdb.DuckDBPyConnection,
    layers: dict[str, Path],
    raw: Path,
    regions: list[str],
    scored: pd.DataFrame,
) -> pd.DataFrame:
    """HIFLD facility points per scored tract, one count column per layer."""
    for name, path in layers.items():
        con.sql(
            f"CREATE OR REPLACE TABLE h_{name} AS "
            f"SELECT ST_SetCRS(geometry, 'OGC:CRS84') AS geometry FROM {db.scan(path)}"
        )
    frames = []
    for region in regions:
        load_tracts(con, raw, region)
        df = scored.loc[scored["region"] == region, ["GEOID"]]
        for name in layers:
            counts = con.sql(
                f"SELECT t.GEOID, count(*) AS hifld_{name} FROM h_{name} h "
                "JOIN tracts t ON ST_Intersects(t.geometry, h.geometry) GROUP BY t.GEOID"
            ).df()
            df = df.merge(counts, on="GEOID", how="left")
        frames.append(df)
    out = scored[["GEOID", "region"]].merge(pd.concat(frames), on="GEOID", how="left")
    return out.fillna({f"hifld_{name}": 0 for name in layers})
