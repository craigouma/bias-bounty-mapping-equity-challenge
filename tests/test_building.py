import numpy as np
import pandas as pd
import pytest

from bbme.components.building import building_draws, ruca_class
from bbme.config import load


def _frame() -> pd.DataFrame:
    n = 60
    return pd.DataFrame(
        {
            "region": ["northern-ca"] * n,
            "ruca_primary": [1.0] * n,
            "acs_housing_units": [100.0] * n,
            "bld_n": [150.0] * n,
            "bld_ml_share": [1.0] * n,
        }
    )


def test_ruca_classes():
    s = ruca_class(pd.Series([1.0, 5.0, 8.0, 10.0, np.nan]))
    assert s.tolist() == ["metro", "micro", "small_town", "rural", "unknown"]


def test_deficit_baseline_and_empty_tracts():
    df, cfg = _frame(), load("model")
    cfg["building"]["use_hu_deficit"] = True
    df.loc[0, ["bld_n", "bld_ml_share"]] = [30.0, 0.2]
    df.loc[1, ["bld_n", "bld_ml_share", "acs_housing_units"]] = [0.0, np.nan, 0.0]
    d = building_draws(df, cfg, np.random.default_rng(0), 100)
    assert d.point[0] == pytest.approx(0.8)
    assert d.point[1] == 1.0
    assert d.p_defined[1] == cfg["building"]["p_defined_without"]
    assert d.point[2] == cfg["building"]["baseline_gap"]


def test_deficit_off_by_default():
    df, cfg = _frame(), load("model")
    df.loc[0, ["bld_n", "bld_ml_share"]] = [30.0, 0.2]
    d = building_draws(df, cfg, np.random.default_rng(0), 10)
    assert d.point[0] == cfg["building"]["baseline_gap"]


def test_usfs_reference_learns_ratio_and_flags_shortfall():
    df, cfg = _frame(), load("model")
    df["usfs_BuildingCount_sum"] = df["bld_n"] / 2
    df.loc[0, ["bld_n", "bld_ml_share"]] = [15.0, 0.3]
    cfg["building"]["reference"] = "usfs"
    d = building_draws(df, cfg, np.random.default_rng(0), 200)
    assert d.point[0] == pytest.approx(0.9, abs=0.01)
    assert d.point[5] == pytest.approx(0.0, abs=0.01)


def test_microsoft_draws_are_exact():
    from bbme.components.building import microsoft_draws

    df = pd.DataFrame(
        {
            "bld_n": [5.0, 20.0, 3.0],
            "bld_n_intersects": [6.0, 20.0, 3.0],
            "ms_n_centroid": [10.0, 10.0, 0.0],
        }
    )
    d = microsoft_draws(df, load("model"), 4)
    assert d.point.tolist() == [0.5, 0.0, 0.0]
    assert d.p_defined.tolist() == [1.0, 1.0, 0.0]
