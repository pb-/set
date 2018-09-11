from random import Random
from itertools import chain, zip_longest, combinations

from . import messages, commands
from .card import is_set

START_DELAY_S = 3
RESTART_DELAY_S = 5
DEAL_DELAY_S = 2
DEAL_DELTA_S = DEAL_DELAY_S / 10


def initial_state():
    return {
        'players': [],
        'game': None
    }


def update(state, time, message):
    # TODO messages: card dealt
    if message['type'] == messages.PLAYER_JOINED:
        s = {
            **state,
            'players': [*state['players'], make_player(
                message['id'], message['name'], time)]
        }

        if not s['game'] and len(s['players']) > 1:
            id_ = max_id(s['players'])
            return s, [
                commands.delay(START_DELAY_S, messages.players_ready(id_))]

        return s, [commands.broadcast(filter_state(s))]
    elif message['type'] == messages.PLAYER_LEFT:
        players = [p for p in state['players'] if p['id'] != message['id']]

        s = {
            **state,
            'players': players,
            'game': state['game'] if players else None,
        }
        return s, [commands.broadcast(filter_state(s))]
    elif message['type'] == messages.PLAYERS_READY:
        id_ = max_id(state['players'])
        if len(state['players']) < 2 or id_ > message['max_id']:
            return state, []
        return state, [commands.generate_random(messages.game_started)]
    elif message['type'] == messages.GAME_STARTED:
        s = {
            **state,
            'players': [{**p, 'points': 0} for p in state['players']],
            'game': refill_board(make_game(message['seed'], time)),
        }
        return s, [commands.broadcast(filter_state(s))]
    elif message['type'] == messages.CARDS_WANTED:
        if not state['game'] or state['game']['future_cards']:
            return state, []

        s = {
            **state,
            'players': [{
                **p, 'wants_cards': True
                } if p['id'] == message['player_id'] else p
                for p in state['players']],
        }

        if not all(p['wants_cards'] for p in s['players']):
            return s, []

        st = {
            **s,
            'players': [{**p, 'wants_cards': False} for p in s['players']],
        }

        # TODO continue
        return st, []
    elif message['type'] == messages.SET_ANNOUNCED:
        if not state['game'] or state['game']['game_over']:
            return state, []

        is_correct = is_board_set(state['game']['board'], message['cards'])
        positions = tuple(
            find_card(state['game']['board'], c) for c in message['cards'])

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

        num_cards = len(list(chain(*s['game']['board'])))
        deals = [
            commands.delay(
                DEAL_DELAY_S + i * DEAL_DELTA_S, messages.card_dealt(position))
            for i, position in enumerate(positions)
        ] if is_correct and num_cards <= 12 and s['game']['deck'] else []

        c = [*deals, commands.broadcast(filter_state(s))]

        if not s['game']['deck'] and not find_set(s['game']['board']):
            id_ = max_id(['players'])
            return {
                **s, 'game': {
                    **s['game'],
                    'game_over': True,
                    'future_cards': s['game']['future_cards'] + 3
                }}, [
                *c, commands.delay(
                    RESTART_DELAY_S, messages.players_ready(id_))]

        return s, c

    return state, []


def find_card(board, card):
    return next((
        (col, row)
        for col in range(len(board))
        for row in range(len(board[col]))
        if board[col][row] == card
    ), None)


def points(is_correct):
    return 1 if is_correct else -1


def max_id(players):
    return max(p['id'] for p in players)


def filter_state(state):
    """Filter game state for clients (remove secrets and useless data)."""
    # TODO implement. also: add message type
    return state


def make_player(id_, name, joined_at):
    return {
        'id': id_,
        'name': name,
        'points': 0,
        'wants_cards': False,
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
        'future_cards': 0,
        'game_over': False,
        'started_at': time,
    }


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
