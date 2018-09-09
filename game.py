from random import Random
from itertools import chain, zip_longest


def initial_state():
    return {
        'players': [],
        'game': None
    }


def update(state, time, message):
    return state, []


def make_deck(seed):
    return Random(seed).sample(list(range(80)), 80)


def refill_board(game):
    deck = iter(game['deck'])
    return {
        **game,
        'board': tuple(
            tuple(card if card != -1 else next(deck, -1) for card in col)
            for col in game['board']
        ),
        'deck': list(deck),
    }


def compress_board(board):
    return tuple(grouper((
        c for c, _ in (zip_longest(
            (c for c in chain(*board) if c != -1),
            range(12),
            fillvalue=-1))), 3, fillvalue=-1))


def make_game(seed, time):
    return {
        'deck': make_deck(seed),
        'board': ((-1, ) * 3, ) * 4,
        'started_at': time,
    }


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
