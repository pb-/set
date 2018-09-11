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


def empty_slots(board):
    return sum(1 for c in chain(*board) if c == -1)


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
