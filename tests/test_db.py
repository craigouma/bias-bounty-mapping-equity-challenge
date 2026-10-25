import pytest
from pyproj import Geod

from bbme import db


@pytest.fixture(scope="module")
def con():
    return db.connect()


def test_length_matches_geodesic(con):
    lon1, lat1, lon2, lat2 = -98.5, 29.4, -98.4, 29.5
    wkt = f"ST_GeomFromText('LINESTRING({lon1} {lat1}, {lon2} {lat2})')"
    got = con.sql(f"SELECT {db.length_m(wkt)}").fetchone()[0]
    expected = Geod(ellps="WGS84").inv(lon1, lat1, lon2, lat2)[2]
    assert got == pytest.approx(expected, rel=1e-3)


def test_area_is_finite_and_plausible(con):
    wkt = "ST_GeomFromText('POLYGON((-98.5 29.4,-98.4 29.4,-98.4 29.5,-98.5 29.5,-98.5 29.4))')"
    got = con.sql(f"SELECT {db.area_m2(wkt)}").fetchone()[0]
    area, _ = Geod(ellps="WGS84").polygon_area_perimeter(
        [-98.5, -98.4, -98.4, -98.5], [29.4, 29.4, 29.5, 29.5]
    )
    assert got == pytest.approx(abs(area), rel=5e-3)


def test_assert_finite_catches_unflipped_spheroid_length(con):
    con.sql(
        "CREATE OR REPLACE TABLE t AS SELECT ST_Length_Spheroid("
        "ST_GeomFromText('LINESTRING(-98.5 29.4, -98.4 29.5)')) AS bad, 1.0 AS good"
    )
    db.assert_finite(con, "t", ["good"])
    with pytest.raises(ValueError, match="bad"):
        db.assert_finite(con, "t", ["good", "bad"])


def test_scan_goes_through_guard():
    assert "maricopa-az-overture-roads.parquet" in db.scan("x/maricopa-az-overture-roads.parquet")
    with pytest.raises(Exception, match="not a provided"):
        db.scan("x/maricopa-az-coverage-gap.parquet")
