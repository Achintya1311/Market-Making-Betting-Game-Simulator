from scaffold import execute_trade


def test_examples():
    result = execute_trade({'cash': 0.0, 'inventory': 0.0}, 'buy', 99.5, 100.5, size=1)
    assert result == {'cash': 100.5, 'inventory': -1.0}

    result = execute_trade({'cash': 0.0, 'inventory': 0.0}, 'sell', 99.5, 100.5, size=2)
    assert result == {'cash': -199.0, 'inventory': 2.0}


def test_input_not_mutated():
    state = {'cash': 10.0, 'inventory': 3.0}
    original = dict(state)
    execute_trade(state, 'buy', 9.0, 11.0, size=1)
    assert state == original
    execute_trade(state, 'sell', 9.0, 11.0, size=1)
    assert state == original


def test_buy_then_sell_round_trip():
    bid, ask, size = 99.0, 101.0, 3
    state = {'cash': 0.0, 'inventory': 0.0}
    state = execute_trade(state, 'buy', bid, ask, size=size)
    state = execute_trade(state, 'sell', bid, ask, size=size)
    assert state['inventory'] == 0.0
    assert abs(state['cash'] - size * (ask - bid)) < 1e-9


def test_inventory_change_signs():
    for size in [1, 2, 5]:
        buy_result = execute_trade({'cash': 0.0, 'inventory': 0.0}, 'buy', 9.0, 11.0, size=size)
        assert buy_result['inventory'] == -float(size)

        sell_result = execute_trade({'cash': 0.0, 'inventory': 0.0}, 'sell', 9.0, 11.0, size=size)
        assert sell_result['inventory'] == float(size)
