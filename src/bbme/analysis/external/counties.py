import urllib.request
from pathlib import Path

import pandas as pd

from bbme import guard

HEADERS = {"User-Agent": "bbme-analysis/1.0"}


def county_names(url: str, dest: Path) -> pd.DataFrame:
    """County names keyed by 5-digit FIPS, from the Census 2020 county code list."""
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / url.rsplit("/", 1)[1]
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as r:
        path.write_bytes(r.read())
    df = pd.read_csv(guard.raw(path), sep="|", dtype=str)
    return pd.DataFrame(
        {
            "county_fips": df["STATEFP"] + df["COUNTYFP"],
            "county_name": df["COUNTYNAME"] + ", " + df["STATE"],
        }
    )
