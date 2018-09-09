from itertools import chain

from .. import messages, commands
from ..game import (
    compress_board, refill_board, make_game, initial_state, update)


def test_compress_board():
    assert compress_board([]) == ((-1, ) * 3, ) * 4
    assert compress_board((
        (1, -1, 2),
        (3, -1, -1),
        (-1, 6, 9),
        (-1, -1, 8))
    ) == (
        (1, 2, 3),
        (6, 9, 8),
        (-1, ) * 3,
        (-1, ) * 3,
    )
    assert compress_board(((1, -1, -1), ) * 5) == (
        (1, ) * 3,
        (1, 1, -1),
        (-1, ) * 3,
        (-1, ) * 3,
    )


def test_refill_board():
    assert -1 not in chain(*refill_board(make_game(0, 0)))
    assert refill_board({  # no exception (empty deck)
        **make_game(0, 0),
        'deck': [],
    })


def test_update():
    s = initial_state()
    s, c = update(s, 0, messages.player_joined(1, 'alice'))
    assert s['players'][0]['name'] == 'alice'
    assert not s['game']
    assert not c

    s, c = update(s, 0, messages.player_joined(1, 'bob'))
    assert len(s['players']) == 2
    assert c[0]['type'] == commands.DELAY

    s, c = update(s, 0, c[0]['message'])
    assert c[0]['type'] == commands.GENERATE_RANDOM

    s, c = update(s, 0, c[0]['message_func'](0))
    assert s['game']
    assert -1 not in chain(*s['game']['board'])
    assert c[0]['type'] == commands.BROADCAST
