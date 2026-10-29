from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from bbme.submit import COLUMNS, assert_valid, compare, read_text_table, validate, write

REPO = Path(__file__).resolve().parents[1]
REAL_SAMPLE = REPO / "data" / "SampleSubmission.csv"
needs_sample = pytest.mark.skipif(not REAL_SAMPLE.exists(), reason="sample not downloaded")


@pytest.fixture
def mini_sample(tmp_path) -> Path:
    rows = [
        ["04013010101", "maricopa-az"],
        ["35023970000", "maricopa-az"],
        ["40013795900", "eastern-ok"],
        ["53001950100", "eastern-wa"],
    ]
    cells = ["0.0", "True"] * 7
    lines = [",".join(COLUMNS)] + [f"{g},0.0,{r}," + ",".join(cells) for g, r in rows]
    path = tmp_path / "sample.csv"
    path.write_text("\n".join(lines) + "\n")
    return path


def _pred(sample: pd.DataFrame) -> pd.DataFrame:
    n = len(sample)
    rng = np.random.default_rng(0)
    pred = pd.DataFrame({"GEOID": sample["GEOID"], "coverage_gap_score": rng.random(n)})
    for name in ["transport", "building"]:
        pred[f"{name}_gap"] = rng.random(n)
        pred[f"{name}_defined"] = rng.random(n) > 0.3
    for t in ["fire", "ems", "schools", "cbp"]:
        pred[f"poi_gap_{t}"] = rng.random(n)
        pred[f"poi_defined_{t}"] = rng.random(n) > 0.5
    pred["building_defined"] = True
    return pred


def _rewrite(path: Path, edit) -> Path:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = edit(df)
    out = path.with_name("broken.csv")
    out.write_text(df.to_csv(index=False, lineterminator="\n"))
    return out


def test_sample_validates_against_itself(mini_sample):
    assert validate(mini_sample, mini_sample) == []


@needs_sample
def test_real_sample_validates():
    assert validate(REAL_SAMPLE, REAL_SAMPLE) == []


@needs_sample
def test_writer_output_validates_on_real_sample(tmp_path):
    sample = read_text_table(REAL_SAMPLE)
    path = write(_pred(sample), sample, tmp_path / "sub.csv")
    assert_valid(path, REAL_SAMPLE)


def test_writer_rolls_up_poi_and_zeroes_undefined(mini_sample, tmp_path):
    sample = read_text_table(mini_sample)
    pred = _pred(sample)
    pred.loc[0, ["poi_gap_fire", "poi_gap_ems", "poi_gap_schools", "poi_gap_cbp"]] = [
        0.2,
        0.9,
        0.4,
        0.6,
    ]
    pred.loc[0, ["poi_defined_fire", "poi_defined_ems", "poi_defined_schools"]] = [
        True,
        False,
        True,
    ]
    pred.loc[0, "poi_defined_cbp"] = True
    pred.loc[1, ["poi_defined_fire", "poi_defined_ems", "poi_defined_schools"]] = False
    pred.loc[1, "poi_defined_cbp"] = False
    path = write(pred, sample, tmp_path / "sub.csv")
    assert_valid(path, mini_sample)
    out = read_text_table(path)
    assert float(out.loc[0, "poi_gap"]) == pytest.approx((0.3 + 0.6) / 2)
    assert out.loc[0, "poi_gap_ems"] == "0.0"
    assert out.loc[1, ["poi_gap", "poi_defined"]].tolist() == ["0.0", "False"]


def test_writer_never_uses_scientific_notation(mini_sample, tmp_path):
    sample = read_text_table(mini_sample)
    pred = _pred(sample)
    pred["coverage_gap_score"] = [1e-12, 3e-7, 0.123456789012345, 1.0]
    path = write(pred, sample, tmp_path / "sub.csv")
    scores = read_text_table(path)["coverage_gap_score"].tolist()
    assert scores == ["0.000000000001", "0.0000003", "0.123456789", "1.0"]
    assert_valid(path, mini_sample)


def test_writer_keeps_sample_row_order(mini_sample, tmp_path):
    sample = read_text_table(mini_sample)
    pred = _pred(sample).iloc[::-1]
    out = read_text_table(write(pred, sample, tmp_path / "sub.csv"))
    assert out["GEOID"].tolist() == sample["GEOID"].tolist()


def _drop_leading_zero(df):
    df.loc[0, "GEOID"] = df.loc[0, "GEOID"].lstrip("0")
    return df


def _set(col, value, row=0):
    def edit(df):
        df.loc[row, col] = value
        return df

    return edit


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda df: df.iloc[::-1], "GEOID order"),
        (lambda df: df.iloc[:-1], "rows"),
        (lambda df: df[COLUMNS[::-1]], "header"),
        (lambda df: df.assign(extra="1"), "header"),
        (_set("region", "eastern-ok"), "region"),
        (_set("poi_gap_cbp", ""), "blank"),
        (_set("coverage_gap_score", "1e-05"), "plain decimal"),
        (_set("coverage_gap_score", "nan"), "plain decimal"),
        (_set("coverage_gap_score", "1.5"), "outside"),
        (_set("transport_defined", "true"), "True/False"),
        (_set("building_defined", "1"), "True/False"),
        (_set("transport_gap", "0.5"), "transport_gap"),
        (_set("poi_gap", "0.5"), "poi_gap disagrees"),
        (_set("poi_defined", "False"), "poi_defined disagrees"),
    ],
)
def test_rejects_broken_copies(mini_sample, edit, message):
    if message == "transport_gap":
        edit_flag = _set("transport_defined", "False")
        broken = _rewrite(mini_sample, lambda df: edit(edit_flag(df)))
    else:
        broken = _rewrite(mini_sample, edit)
    errors = validate(broken, mini_sample)
    assert any(message in e for e in errors), errors


def test_rejects_all_undefined_rows(mini_sample):
    def edit(df):
        for c in COLUMNS:
            if "defined" in c:
                df.loc[0, c] = "False"
        return df

    errors = validate(_rewrite(mini_sample, edit), mini_sample)
    assert any("every top-level" in e for e in errors), errors


def test_rejects_crlf(mini_sample, tmp_path):
    broken = tmp_path / "crlf.csv"
    broken.write_bytes(mini_sample.read_bytes().replace(b"\n", b"\r\n"))
    assert any("CR" in e for e in validate(broken, mini_sample))


def test_rejects_index_column(mini_sample, tmp_path):
    df = pd.read_csv(mini_sample, dtype=str, keep_default_na=False)
    broken = tmp_path / "idx.csv"
    broken.write_text(df.to_csv(lineterminator="\n"))
    assert any("header" in e for e in validate(broken, mini_sample))


def test_rejects_numeric_geoid(mini_sample):
    broken = _rewrite(mini_sample, _drop_leading_zero)
    with pytest.raises(ValueError):
        validate(broken, mini_sample)


def test_compare_reports_float_and_flag_differences(mini_sample, tmp_path):
    sample = read_text_table(mini_sample)
    a = write(_pred(sample), sample, tmp_path / "a.csv")
    assert compare(a, a) == {"max_abs_diff": 0.0, "flag_mismatches": 0}
    edited = _pred(sample)
    edited.loc[0, "coverage_gap_score"] += 1e-3
    edited.loc[1, "transport_defined"] = not edited.loc[1, "transport_defined"]
    b = write(edited, sample, tmp_path / "b.csv")
    out = compare(a, b)
    assert out["max_abs_diff"] >= 1e-3 - 1e-9
    assert out["flag_mismatches"] == 1
