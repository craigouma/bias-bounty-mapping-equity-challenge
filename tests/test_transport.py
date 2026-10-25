import numpy as np
import pandas as pd
import pytest

from bbme.components.transport import calibrate, reference_length, transport_draws
from bbme.config import load


def _frame(n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    ref = np.where(rng.random(n) < 0.5, 0.0, rng.uniform(500, 5000, n))
    return pd.DataFrame(
        {
            "region": ["maricopa-az"] * (n // 2) + ["eastern-wa"] * (n // 2),
            "road_refAmt_len": ref,
            "road_named_len": ref * rng.uniform(0.5, 1.5, n),
        }
    )


def test_calibration_hits_published_definedness():
    df, cfg = _frame(), load("model")
    cal = calibrate(df, reference_length(df, cfg), cfg)
    az = cal.loc["maricopa-az"]
    p_hi = cfg["transport"]["p_defined_above_tau"]
    mean_p = az["share_above_tau"] * p_hi + (1 - az["share_above_tau"]) * az["p_lo"]
    assert mean_p == pytest.approx(az["target_defined"], abs=0.02)
    assert cal.loc["eastern-wa", "tau"] == az["tau"]


def test_draws_shape_bounds_and_zero_overture():
    df, cfg = _frame(), load("model")
    df.loc[0, ["road_refAmt_len", "road_named_len"]] = [3000.0, 0.0]
    cal = calibrate(df, reference_length(df, cfg), cfg)
    d = transport_draws(df, cfg, cal, np.random.default_rng(1), 500)
    assert d.values.shape == (len(df), 500)
    assert np.isfinite(d.values).all()
    assert (d.values >= 0).all() and (d.values <= 1).all()
    assert d.point[0] == pytest.approx(1.0)
    assert d.p_defined[0] == cfg["transport"]["p_defined_above_tau"]


def test_boundary_knob_switches_to_buffered_length():
    df, cfg = _frame(), load("model")
    df["road_buf25_refAmt_len"] = df["road_refAmt_len"] + 100.0
    cfg["transport"]["boundary_d_m"] = 25
    assert (reference_length(df, cfg) == df["road_refAmt_len"] + 100.0).all()
