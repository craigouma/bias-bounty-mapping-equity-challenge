import pandas as pd

from bbme import db
from bbme.config import load
from bbme.features.build import build
from bbme.model import metrics, predict, submission_frame
from bbme.submit import COLUMNS, assert_valid, write
from synthetic import REGION, TRACT_A, TRACT_B, build_raw


def test_end_to_end_on_synthetic(tmp_path):
    raw = build_raw(tmp_path / "raw")
    cfg = {
        "data": {"regions": [REGION]},
        "features": load("features"),
        "poi": load("poi_categories"),
    }
    df = build(db.connect(), raw, cfg)
    model = load("model")
    model["mc_draws"] = 300
    model["published_undefined_rate"] = {REGION: 0.5}
    comp, _ = predict(df, model)
    assert metrics(comp)["non_finite"] == 0
    sample = df[["GEOID", "region"]]
    sample_path = tmp_path / "sample.csv"
    lines = [",".join(COLUMNS)] + [
        f"{g},0.0,{r}," + ",".join(["0.0", "True"] * 7) for g, r in sample.itertuples(index=False)
    ]
    sample_path.write_text("\n".join(lines) + "\n")
    path = write(submission_frame(comp), sample, tmp_path / "sub.csv")
    assert_valid(path, sample_path)
    out = pd.read_csv(path, dtype={"GEOID": str}).set_index("GEOID")
    assert 0 <= out.loc[TRACT_A, "coverage_gap_score"] <= 1
    assert out.loc[TRACT_B, "poi_defined_cbp"] == False  # noqa: E712
    again, _ = predict(df, model)
    assert again["coverage_gap_score"].equals(comp["coverage_gap_score"])


def test_constant_poi_mode_flattens_poi_within_region(tmp_path):
    raw = build_raw(tmp_path / "raw")
    cfg = {
        "data": {"regions": [REGION]},
        "features": load("features"),
        "poi": load("poi_categories"),
    }
    df = build(db.connect(), raw, cfg)
    model = load("model")
    model["mc_draws"] = 200
    model["published_undefined_rate"] = {REGION: 0.5}
    model["poi"]["mode"] = "constant"
    comp, _ = predict(df, model)
    assert (comp["poi_point"] == comp["poi_point"].iloc[0]).all()


def test_component_streams_are_independent(tmp_path):
    raw = build_raw(tmp_path / "raw")
    cfg = {
        "data": {"regions": [REGION]},
        "features": load("features"),
        "poi": load("poi_categories"),
    }
    df = build(db.connect(), raw, cfg)
    df["usfs_BuildingCount_sum"] = df["bld_n"] + 1
    model = load("model")
    model["mc_draws"] = 200
    model["published_undefined_rate"] = {REGION: 0.5}
    base, _ = predict(df, model)
    model["building"]["reference"] = "usfs"
    changed, _ = predict(df, model)
    assert changed["transport_point"].equals(base["transport_point"])
