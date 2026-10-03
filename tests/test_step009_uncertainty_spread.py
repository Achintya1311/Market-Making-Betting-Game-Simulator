from scaffold import uncertainty_spread


def test_examples():
    assert uncertainty_spread(1.0, 0.0) >= 1.0
    assert uncertainty_spread(1.0, 2.0) > uncertainty_spread(1.0, 0.5)


def test_pinned_formula_exact():
    for base_spread in [0.0, 0.5, 1.0, 3.25, 10.0]:
        for uncertainty in [0.0, 0.1, 1.0, 2.5, 7.0]:
            assert uncertainty_spread(base_spread, uncertainty) == base_spread + uncertainty


def test_at_least_base_spread():
    for base_spread in [0.0, 0.5, 2.0, 5.0]:
        for uncertainty in [0.0, 0.3, 1.0, 10.0]:
            assert uncertainty_spread(base_spread, uncertainty) >= base_spread


def test_strictly_increasing_in_uncertainty():
    base_spread = 1.5
    uncertainties = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
    for i in range(len(uncertainties) - 1):
        lo = uncertainty_spread(base_spread, uncertainties[i])
        hi = uncertainty_spread(base_spread, uncertainties[i + 1])
        assert hi > lo


def test_return_type_is_float():
    result = uncertainty_spread(1.0, 2.0)
    assert isinstance(result, float)
    result_zero = uncertainty_spread(0.0, 0.0)
    assert isinstance(result_zero, float)
