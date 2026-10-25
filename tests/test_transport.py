import numpy as np
import pandas as pd
import pytest

from bbme.components.transport import calibrate, reference_lengths, tiers, transport_draws
from bbme.config import load


def _frame(n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    u = rng.random(n)
    primary = np.where(u < 0.5, 0.0, rng.uniform(500, 5000, n))
    secondary = primary + np.where((u >= 0.3) & (u < 0.5), 800.0, 0.0)
    df = pd.DataFrame(
        {
            "region": ["south-central-tx"] * (n // 2) + ["eastern-wa"] * (n // 2),
            "road_refAmt_len": primary,
            "road_refBmt_len": secondary,
            "road_named_len": primary * rng.uniform(0.5, 1.5, n),
        }
    )
    df["road_buf25_refAmt_len"] = df["road_refAmt_len"]
    df["road_buf25_refBmt_len"] = df["road_refBmt_len"]
    return df


def test_tiers():
    got = tiers(np.array([5.0, 0.0, 0.0]), np.array([5.0, 3.0, 0.0])).tolist()
    assert got == ["high", "mid", "low"]


def test_calibration_hits_published_definedness():
    df, cfg = _frame(), load("model")
    cal = calibrate(df, cfg)
    tx = cal.loc["south-central-tx"]
    t = cfg["transport"]
    assert tx["mean_p_defined"] == pytest.approx(tx["target_defined"], abs=1e-6)
    assert t["p_defined_floor"] <= tx["p_mid"] <= t["p_defined_high"]
    assert cal.loc["eastern-wa", "p_mid"] == tx["p_mid"]


def test_draws_shape_bounds_and_zero_overture():
    df, cfg = _frame(), load("model")
    cols = ["road_buf25_refAmt_len", "road_buf25_refBmt_len", "road_named_len"]
    df.loc[0, cols] = [3000.0, 3000.0, 0.0]
    cal = calibrate(df, cfg)
    d = transport_draws(df, cfg, cal, np.random.default_rng(1), 500)
    assert d.values.shape == (len(df), 500)
    assert np.isfinite(d.values).all()
    assert (d.values >= 0).all() and (d.values <= 1).all()
    assert d.point[0] == pytest.approx(1.0)
    assert d.p_defined[0] == cfg["transport"]["p_defined_high"]


def test_boundary_knob_switches_to_buffered_length():
    df, cfg = _frame(), load("model")
    df["road_buf25_refAmt_len"] = df["road_refAmt_len"] + 100.0
    cfg["transport"]["boundary_d_m"] = 25
    primary, _ = reference_lengths(df, cfg)
    assert (primary == df["road_refAmt_len"] + 100.0).all()
    cfg["transport"]["boundary_d_m"] = 0
    primary, _ = reference_lengths(df, cfg)
    assert (primary == df["road_refAmt_len"]).all()
