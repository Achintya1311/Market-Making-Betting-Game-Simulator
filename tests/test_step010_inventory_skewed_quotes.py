from scaffold import inventory_skewed_quotes


def test_examples():
    q = inventory_skewed_quotes(100.0, 2.0, 0.0, 0.5)
    assert q == {'bid': 99.0, 'ask': 101.0}

    q2 = inventory_skewed_quotes(100.0, 2.0, 4.0, 0.5)
    assert (q2['bid'] + q2['ask']) / 2 < 100.0


def test_zero_inventory_or_zero_skew_gives_symmetric_quote():
    for inventory in [0.0]:
        for skew_strength in [0.0, 0.5, 2.0]:
            q = inventory_skewed_quotes(100.0, 2.0, inventory, skew_strength)
            assert q == {'bid': 99.0, 'ask': 101.0}
    for inventory in [-5.0, 0.0, 3.0]:
        q = inventory_skewed_quotes(100.0, 2.0, inventory, 0.0)
        assert q == {'bid': 99.0, 'ask': 101.0}


def test_spread_width_constant_across_inventory():
    fair_value, spread_width, skew_strength = 50.0, 4.0, 0.3
    for inventory in [-10.0, -1.0, 0.0, 2.0, 7.5]:
        q = inventory_skewed_quotes(fair_value, spread_width, inventory, skew_strength)
        assert round(q['ask'] - q['bid'], 9) == spread_width


def test_midpoint_formula_exact():
    fair_value, spread_width, skew_strength = 100.0, 2.0, 0.5
    for inventory in [-6.0, -2.0, 0.0, 3.0, 8.0]:
        q = inventory_skewed_quotes(fair_value, spread_width, inventory, skew_strength)
        mid = (q['bid'] + q['ask']) / 2
        expected_mid = fair_value - skew_strength * inventory
        assert abs(mid - expected_mid) < 1e-9


def test_midpoint_strictly_decreasing_in_inventory_when_skew_positive():
    fair_value, spread_width, skew_strength = 100.0, 2.0, 0.5
    inventories = [-5.0, -1.0, 0.0, 1.0, 5.0, 10.0]
    mids = []
    for inventory in inventories:
        q = inventory_skewed_quotes(fair_value, spread_width, inventory, skew_strength)
        mids.append((q['bid'] + q['ask']) / 2)
    for i in range(len(mids) - 1):
        assert mids[i + 1] < mids[i]


def test_long_inventory_shifts_down_short_shifts_up():
    fair_value, spread_width, skew_strength = 100.0, 2.0, 0.5
    long_q = inventory_skewed_quotes(fair_value, spread_width, 4.0, skew_strength)
    short_q = inventory_skewed_quotes(fair_value, spread_width, -4.0, skew_strength)
    assert (long_q['bid'] + long_q['ask']) / 2 < fair_value
    assert (short_q['bid'] + short_q['ask']) / 2 > fair_value
