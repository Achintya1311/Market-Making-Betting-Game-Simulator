from scaffold import pay_per_reroll_die_game


def brute_force(sides, reroll_cost):
    n = sides
    best_t, best_v = 1, None
    for t in range(1, n + 1):
        v = (t + n) / 2.0 - ((t - 1) / (n - t + 1)) * reroll_cost
        if best_v is None or v > best_v:
            best_v = v
            best_t = t
    return best_t, best_v


def test_examples():
    assert pay_per_reroll_die_game(6, 1.0) == {'threshold': 3, 'value': 4.0}
    assert pay_per_reroll_die_game(6, 0.0) == {'threshold': 6, 'value': 6.0}


def test_zero_cost_gives_threshold_equals_sides():
    for n in range(1, 11):
        result = pay_per_reroll_die_game(n, 0.0)
        assert result['threshold'] == n
        assert result['value'] == float(n)


def test_threshold_in_range():
    for n in range(1, 11):
        for cost in [0.0, 0.5, 1.0, 2.0, 5.0]:
            result = pay_per_reroll_die_game(n, cost)
            assert 1 <= result['threshold'] <= n


def test_value_non_increasing_in_cost():
    for n in range(1, 11):
        costs = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 10.0]
        values = [pay_per_reroll_die_game(n, c)['value'] for c in costs]
        for a, b in zip(values, values[1:]):
            assert b <= a + 1e-9


def test_value_at_least_baseline():
    for n in range(1, 11):
        for cost in [0.0, 0.5, 1.0, 2.0, 5.0]:
            result = pay_per_reroll_die_game(n, cost)
            assert result['value'] >= (n + 1) / 2.0 - 1e-9


def test_matches_brute_force_smallest_tie():
    for n in range(1, 11):
        for cost in [0.0, 0.3, 1.0, 2.0, 3.0]:
            result = pay_per_reroll_die_game(n, cost)
            bt, bv = brute_force(n, cost)
            assert result['threshold'] == bt
            assert abs(result['value'] - bv) < 1e-9


def test_return_types():
    result = pay_per_reroll_die_game(6, 1.0)
    assert isinstance(result['threshold'], int)
    assert isinstance(result['value'], float)
