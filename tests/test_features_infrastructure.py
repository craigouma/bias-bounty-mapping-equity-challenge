import pytest

from bbme import db
from bbme.features import load_tracts
from bbme.features.infrastructure import infrastructure_features
from synthetic import REGION, TRACT_A, TRACT_B, build_raw


def test_infrastructure_counts_and_rail_split(tmp_path):
    raw = build_raw(tmp_path / "raw")
    con = db.connect()
    load_tracts(con, raw, REGION)
    df = infrastructure_features(con, raw, REGION).set_index("GEOID")
    assert df.loc[TRACT_A, "infra_transit"] == 1
    total = df["rail_len_m"].sum()
    assert total == pytest.approx(0.10 * 111_320 * 0.8371, rel=0.01)
    assert df.loc[TRACT_A, "rail_len_m"] == pytest.approx(df.loc[TRACT_B, "rail_len_m"], rel=0.01)
