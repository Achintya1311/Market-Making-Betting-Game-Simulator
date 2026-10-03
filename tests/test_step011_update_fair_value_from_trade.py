from scaffold import update_fair_value_from_trade


def test_examples():
    assert update_fair_value_from_trade(100.0, 'buy', 99.0, 101.0, 0.0) == 100.0

    up = update_fair_value_from_trade(100.0, 'buy', 99.0, 101.0, 0.5)
    assert up > 100.0

    down = update_fair_value_from_trade(100.0, 'sell', 99.0, 101.0, 0.5)
    assert down < 100.0


def test_adjustment_zero_returns_fair_value_unchanged():
    for fair_value in [50.0, 100.0, -3.0]:
        for side in ['buy', 'sell']:
            for bid, ask in [(99.0, 101.0), (0.0, 10.0), (49.5, 50.5)]:
                result = update_fair_value_from_trade(fair_value, side, bid, ask, 0.0)
                assert result == fair_value


def test_buy_then_sell_same_quotes_and_adjustment_returns_original():
    for fair_value in [100.0, 25.0, -10.0]:
        for adjustment in [0.1, 0.5, 2.0]:
            bid, ask = 99.0, 101.0
            after_buy = update_fair_value_from_trade(fair_value, 'buy', bid, ask, adjustment)
            after_sell = update_fair_value_from_trade(after_buy, 'sell', bid, ask, adjustment)
            assert abs(after_sell - fair_value) < 1e-9


def test_strictly_monotone_in_adjustment():
    fair_value, bid, ask = 100.0, 99.0, 101.0
    adjustments = [0.0, 0.25, 0.5, 1.0, 2.0]

    buy_values = [update_fair_value_from_trade(fair_value, 'buy', bid, ask, a) for a in adjustments]
    for i in range(len(buy_values) - 1):
        assert buy_values[i + 1] > buy_values[i]

    sell_values = [update_fair_value_from_trade(fair_value, 'sell', bid, ask, a) for a in adjustments]
    for i in range(len(sell_values) - 1):
        assert sell_values[i + 1] < sell_values[i]


def test_return_type_is_float():
    result = update_fair_value_from_trade(100.0, 'buy', 99.0, 101.0, 0.5)
    assert isinstance(result, float)
