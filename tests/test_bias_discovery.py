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
                    "tribal_legal": tribal and county == "40001",
                    "road_len_unnamed": share * 10_000,
                    "road_len_total": 10_000.0,
                    "road_named_len": 2_000.0,
                    "road_named_unnamed_len": 0.0,
                    "pop_total": 100,
                }
            )
    return pd.DataFrame(rows)


def test_matched_difference_and_bootstrap():
    df = bd.unnamed_table(_frame(), pd.DataFrame({"GEOID": []}))
    assert bd.matched_difference(df) == pytest.approx(0.2)
    lo, hi = bd.bootstrap_by_county(df, np.random.default_rng(0), n_boot=200)
    assert lo <= 0.2 <= hi


def test_local_share_excludes_named_classes():
    df = bd.unnamed_table(_frame(), pd.DataFrame({"GEOID": []}))
    tribal = df[df["county_fips"].eq("40001") & df["tribal"]]
    assert tribal["local_unnamed_share"].iloc[0] == pytest.approx(3_000 / 8_000)
    assert tribal["named_unnamed_share"].iloc[0] == 0.0


def test_contrast_compares_one_tribal_kind_with_non_tribal_tracts():
    df = bd.unnamed_table(_frame(), pd.DataFrame({"GEOID": []}))
    legal = bd.contrast(df, "legal")
    assert set(legal.loc[legal["tribal"], "county_fips"]) == {"40001"}
    assert len(legal) == 15
    assert bd.matched_difference(legal) == pytest.approx(0.3 - 0.075)
    assert bd.matched_difference(bd.contrast(df, "statistical")) == pytest.approx(0.25 - 0.075)


def test_bootstrap_skips_resamples_without_tribal_tracts():
    frame = _frame()
    frame.loc[frame["county_fips"] == "40003", "tribal_any"] = False
    df = bd.unnamed_table(frame, pd.DataFrame({"GEOID": []}))
    assert np.isnan(bd.matched_difference(df[~df["tribal"]]))
    lo, hi = bd.bootstrap_by_county(df, np.random.default_rng(0), n_boot=200)
    assert np.isfinite(lo) and np.isfinite(hi)
