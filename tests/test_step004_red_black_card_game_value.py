from scaffold import red_black_card_game_value


def test_examples():
    result = red_black_card_game_value(1, 1)
    assert abs(result['value'] - 0.5) < 1e-9
    assert result['stop_now'] is False

    result = red_black_card_game_value(0, 3)
    assert result['value'] == 0.0
    assert result['stop_now'] is True


def test_value_non_negative():
    for r in range(0, 7):
        for b in range(0, 7):
            result = red_black_card_game_value(r, b)
            assert result['value'] >= 0.0


def test_all_red_boundary():
    for r in range(1, 7):
        result = red_black_card_game_value(r, 0)
        assert result['value'] == float(r)
        assert result['stop_now'] is False


def test_all_black_boundary():
    for b in range(0, 7):
        result = red_black_card_game_value(0, b)
        assert result['value'] == 0.0
        assert result['stop_now'] is True


def test_value_bounded_by_num_red():
    for r in range(0, 7):
        for b in range(0, 7):
            result = red_black_card_game_value(r, b)
            assert result['value'] <= r + 1e-9


def test_value_non_decreasing_in_num_red():
    for b in range(0, 6):
        values = [red_black_card_game_value(r, b)['value'] for r in range(0, 7)]
        for a, c in zip(values, values[1:]):
            assert c >= a - 1e-9


def test_value_non_increasing_in_num_black():
    for r in range(0, 6):
        values = [red_black_card_game_value(r, b)['value'] for b in range(0, 7)]
        for a, c in zip(values, values[1:]):
            assert c <= a + 1e-9


def test_stop_now_consistency():
    for r in range(0, 7):
        for b in range(0, 7):
            result = red_black_card_game_value(r, b)
            if result['value'] <= 0.0:
                assert result['stop_now'] is True
            else:
                assert result['stop_now'] is False
