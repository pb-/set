from random import Random
from itertools import chain, zip_longest, combinations

from . import messages, commands
from .card import is_set


def initial_state():
    return {
        'players': [],
        'game': None
    }


def update(state, time, message):
    if message['type'] == messages.PLAYER_JOINED:
        s = {
            **state,
            'players': [*state['players'], make_player(
                message['id'], message['name'], time)]
        }

        if not s['game'] and len(s['players']) > 1:
            return s, [commands.delay(3, messages.players_ready())]

        return s, []
    elif message['type'] == messages.PLAYERS_READY:
        return state, [commands.generate_random(messages.game_started)]
    elif message['type'] == messages.GAME_STARTED:
        s = {
            **state,
            'game': refill_board(make_game(message['seed'], time)),
        }
        return s, [commands.broadcast(filter_state(s))]
    elif message['type'] == messages.SET_ANNOUNCED:
        if not state['game']:
            return state, []

        is_correct = is_board_set(state['game']['board'], message['cards'])
        s = {
            **state,
            'players': [
                {
                    **p,
                    'points': max(0, p['points'] + points(is_correct))
                } if p['id'] == message['id'] else p
                for p in state['players']
            ],
            'game': {
                **state['game'],
                'board': tuple(
                    tuple(c if c not in message['cards'] else -1 for c in col)
                    for col in state['game']['board']
                ),
            } if is_correct else state['game']
        }

        return s, []  # TODO commands

    return state, []


def points(is_correct):
    return 1 if is_correct else -1


def filter_state(state):
    """Filter game state for clients (remove secrets and useless data)."""
    return state


def make_player(id_, name, joined_at):
    return {
        'id': id_,
        'name': name,
        'points': 0,
        'joined_at': joined_at,
    }


def is_board_set(board, cards):
    return is_set(cards) and all(c in chain(*board) for c in cards)


def find_set(board):
    return next((
        s for s in combinations((c for c in chain(*board) if c != -1), 3)
        if is_set(s)), None)


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


def make_deck(seed):
    return Random(seed).sample(list(range(80)), 80)


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
