"""
Pure functions to manage cards and collections of cards.
"""
from functools import reduce
from operator import add


def encode(parts):
    return reduce(add, (v * 3 ** i for i, v in enumerate(parts)))


def decode(comp):
    return [comp // 3 ** i % 3 for i in range(4)]


def is_set(cards):
    if len(set(cards)) != 3:
        return False

    if not all(0 <= c <= 80 for c in cards):
        return False

    return 2 not in map(len, map(set, zip(*map(decode, cards))))
