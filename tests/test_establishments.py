import pandas as pd
import pytest

from bbme.reference.establishments import tract_establishments


def test_apportioning_by_area_and_population(tmp_path):
    rel = tmp_path / "tab20_zcta520_tract20_natl.txt"
    rel.write_text(
        "GEOID_ZCTA5_20|GEOID_TRACT_20|AREALAND_PART|AREALAND_ZCTA5_20|AREALAND_TRACT_20\n"
        "78701|48453000100|300|400|300\n"
        "78701|48453000200|100|400|200\n"
        "|48453000300|0||100\n"
    )
    zbp = pd.Series({"78701": 100})
    tracts = pd.DataFrame(
        {
            "GEOID": ["48453000100", "48453000200", "48453000300"],
            "region": ["south-central-tx"] * 3,
            "pop_total": [1000, 3000, 50],
            "poi_n": [40, 0, 5],
        }
    )
    out = tract_establishments(zbp, rel, tracts).set_index("GEOID")
    assert out.loc["48453000100", "est_area"] == pytest.approx(75)
    assert out.loc["48453000200", "est_area"] == pytest.approx(25)
    w1, w2 = 1000 * 300 / 300, 3000 * 100 / 200
    assert out.loc["48453000100", "est_pop"] == pytest.approx(100 * w1 / (w1 + w2))
    assert out.loc["48453000300", "est_area"] == 0
    assert out.loc["48453000100", "est_places"] == pytest.approx(100)
