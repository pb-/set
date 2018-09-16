from .. import messages as m


def test_creators():
    assert m.is_valid(m.player_joined(1, 'foo'))
    assert not m.is_valid(m.player_joined(1, ''))

    assert m.is_valid(m.cards_wanted(1))

    assert m.is_valid(m.set_announced(1, [0, 1, 2]))
    assert not m.is_valid(m.set_announced(1, [1, 2]))
