import numpy as np
import pytest

from bbme.composite import COMPONENTS, Draws, analytic, bernoulli, monte_carlo, plug_in, shrink

S = 4000


def _degenerate(points: np.ndarray, p: np.ndarray) -> dict[str, Draws]:
    n = len(points)
    out = {}
    for j, c in enumerate(COMPONENTS):
        values = np.repeat(points[:, j : j + 1], S, axis=1)
        flags = np.repeat((p[:, j : j + 1] >= 0.5), S, axis=1)
        out[c] = Draws(values, flags, points[:, j], p[:, j])
    assert len(out["poi"].point) == n
    return out


def test_monte_carlo_equals_plug_in_when_degenerate():
    points = np.array([[0.2, 0.0, 0.6], [1.0, 0.1, 0.3], [0.5, 0.5, 0.5]])
    p = np.array([[1, 1, 1], [0, 1, 1], [0, 0, 1]], dtype=float)
    draws = _degenerate(points, p)
    y, kept = monte_carlo(draws)
    assert y == pytest.approx(plug_in(draws))
    assert y == pytest.approx([0.8 / 3, 0.2, 0.5])
    assert kept.tolist() == [S, S, S]


def test_all_undefined_draws_are_discarded():
    rng = np.random.default_rng(0)
    p = np.array([0.5])
    draws = {
        "transport": Draws(np.ones((1, S)), bernoulli(rng, p, S), np.ones(1), p),
        "building": Draws(np.zeros((1, S)), np.zeros((1, S), bool), np.zeros(1), np.zeros(1)),
        "poi": Draws(np.zeros((1, S)), np.zeros((1, S), bool), np.zeros(1), np.zeros(1)),
    }
    y, kept = monte_carlo(draws)
    assert y[0] == pytest.approx(1.0)
    assert 0.4 * S < kept[0] < 0.6 * S


def test_monte_carlo_matches_analytic_under_independence():
    rng = np.random.default_rng(1)
    n = 50
    p = rng.uniform(0.05, 0.95, (n, 3))
    mu = rng.uniform(0, 1, (n, 3))
    draws = {
        c: Draws(
            np.repeat(mu[:, j : j + 1], 20000, axis=1),
            bernoulli(rng, p[:, j], 20000),
            mu[:, j],
            p[:, j],
        )
        for j, c in enumerate(COMPONENTS)
    }
    y, _ = monte_carlo(draws)
    assert np.abs(y - analytic(p, mu)).max() < 0.02


def test_analytic_single_component():
    p = np.array([[1.0, 0.0, 0.0]])
    mu = np.array([[0.7, 0.1, 0.9]])
    assert analytic(p, mu)[0] == pytest.approx(0.7)


def test_plug_in_falls_back_to_likeliest_component():
    points = np.array([[0.9, 0.1, 0.4]])
    p = np.array([[0.3, 0.2, 0.4]])
    draws = _degenerate(points, p)
    assert plug_in(draws)[0] == pytest.approx(0.4)


def test_shrink_and_clip():
    y = np.array([0.0, 1.0])
    assert shrink(y, 1.0).tolist() == [0.0, 1.0]
    assert shrink(y, 0.5).tolist() == [0.25, 0.75]
