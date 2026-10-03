from scaffold import expected_value


def test_examples():
    assert expected_value([1, 2, 3, 4, 5, 6], [1 / 6] * 6) == 3.5
    assert expected_value([10, -5], [0.2, 0.8]) == -2.0


def test_uniform_die_ev_is_midpoint():
    for n in range(1, 21):
        values = list(range(1, n + 1))
        probs = [1.0 / n] * n
        assert abs(expected_value(values, probs) - (n + 1) / 2) < 1e-9


def test_constant_distribution_equals_constant():
    for c in [-10.0, 0.0, 3.5, 100.0]:
        for n in [1, 2, 5]:
            values = [c] * n
            probs = [1.0 / n] * n
            assert abs(expected_value(values, probs) - c) < 1e-9


def test_linearity():
    values = [1, 2, 3, 4, 5]
    probs = [0.1, 0.2, 0.3, 0.1, 0.3]
    base = expected_value(values, probs)
    for a in [-2.0, 0.0, 1.0, 3.5]:
        for b in [-5.0, 0.0, 2.0]:
            scaled_values = [a * v + b for v in values]
            scaled_ev = expected_value(scaled_values, probs)
            assert abs(scaled_ev - (a * base + b)) < 1e-9


def test_return_type_is_float():
    result = expected_value([1, 2, 3], [0.2, 0.3, 0.5])
    assert isinstance(result, float)
    assert not isinstance(result, bool)


def test_does_not_renormalize_probabilities():
    # Caller guarantees a valid distribution; function must not alter the
    # weighting behavior by renormalizing already-valid probabilities.
    assert expected_value([1, 2, 3], [1 / 3, 1 / 3, 1 / 3]) == 2.0
