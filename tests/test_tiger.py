from unittest import mock

import pandas as pd
import pytest

from bbme import db
from bbme.reference import tiger


def _tracts(con, raw, region):
    con.sql(
        """
        CREATE OR REPLACE TABLE tracts AS SELECT * FROM (VALUES
          ('48000000001', ST_GeomFromText('POLYGON((-98.01 30, -98 30, -98 30.01, -98.01 30.01,
                                                     -98.01 30))')),
          ('48000000002', ST_GeomFromText('POLYGON((-98 30, -97.99 30, -97.99 30.01, -98 30.01,
                                                     -98 30))'))
        ) v(GEOID, geometry)
        """
    )


def test_boundary_length_counts_shared_edge_in_both_tracts():
    con = db.connect()
    con.sql(
        """
        CREATE TABLE tiger AS SELECT * FROM (VALUES
          ('a', 'S1100', ST_GeomFromText('LINESTRING(-98.0 30.0, -98.0 30.01)')),
          ('b', 'S1200', ST_GeomFromText('LINESTRING(-98.005 30.0, -98.005 30.01)'))
        ) v(LINEARID, MTFCC, geometry)
        """
    )
    scored = pd.DataFrame({"GEOID": ["48000000001", "48000000002"], "region": "x"})
    with mock.patch.object(tiger, "load_tracts", _tracts):
        out = tiger.boundary_lengths(con, None, ["x"], scored, {"1m": 1e-5}).set_index("GEOID")
    edge = out.loc["48000000002", "tiger_len_m"]
    assert out.loc["48000000002", "tiger_bnd_1m_m"] == pytest.approx(edge)
    assert out.loc["48000000001", "tiger_len_m"] == pytest.approx(2 * edge, rel=1e-3)
    assert out.loc["48000000001", "tiger_bnd_1m_m"] == pytest.approx(edge, abs=5)
