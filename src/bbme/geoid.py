from pathlib import Path

import pandas as pd


def assert_geoids(geoids: pd.Series) -> pd.Series:
    """Fail unless every GEOID is an 11-character string of digits.

    GEOID is text everywhere: an integer read drops the leading zero of Arizona (04) and
    the New Mexico tract (35) and every later join silently loses those rows.
    """
    if not all(isinstance(g, str) for g in geoids):
        raise TypeError("GEOID values must be strings")
    bad = geoids[~geoids.str.fullmatch(r"\d{11}")]
    if len(bad):
        raise ValueError(f"{len(bad)} malformed GEOIDs, first: {bad.iloc[0]!r}")
    return geoids


def read_csv(path: Path | str, **kwargs) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"GEOID": str}, keep_default_na=False, **kwargs)
    assert_geoids(df["GEOID"])
    return df
