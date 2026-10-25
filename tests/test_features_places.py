import pytest

from bbme import db
from bbme.config import load
from bbme.features import load_tracts
from bbme.features.places import place_features
from synthetic import REGION, TRACT_A, TRACT_B, build_raw


@pytest.fixture(scope="module")
def setup(tmp_path_factory):
    raw = build_raw(tmp_path_factory.mktemp("feat") / "raw")
    con = db.connect()
    load_tracts(con, raw, REGION)
    return con, raw


def test_place_groups(setup):
    con, raw = setup
    df = place_features(con, raw, REGION, load("poi_categories"), load("features"))
    a = df.set_index("GEOID").loc[TRACT_A]
    assert (a["poi_n"], a["poi_fire"], a["poi_school"], a["poi_hospital"], a["poi_ems"]) == (
        4,
        1,
        1,
        1,
        0,
    )
    assert a["poi_src_meta"] == 4
    assert TRACT_B not in set(df["GEOID"])
