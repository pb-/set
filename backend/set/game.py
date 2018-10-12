"""
Pure functions to manipulate the game's state. Contains the meat of the app,
all game logic is contained in update().
"""
from random import Random
from itertools import combinations

from . import messages, commands, board, net
from .card import is_set
from .func import valuedispatch

START_DELAY_S = 3
RESTART_DELAY_S = 5
DEAL_DELAY_S = 2
DEAL_DELTA_S = DEAL_DELAY_S / 10


def initial_state():
    return {
        'players': [],
        'game': None
    }


@valuedispatch(lambda args, _: args[2].get('type'))
def update(state, time, message):
    return state, []


@update.register(messages.PLAYER_JOINED)  # NOQA: F811
def _(state, time, message):
    if next((p for p in state['players'] if p['id'] == message['id']),
            None):
        return state, []

    return schedule_ready({
        **state,
        'players': [*state['players'], make_player(
            message['id'], message['name'], time)]
    })


def schedule_ready(state):
    if not state['game'] and len(state['players']) > 1:
        id_ = max_id(state['players'])
        return broadcast(state, [
            commands.delay(START_DELAY_S, messages.players_ready(id_))])

    return broadcast(state)


@update.register(messages.PLAYER_LEFT)  # NOQA: F811
def _(state, time, message):
    players = [p for p in state['players'] if p['id'] != message['id']]

    return broadcast({
        **state,
        'players': players,
        'game': state['game'] if players else None,
    })


@update.register(messages.PLAYERS_READY)  # NOQA: F811
def _(state, time, message):
    id_ = max_id(state['players'])
    if len(state['players']) < 2 or id_ > message['max_id']:
        return state, []
    return state, [commands.generate_random(messages.game_started)]


@update.register(messages.GAME_STARTED)  # NOQA: F811
def _(state, time, message):
    return broadcast({
        **state,
        'players': [{
            **p,
            'points': 0,
            'wants_cards': False} for p in state['players']],
        'game': make_game(message['seed'], time),
    })


@update.register(messages.GAME_ENDED)  # NOQA: F811
def _(state, time, message):
    return schedule_ready({**state, 'game': None})


@update.register(messages.CARD_DEALT)  # NOQA: F811
def _(state, time, message):
    s = {
        **state,
        'game': {
            **state['game'],
            'deck': state['game']['deck'][1:],
            'board': board.put(
                state['game']['board'],
                message['position'],
                state['game']['deck'][0]),
            'future_cards': state['game']['future_cards'] - 1,
        }
    }

    if game_is_over(s):
        return end_game(s)

    return broadcast(s)


@update.register(messages.CARDS_WANTED)  # NOQA: F811
def _(state, time, message):
    if not state['game'] or state['game']['future_cards'] or \
            not state['game']['deck']:
        return state, []

    players = [
        {**p, 'wants_cards': True} if p['id'] == message['id'] else p
        for p in state['players']]

    if not all(p['wants_cards'] for p in players):
        return broadcast({**state, 'players': players})

    players_reset = reset_card_requests(players)

    if find_set(state['game']['board']):
        return broadcast(
            {**state, 'players': players_reset},
            [commands.broadcast(net.cards_denied())])

    b = state['game']['board']
    new_board = board.expand(b) if board.is_full(b) else b
    free = board.free_positions(new_board)[:3]
    deals = [
        commands.delay(
            DEAL_DELAY_S + i * DEAL_DELTA_S, messages.card_dealt(position))
        for i, position in enumerate(free)
    ]

    return broadcast({
        **state,
        'players': players_reset,
        'game': {
            **state['game'],
            'board': new_board,
            'future_cards': state['game']['future_cards'] + 3,
        },
    }, deals)


def reset_card_requests(players):
    return [{**p, 'wants_cards': False} for p in players]


@update.register(messages.SET_ANNOUNCED)  # NOQA: F811
def _(state, time, message):
    if not state['game'] or state['game']['game_over']:
        return state, []

    is_correct = is_board_set(state['game']['board'], message['cards'])
    positions = tuple(
        board.position(state['game']['board'], c) for c in message['cards'])

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
            'board': board.without(state['game']['board'], message['cards']),
        } if is_correct else state['game']
    }

    conf = [commands.broadcast(net.set_confirmed(
        message['cards'], next((
            p['name'] for p in s['players'] if p['id'] == message['id']), '?')
    ))] if is_correct else []

    if game_is_over(s):
        return end_game(s, conf)

    num_cards = len(list(board.cards(s['game']['board'])))
    deals = [
        commands.delay(
            DEAL_DELAY_S + i * DEAL_DELTA_S, messages.card_dealt(position))
        for i, position in enumerate(positions)
    ] if is_correct and num_cards < 12 and s['game']['deck'] else []

    return broadcast({
        **s,
        'game': {
            **s['game'],
            'future_cards': s['game']['future_cards'] + (3 if deals else 0),
        },
    }, deals + conf)


def broadcast(state, cmds=[]):
    return state, [*cmds, commands.broadcast(net.state(state))]


def game_is_over(state):
    return not state['game']['deck'] and not find_set(state['game']['board'])


def end_game(state, cmds=[]):
    return broadcast({
        **state, 'game': {
            **state['game'],
            'game_over': True,
        }
    }, [commands.delay(RESTART_DELAY_S, messages.game_ended()), *cmds])


def points(is_correct):
    return 1 if is_correct else -1


def max_id(players):
    return max(p['id'] for p in players)


def make_player(id_, name, joined_at):
    return {
        'id': id_,
        'name': name,
        'points': 0,
        'wants_cards': False,
        'joined_at': joined_at,
    }


def find_set(board_):
    return next((
        s for s in combinations(board.cards(board_), 3) if is_set(s)), None)


def is_board_set(board_, cards):
    return is_set(cards) and all(c in board.cards(board_) for c in cards)


def make_deck(seed):
    return Random(seed).sample(list(range(81)), 81)


def make_game(seed, time):
    deck = make_deck(seed)
    return {
        'deck': deck[12:],
        'board': board.make(deck[:12]),
        'future_cards': 0,
        'game_over': False,
        'started_at': time,
    }
