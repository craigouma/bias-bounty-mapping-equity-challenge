import pytest

from bbme import db
from bbme.config import load
from bbme.features.build import build, calibration, column_doc, summary
from synthetic import REGION, TRACT_A, TRACT_B, build_raw


@pytest.fixture(scope="module")
def features(tmp_path_factory):
    raw = build_raw(tmp_path_factory.mktemp("build") / "raw")
    cfg = {
        "data": {"regions": [REGION]},
        "features": load("features"),
        "poi": load("poi_categories"),
    }
    return build(db.connect(), raw, cfg)


def test_one_row_per_scored_tract_with_explicit_zeros(features):
    assert features["GEOID"].tolist() == [TRACT_A, TRACT_B]
    b = features.set_index("GEOID").loc[TRACT_B]
    assert b["poi_n"] == 0
    assert b["poi_fire"] == 0
    assert b["infra_n"] == 0
    assert summary(features)["non_finite_numeric_cells"] == 0


def test_calibration_and_docs(features):
    cal = calibration(features, load("features"))[REGION]
    assert set(cal["sets"]) >= {"A", "A_buf25", "C"}
    assert 0 <= cal["sets"]["A"]["share_ref_le_tau"]["0"] <= 1
    doc = column_doc(features)
    assert "| road_named_len |" in doc
