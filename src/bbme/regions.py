from pathlib import Path

import pandas as pd

from bbme import guard
from bbme.geoid import read_csv


def scored_tracts(raw: Path, regions: list[str]) -> pd.DataFrame:
    """Scored GEOIDs with their region, from the per-region sample submissions in the bucket.

    Region always comes from these lists (equivalently the `region` column of the Zindi sample),
    never from state FIPS: the New Mexico tract 35023970000 belongs to maricopa-az.
    """
    frames = []
    for region in regions:
        path = raw / "reference" / region / f"{region}-sample-submission.csv"
        df = read_csv(guard.raw(path), usecols=["GEOID"])
        frames.append(df.assign(region=region))
    out = pd.concat(frames, ignore_index=True).sort_values("GEOID", ignore_index=True)
    if out["GEOID"].duplicated().any():
        raise ValueError("a GEOID appears in more than one region list")
    return out


def assert_matches_sample(scored: pd.DataFrame, sample: pd.DataFrame) -> None:
    got = scored[["GEOID", "region"]].sort_values("GEOID", ignore_index=True)
    want = sample[["GEOID", "region"]].sort_values("GEOID", ignore_index=True)
    if not got.equals(want):
        diff = got.merge(want, on="GEOID", how="outer", indicator=True)
        diff = diff[(diff["_merge"] != "both") | (diff["region_x"] != diff["region_y"])]
        raise ValueError(f"region lists differ from the sample in {len(diff)} rows:\n{diff.head()}")
