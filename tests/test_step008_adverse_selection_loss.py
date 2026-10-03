import numpy as np

from scaffold import adverse_selection_loss


def test_example():
    vals = [98.0, 100.0, 102.0]
    probs = [1 / 3, 1 / 3, 1 / 3]
    assert round(adverse_selection_loss(100.0, 99.0, 101.0, vals, probs), 4) == 0.6667


def test_result_non_negative():
    rng = np.random.default_rng(0)
    for _ in range(10):
        vals = rng.uniform(80.0, 120.0, size=5)
        probs = rng.uniform(0.1, 1.0, size=5)
        probs = probs / probs.sum()
        loss = adverse_selection_loss(100.0, 99.0, 101.0, vals, probs)
        assert loss >= 0.0


def test_zero_when_all_values_within_quotes():
    bid, ask = 99.0, 101.0
    vals = [99.0, 100.0, 101.0, 99.5, 100.9]
    probs = [0.2, 0.2, 0.2, 0.2, 0.2]
    assert adverse_selection_loss(100.0, bid, ask, vals, probs) == 0.0


def test_point_mass_above_ask_gives_exact_excess():
    bid, ask = 99.0, 101.0
    loss = adverse_selection_loss(100.0, bid, ask, [105.0], [1.0])
    assert abs(loss - (105.0 - ask)) < 1e-9


def test_point_mass_below_bid_gives_exact_excess():
    bid, ask = 99.0, 101.0
    loss = adverse_selection_loss(100.0, bid, ask, [95.0], [1.0])
    assert abs(loss - (bid - 95.0)) < 1e-9


def test_narrowing_quotes_never_lowers_loss():
    fair_value = 100.0
    vals = [90.0, 96.0, 100.0, 104.0, 110.0]
    probs = [0.2, 0.2, 0.2, 0.2, 0.2]
    wide = adverse_selection_loss(fair_value, 97.0, 103.0, vals, probs)
    narrow = adverse_selection_loss(fair_value, 99.0, 101.0, vals, probs)
    narrower = adverse_selection_loss(fair_value, 99.9, 100.1, vals, probs)
    assert narrow >= wide
    assert narrower >= narrow


def test_return_type_float():
    result = adverse_selection_loss(100.0, 99.0, 101.0, [98.0, 102.0], [0.5, 0.5])
    assert isinstance(result, float)
