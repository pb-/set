"""
Pure functions to create messages. Messages passed into the update() function,
some of these are also acceptable as client -> server messages (schema
validation available for those.)
"""
from jsonschema import validate, ValidationError

PLAYER_JOINED = 'player-joined'
PLAYER_LEFT = 'player-left'
GAME_STARTED = 'game-started'
CARDS_WANTED = 'cards-wanted'
PLAYERS_READY = 'players-ready'
SET_ANNOUNCED = 'set-announced'
CARD_DEALT = 'card-dealt'

CLIENT_MESSAGES = [PLAYER_JOINED, SET_ANNOUNCED, CARDS_WANTED]

BASE_SCHEMA = {
    'type': 'object',
    'properties': {
        'type': {
            'type': 'string',
            'enum': CLIENT_MESSAGES,
        },
    },
    'required': ['type'],
}

SCHEMA = {
    PLAYER_JOINED: {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'minLength': 1,
            },
        },
        'required': ['name'],
    },
    SET_ANNOUNCED: {
        'type': 'object',
        'properties': {
            'cards': {
                'type': 'array',
                'items': {
                    'type': 'number',
                },
                'minItems': 3,
                'maxItems': 3,
            },
        },
        'required': ['cards'],
    },
    CARDS_WANTED: {},
}


def player_joined(id_, name):
    return {
        'type': PLAYER_JOINED,
        'id': id_,
        'name': name,
    }


def player_left(id_):
    return {
        'type': PLAYER_LEFT,
        'id': id_,
    }


def players_ready(max_id):
    return {
        'type': PLAYERS_READY,
        'max_id': max_id,
    }


def game_started(seed):
    return {
        'type': GAME_STARTED,
        'seed': seed,
    }


def cards_wanted(player_id):
    return {
        'type': CARDS_WANTED,
        'id': player_id,
    }


def set_announced(player_id, cards):
    return {
        'type': SET_ANNOUNCED,
        'id': player_id,
        'cards': cards,
    }


def card_dealt(position):
    return {
        'type': CARD_DEALT,
        'position': position,
    }


def is_valid(message):
    try:
        validate(message, BASE_SCHEMA)
        validate(message, SCHEMA[message['type']])
        return True
    except ValidationError:
        return False
