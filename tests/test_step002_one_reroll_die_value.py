from scaffold import one_reroll_die_value


def test_examples():
    assert one_reroll_die_value(2) == {'value': 1.75, 'reroll_faces': [1]}
    assert one_reroll_die_value(6) == {'value': 4.25, 'reroll_faces': [1, 2, 3]}


def test_value_bounds():
    for n in range(1, 21):
        mu = (n + 1) / 2
        result = one_reroll_die_value(n)
        assert mu - 1e-9 <= result['value'] <= n + 1e-9


def test_every_reroll_face_below_mu():
    for n in range(1, 21):
        mu = (n + 1) / 2
        result = one_reroll_die_value(n)
        for f in result['reroll_faces']:
            assert f < mu


def test_reroll_faces_sorted_and_python_int():
    for n in range(1, 21):
        result = one_reroll_die_value(n)
        faces = result['reroll_faces']
        assert faces == sorted(faces)
        for f in faces:
            assert isinstance(f, int)


def test_sides_one_edge_case():
    result = one_reroll_die_value(1)
    assert result == {'value': 1.0, 'reroll_faces': []}


def test_matches_brute_force():
    for n in range(1, 21):
        mu = (n + 1) / 2
        expected_payouts = [max(f, mu) for f in range(1, n + 1)]
        brute_value = sum(expected_payouts) / n
        brute_reroll = sorted(f for f in range(1, n + 1) if f < mu)
        result = one_reroll_die_value(n)
        assert abs(result['value'] - brute_value) < 1e-9
        assert result['reroll_faces'] == brute_reroll
