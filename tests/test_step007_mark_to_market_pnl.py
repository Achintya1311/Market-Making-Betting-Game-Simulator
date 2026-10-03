from scaffold import mark_to_market_pnl, execute_trade


def test_examples():
    assert mark_to_market_pnl(10.0, 2.0, 5.0) == 20.0
    assert mark_to_market_pnl(0.0, -3.0, 4.0) == -12.0


def test_zero_inventory_gives_pnl_equal_cash():
    for cash in [-10.0, 0.0, 3.5, 100.0]:
        for settlement in [-5.0, 0.0, 7.0]:
            assert mark_to_market_pnl(cash, 0.0, settlement) == cash


def test_linear_in_settlement_value():
    cash, inventory = 4.0, 2.0
    settlements = [-10.0, -1.0, 0.0, 1.0, 10.0]
    pnls = [mark_to_market_pnl(cash, inventory, s) for s in settlements]
    for s, pnl in zip(settlements, pnls):
        assert abs(pnl - (cash + inventory * s)) < 1e-9
    # strictly increasing since inventory > 0
    for i in range(len(pnls) - 1):
        assert pnls[i] < pnls[i + 1]


def test_buy_then_sell_round_trip_pnl_matches_spread_for_every_settlement():
    bid, ask, size = 99.0, 101.0, 3
    state = {'cash': 0.0, 'inventory': 0.0}
    state = execute_trade(state, 'buy', bid, ask, size=size)
    state = execute_trade(state, 'sell', bid, ask, size=size)
    for settlement in [-50.0, 0.0, 50.0, 1000.0]:
        pnl = mark_to_market_pnl(state['cash'], state['inventory'], settlement)
        assert abs(pnl - size * (ask - bid)) < 1e-9


def test_negative_pnl_is_legitimate():
    assert mark_to_market_pnl(0.0, 1.0, -5.0) == -5.0
    assert mark_to_market_pnl(-2.0, 0.0, 100.0) == -2.0


def test_no_abs_no_clamp():
    # short position losing money when settlement is high must stay negative
    assert mark_to_market_pnl(4.0, -1.0, 5.0) == -1.0
