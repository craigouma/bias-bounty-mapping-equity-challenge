import pytest

from bbme import db
from bbme.config import load
from bbme.features.strata import strata_features
from synthetic import REGION, TRACT_A, TRACT_B, build_raw


def test_context_columns_and_water_share(tmp_path):
    raw = build_raw(tmp_path / "raw")
    df = strata_features(db.connect(), raw, REGION, load("features")).set_index("GEOID")
    assert set(load("features")["strata_columns"]) <= set(df.columns)
    assert df.loc[TRACT_A, "acs_housing_units"] == 500
    assert df.loc[TRACT_B, "water_share"] == pytest.approx(0.95)
    assert df.loc[TRACT_B, "mtbs_burned_pct_2015"] == 12.5
    assert df.loc[TRACT_A, "COUNTYFP"] == "013"
