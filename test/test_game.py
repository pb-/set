from itertools import chain

from ..game import compress_board, refill_board, make_game


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
