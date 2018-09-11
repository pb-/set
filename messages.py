PLAYER_JOINED = 'player-joined'
PLAYER_LEFT = 'player-left'
GAME_STARTED = 'game-started'
CARDS_WANTED = 'cards-wanted'
PLAYERS_READY = 'players-read'
SET_ANNOUNCED = 'set-announced'
CARD_DEALT = 'card-dealt'


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
