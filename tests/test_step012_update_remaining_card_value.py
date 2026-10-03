from scaffold import update_remaining_card_value


def test_example():
    res = update_remaining_card_value({1.0: 2, -1.0: 2}, 1.0)
    assert res['remaining_counts'] == {1.0: 1, -1.0: 2}
    assert round(res['expected_value'], 4) == -0.3333


def test_total_count_falls_by_exactly_one():
    decks = [{1.0: 2, -1.0: 2}, {5.0: 1, 3.0: 4, -2.0: 3}, {0.0: 1}]
    for deck in decks:
        for revealed_value in deck:
            before = sum(deck.values())
            res = update_remaining_card_value(deck, revealed_value)
            after = sum(res['remaining_counts'].values())
            assert before - after == 1


def test_input_dict_not_mutated():
    original = {1.0: 2, -1.0: 2}
    snapshot = dict(original)
    update_remaining_card_value(original, 1.0)
    assert original == snapshot


def test_no_zero_count_keys_remain():
    deck = {1.0: 1, -1.0: 2}
    res = update_remaining_card_value(deck, 1.0)
    assert 1.0 not in res['remaining_counts']
    for count in res['remaining_counts'].values():
        assert count > 0


def test_expected_value_within_min_max_of_remaining_keys():
    decks = [{1.0: 2, -1.0: 2}, {5.0: 1, 3.0: 4, -2.0: 3}]
    for deck in decks:
        for revealed_value in list(deck):
            res = update_remaining_card_value(deck, revealed_value)
            if res['remaining_counts']:
                keys = res['remaining_counts'].keys()
                assert min(keys) <= res['expected_value'] <= max(keys)
            else:
                assert res['expected_value'] == 0.0


def test_revealing_every_card_in_turn_ends_empty_and_zero():
    deck = {1.0: 1, -1.0: 1}
    res = update_remaining_card_value(deck, 1.0)
    res = update_remaining_card_value(res['remaining_counts'], -1.0)
    assert res['remaining_counts'] == {}
    assert res['expected_value'] == 0.0


def test_return_type_is_float_for_expected_value():
    res = update_remaining_card_value({1.0: 2, -1.0: 2}, 1.0)
    assert isinstance(res['expected_value'], float)
