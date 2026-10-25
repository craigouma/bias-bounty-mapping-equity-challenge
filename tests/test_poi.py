import numpy as np
import pandas as pd
import pytest

from bbme.components.poi import facility_prior, poi_draws
from bbme.config import load


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": ["eastern-ok"] * 4,
            "pop_total": [4000.0, 4000.0, 0.0, 2000.0],
            "ALAND": [1e7, 1e7, 1e7, 1e7],
            "poi_fire": [2.0, 0.0, 0.0, 0.0],
            "poi_ems": [0.0, 0.0, 0.0, 1.0],
            "poi_school": [3.0, 0.0, 0.0, 1.0],
            "poi_n": [500.0, 10.0, 40.0, 0.0],
        }
    )


def test_prior_spreads_regional_total():
    df = _frame()
    prior = facility_prior(df, "fire", "pop_area")
    assert prior.sum() == pytest.approx(df["poi_fire"].sum())
    assert prior[2] == pytest.approx(0.5 * 2 * 0.25)


def test_draw_rules():
    df, cfg = _frame(), load("model")
    draws, sub = poi_draws(df, cfg, np.random.default_rng(0), 4000)
    assert sub["cbp"][1][2] == 0.0
    assert sub["cbp"][0][0] == pytest.approx(0.0, abs=1e-3)
    assert sub["cbp"][0][3] == 1.0
    fire_point, fire_p = sub["fire"]
    assert fire_point[1] == 1.0
    assert 0 < fire_p[1] < 1
    assert fire_p[0] > 0.6
    assert ((draws.values >= 0) & (draws.values <= 1)).all()
    assert draws.p_defined[0] == pytest.approx(1.0)
