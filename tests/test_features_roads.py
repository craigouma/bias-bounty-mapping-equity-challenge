import pytest

from bbme import db
from bbme.config import load
from bbme.features import load_tracts
from bbme.features.roads import road_features
from synthetic import REGION, TRACT_A, TRACT_B, build_raw

DEG_LAT_M = 110_900


@pytest.fixture(scope="module")
def roads(tmp_path_factory):
    raw = build_raw(tmp_path_factory.mktemp("roads") / "raw")
    con = db.connect()
    load_tracts(con, raw, REGION)
    return road_features(con, raw, REGION, load("features")).set_index("GEOID").fillna(0)


def test_named_length_counts_boundary_motorway_in_both_tracts(roads):
    motorway = 0.05 * DEG_LAT_M
    assert roads.loc[TRACT_B, "road_len_motorway"] == pytest.approx(motorway, rel=0.01)
    assert roads.loc[TRACT_A, "road_len_motorway"] == pytest.approx(motorway, rel=0.01)
    assert roads.loc[TRACT_B, "road_named_len"] == pytest.approx(motorway, rel=0.01)


def test_route_groups_and_reference_sets(roads):
    a = roads.loc[TRACT_A]
    assert a["road_route_interstate_len"] > 0
    assert a["road_route_state_len"] > 0
    assert a["road_route_state_secondary_len"] > 0
    assert a["road_refC_len"] >= a["road_refB_len"] >= a["road_refA_len"]
    assert a["road_refB_len"] - a["road_refA_len"] == pytest.approx(
        a["road_len_tertiary"], rel=1e-6
    )


def test_unnamed_residential(roads):
    b = roads.loc[TRACT_B]
    assert b["road_len_unnamed"] == pytest.approx(b["road_len_residential"])


def test_buffer_never_shrinks_length(roads):
    for d in load("features")["boundary_distances_m"]:
        assert (roads[f"road_buf{d}_named_len"] >= roads["road_named_len"] - 1e-6).all()


@pytest.mark.parametrize(
    ("network", "group"),
    [
        ("US:I", "interstate"),
        ("US:US", "us_route"),
        ("US:TX", "state"),
        ("US:OK", "state"),
        ("US:TX:FM", "state_secondary"),
        ("US:TX:Loop", "state_secondary"),
        ("US:AZ:Loop", "state_secondary"),
        ("US:OK:Turnpike", "toll"),
        ("US:TX:NTTA", "toll"),
        ("US:US:Business", "business"),
        ("US:I:Business:Loop", "business"),
        ("US:OK:Washita", "county"),
        ("US:TX:Jim_Wells", "county"),
        ("US:CA:CR", "county"),
        ("US:NHT", "other"),
        ("US:US:Historic", "other"),
        ("", "other"),
    ],
)
def test_network_group_assignment(network, group):
    from bbme.features.roads import _group_case

    case = _group_case(load("features")["route_groups"])
    got = (
        db.connect().sql(f"SELECT {case} FROM (SELECT {{'network': '{network}'}} AS x)").fetchone()
    )
    assert got[0] == group


def test_unclipped_lengths_cover_whole_segments(roads):
    a = roads.loc[TRACT_A]
    assert a["road_named_unclipped_len"] >= a["road_named_len"] - 1e-6
    assert a["road_refAmt_unclipped_len"] >= a["road_refAmt_len"] - 1e-6
    assert a["road_refAmt_nolink_len"] == pytest.approx(a["road_refAmt_len"])
    assert a["road_named_link_len"] == 0
