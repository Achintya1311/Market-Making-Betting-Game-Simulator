import numpy as np

from scaffold import summarize_episode_pnls


def test_examples():
    res = summarize_episode_pnls([1.0, 2.0, 3.0, 4.0])
    assert res['mean'] == 2.5
    assert res['std'] == 1.118033988749895
    assert res['worst'] == 1.0

    res = summarize_episode_pnls([-5.0, 0.0, 5.0])
    assert res['mean'] == 0.0
    assert res['std'] == 4.08248290463863
    assert res['worst'] == -5.0


def test_min_le_mean_le_max():
    grids = [[1.0, 2.0, 3.0, 4.0], [-5.0, 0.0, 5.0], [7.0], [-2.0, -2.0, 3.0, 10.0]]
    for pnls in grids:
        res = summarize_episode_pnls(pnls)
        assert min(pnls) <= res['mean'] <= max(pnls)


def test_std_non_negative():
    grids = [[1.0, 2.0, 3.0, 4.0], [-5.0, 0.0, 5.0], [7.0], [-2.0, -2.0, 3.0, 10.0]]
    for pnls in grids:
        res = summarize_episode_pnls(pnls)
        assert res['std'] >= 0.0


def test_constant_series_gives_zero_std_and_worst_equals_constant():
    for c in (0.0, 5.0, -3.5):
        res = summarize_episode_pnls([c] * 5)
        assert res['std'] == 0.0
        assert res['worst'] == c
        assert res['mean'] == c


def test_worst_le_mean():
    grids = [[1.0, 2.0, 3.0, 4.0], [-5.0, 0.0, 5.0], [-2.0, -2.0, 3.0, 10.0]]
    for pnls in grids:
        res = summarize_episode_pnls(pnls)
        assert res['worst'] <= res['mean']


def test_adding_constant_shifts_mean_and_worst_leaves_std_unchanged():
    pnls = [1.0, 2.0, 3.0, 4.0, -10.0]
    base = summarize_episode_pnls(pnls)
    for c in (3.0, -7.0):
        shifted = summarize_episode_pnls([x + c for x in pnls])
        assert np.isclose(shifted['mean'], base['mean'] + c)
        assert np.isclose(shifted['worst'], base['worst'] + c)
        assert np.isclose(shifted['std'], base['std'])


def test_scaling_by_positive_k_scales_all_three():
    pnls = [1.0, 2.0, 3.0, 4.0, -10.0]
    base = summarize_episode_pnls(pnls)
    for k in (2.0, 0.5):
        scaled = summarize_episode_pnls([x * k for x in pnls])
        assert np.isclose(scaled['mean'], base['mean'] * k)
        assert np.isclose(scaled['worst'], base['worst'] * k)
        assert np.isclose(scaled['std'], base['std'] * k)


def test_return_types_are_python_float():
    res = summarize_episode_pnls([1.0, 2.0, 3.0, 4.0])
    for key in ('mean', 'std', 'worst'):
        assert isinstance(res[key], float)
        assert not isinstance(res[key], np.floating)
