from random import Random
from itertools import chain, zip_longest

from . import messages, commands


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

    return state, []


def filter_state(state):
    """Filter game state for clients (remove secrets and useless data)."""
    return state


def make_player(id_, name, joined_at):
    return {
        'id': id_,
        'name': name,
        'joined_at': joined_at,
    }


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
