from scaffold import make_quotes


def test_examples():
    result = make_quotes(100.0, 2.0)
    assert result == {'bid': 99.0, 'ask': 101.0}

    result = make_quotes(50.0, 0.0)
    assert result == {'bid': 50.0, 'ask': 50.0}


def test_midpoint_equals_fair_value():
    for fv in [-10.0, 0.0, 3.5, 100.0, 250.25]:
        for w in [0.0, 0.5, 1.0, 2.0, 10.0]:
            result = make_quotes(fv, w)
            assert abs((result['bid'] + result['ask']) / 2.0 - fv) < 1e-9


def test_spread_equals_width():
    for fv in [-10.0, 0.0, 3.5, 100.0, 250.25]:
        for w in [0.0, 0.5, 1.0, 2.0, 10.0]:
            result = make_quotes(fv, w)
            assert abs((result['ask'] - result['bid']) - w) < 1e-9


def test_bid_le_ask():
    for fv in [-10.0, 0.0, 3.5, 100.0]:
        for w in [0.0, 0.5, 1.0, 2.0, 10.0]:
            result = make_quotes(fv, w)
            assert result['bid'] <= result['ask']


def test_zero_width_bid_equals_ask_equals_fair():
    for fv in [-5.0, 0.0, 42.0]:
        result = make_quotes(fv, 0.0)
        assert result['bid'] == fv
        assert result['ask'] == fv
