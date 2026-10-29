import numpy as np
import pandas as pd
import pytest

from bbme.analysis import bias_discovery as bd


def _frame() -> pd.DataFrame:
    rows = []
    for county, tribal, share in [
        ("40001", True, 0.3),
        ("40001", False, 0.1),
        ("40003", True, 0.25),
        ("40003", False, 0.05),
    ]:
        for i in range(5):
            rows.append(
                {
                    "GEOID": f"{county}{tribal:d}{i:05d}",
                    "region": "eastern-ok",
                    "county_fips": county,
                    "ruca_primary": 10.0,
                    "tribal_any": tribal,
                    "road_len_unnamed": share * 10_000,
                    "road_len_total": 10_000.0,
                    "pop_total": 100,
                }
            )
    return pd.DataFrame(rows)


def test_matched_difference_and_bootstrap():
    df = bd.unnamed_table(_frame(), pd.DataFrame({"GEOID": []}))
    assert bd.matched_difference(df) == pytest.approx(0.2)
    lo, hi = bd.bootstrap_by_county(df, np.random.default_rng(0), n_boot=200)
    assert lo <= 0.2 <= hi


def test_bootstrap_skips_resamples_without_tribal_tracts():
    frame = _frame()
    frame.loc[frame["county_fips"] == "40003", "tribal_any"] = False
    df = bd.unnamed_table(frame, pd.DataFrame({"GEOID": []}))
    assert np.isnan(bd.matched_difference(df[~df["tribal"]]))
    lo, hi = bd.bootstrap_by_county(df, np.random.default_rng(0), n_boot=200)
    assert np.isfinite(lo) and np.isfinite(hi)
