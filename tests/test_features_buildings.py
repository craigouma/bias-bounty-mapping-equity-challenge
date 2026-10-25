import pytest

from bbme import db
from bbme.config import load
from bbme.features import load_tracts
from bbme.features.buildings import building_features
from synthetic import REGION, TRACT_A, TRACT_B, build_raw


@pytest.fixture(scope="module")
def setup(tmp_path_factory):
    raw = build_raw(tmp_path_factory.mktemp("feat") / "raw")
    con = db.connect()
    load_tracts(con, raw, REGION)
    return con, raw


def test_building_counts_and_source_mix(setup):
    con, raw = setup
    df = building_features(con, raw, REGION, load("features")).set_index("GEOID")
    a, b = df.loc[TRACT_A], df.loc[TRACT_B]
    assert (a["bld_n"], a["bld_n_osm"], a["bld_n_microsoft"]) == (3, 1, 2)
    assert a["bld_ml_share"] == pytest.approx(2 / 3)
    assert a["bld_osm_large_n_500"] == 1
    assert a["bld_suppressed_500"] == pytest.approx(0, abs=0.05)
    assert b["bld_n"] == 1
    assert a["bld_area_median"] == pytest.approx(31 * 33.4 * 0.835, rel=0.1)
