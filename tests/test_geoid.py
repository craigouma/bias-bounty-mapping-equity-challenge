import pandas as pd
import pytest

from bbme.geoid import assert_geoids, read_csv


def test_csv_read_keeps_leading_zeros(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("GEOID,x\n04013010101,1\n35023970000,2\n")
    df = read_csv(path)
    assert df["GEOID"].tolist() == ["04013010101", "35023970000"]


@pytest.mark.parametrize(
    "values",
    [
        ["4013010101"],
        ["040130101011"],
        ["0401301010a"],
    ],
)
def test_rejects_malformed_geoids(values):
    with pytest.raises(ValueError):
        assert_geoids(pd.Series(values))


def test_rejects_numeric_geoids():
    with pytest.raises(TypeError):
        assert_geoids(pd.Series([4013010101]))


def test_rejects_numeric_csv_read(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("GEOID\n04013010101\n")
    with pytest.raises(TypeError):
        assert_geoids(pd.read_csv(path)["GEOID"])
