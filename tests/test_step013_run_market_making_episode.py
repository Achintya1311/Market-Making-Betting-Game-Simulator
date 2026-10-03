from scaffold import run_market_making_episode, mark_to_market_pnl


def test_example():
    cfg = {'base_spread': 2.0, 'uncertainty': 0.0, 'skew_strength': 0.0, 'belief_adjustment': 0.0}
    res = run_market_making_episode(100.0, ['buy', 'sell'], 100.0, cfg)
    assert (res['cash'], res['inventory'], res['pnl']) == (2.0, 0.0, 2.0)
    assert len(res['history']) == 2


def test_history_length_matches_sides():
    cfg = {'base_spread': 1.0, 'uncertainty': 0.0, 'skew_strength': 0.0, 'belief_adjustment': 0.0}
    for sides in ([], ['buy'], ['buy', 'sell', 'buy'], ['sell'] * 5):
        res = run_market_making_episode(100.0, sides, 100.0, cfg)
        assert len(res['history']) == len(sides)


def test_final_cash_inventory_match_last_history_entry():
    cfg = {'base_spread': 1.5, 'uncertainty': 0.3, 'skew_strength': 0.2, 'belief_adjustment': 0.1}
    sides = ['buy', 'sell', 'sell', 'buy', 'buy']
    res = run_market_making_episode(100.0, sides, 100.0, cfg)
    assert res['cash'] == res['history'][-1]['cash']
    assert res['inventory'] == res['history'][-1]['inventory']
    assert res['fair_value'] == res['history'][-1]['fair_value']


def test_unit_size_inventory_equals_sells_minus_buys():
    cfg = {'base_spread': 1.0, 'uncertainty': 0.0, 'skew_strength': 0.0, 'belief_adjustment': 0.0}
    sides = ['buy', 'sell', 'sell', 'buy', 'buy', 'sell']
    res = run_market_making_episode(100.0, sides, 100.0, cfg)
    n_buys = sides.count('buy')
    n_sells = sides.count('sell')
    assert res['inventory'] == n_sells - n_buys


def test_pnl_matches_mark_to_market_pnl():
    cfg = {'base_spread': 1.0, 'uncertainty': 0.5, 'skew_strength': 0.3, 'belief_adjustment': 0.2}
    sides = ['buy', 'buy', 'sell']
    true_value = 105.0
    res = run_market_making_episode(true_value, sides, 100.0, cfg)
    expected = mark_to_market_pnl(res['cash'], res['inventory'], true_value)
    assert res['pnl'] == expected


def test_empty_sides_gives_zero_pnl_and_empty_history():
    cfg = {'base_spread': 1.0, 'uncertainty': 0.0, 'skew_strength': 0.0, 'belief_adjustment': 0.0}
    res = run_market_making_episode(100.0, [], 100.0, cfg)
    assert res['pnl'] == 0.0
    assert res['history'] == []
    assert res['cash'] == 0.0
    assert res['inventory'] == 0.0
    assert res['fair_value'] == 100.0


def test_zero_uncertainty_skew_belief_equal_buys_sells_gives_zero_inventory():
    cfg = {'base_spread': 1.0, 'uncertainty': 0.0, 'skew_strength': 0.0, 'belief_adjustment': 0.0}
    sides = ['buy', 'sell', 'buy', 'sell', 'buy', 'sell']
    res = run_market_making_episode(100.0, sides, 100.0, cfg)
    assert res['inventory'] == 0.0


def test_missing_config_key_behaves_as_zero():
    sides = ['buy', 'sell']
    res_missing = run_market_making_episode(100.0, sides, 100.0, {})
    res_explicit_zero = run_market_making_episode(100.0, sides, 100.0, {
        'base_spread': 0.0, 'uncertainty': 0.0, 'skew_strength': 0.0, 'belief_adjustment': 0.0,
    })
    assert res_missing == res_explicit_zero


def test_reuses_helpers_quote_before_trade_skew_on_pretrade_inventory():
    # With skew_strength > 0, the first round must skew on starting inventory (0),
    # giving a symmetric quote regardless of which side trades first.
    cfg = {'base_spread': 2.0, 'uncertainty': 0.0, 'skew_strength': 1.0, 'belief_adjustment': 0.0}
    res = run_market_making_episode(100.0, ['buy'], 100.0, cfg)
    first = res['history'][0]
    assert first['bid'] == 99.0
    assert first['ask'] == 101.0
