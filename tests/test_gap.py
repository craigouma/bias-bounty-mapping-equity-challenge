import numpy as np
import pytest

from bbme.components.gap import defined, gap, mean_defined


def test_zero_overture_gives_one():
    assert gap(np.array([0.0]), np.array([5.0]))[0] == 1.0


def test_full_or_excess_coverage_gives_zero():
    assert gap(np.array([5.0, 9.0]), np.array([5.0, 5.0])).tolist() == [0.0, 0.0]


def test_partial_coverage():
    assert gap(np.array([3.0]), np.array([4.0]))[0] == pytest.approx(0.25)


def test_zero_reference_is_undefined():
    assert np.isnan(gap(np.array([3.0]), np.array([0.0]))[0])
    assert not defined(np.array([0.0]))[0]


def test_divisor_follows_definedness():
    values = np.array([[0.2, 0.8, 0.5], [0.2, 0.8, 0.5]])
    flags = np.array([[True, True, True], [True, False, False]])
    mean, any_defined = mean_defined(values, flags, axis=1)
    assert mean.tolist() == pytest.approx([0.5, 0.2])
    assert any_defined.tolist() == [True, True]


def test_all_undefined_row_is_flagged():
    mean, any_defined = mean_defined(np.array([[0.4, 0.9]]), np.array([[False, False]]), axis=1)
    assert mean.tolist() == [0.0]
    assert any_defined.tolist() == [False]
