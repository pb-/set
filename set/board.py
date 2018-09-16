"""
Pure functions to manipulate the board of communal cards.
"""
from itertools import chain, zip_longest


def make(cards):
    return tuple(grouper(cards, 3, -1))


def position(board, card):
    return next((
        (col, row)
        for col in range(len(board))
        for row in range(len(board[col]))
        if board[col][row] == card
    ), None)


def without(board, cards):
    return tuple(
        tuple(-1 if c in cards else c for c in col) for col in board)


def cards(board):
    return (c for c in chain(*board) if c != -1)


def size(board):
    return sum(1 for _ in chain(*board))


def is_full(board):
    return -1 not in chain(*board)


def expand(board):
    return (*board, (-1, ) * 3)


def free_positions(board):
    return tuple(
        (col, row)
        for col in range(len(board))
        for row in range(len(board[col]))
        if board[col][row] == -1
    )


def put(board, position, card):
    return tuple(
        tuple(
            card if (col, row) == position else board[col][row]
            for row in range(len(board[col])))
        for col in range(len(board))
    )


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
