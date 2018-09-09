PLAYER_JOINED = 'player-joined'
GAME_STARTED = 'game-started'
PLAYERS_READY = 'players-read'
SET_ANNOUNCED = 'set-announced'
CARDS_DEALT = 'cards-dealt'


def player_joined(id_, name):
    return {
        'type': PLAYER_JOINED,
        'id': id_,
        'name': name,
    }


def players_ready():
    return {
        'type': PLAYERS_READY,
    }


def game_started(seed):
    return {
        'type': GAME_STARTED,
        'seed': seed,
    }


def set_announced(player_id, cards):
    return {
        'type': SET_ANNOUNCED,
        'id': player_id,
        'cards': cards,
    }


def cards_dealt(positions):
    return {
        'type': CARDS_DEALT,
        'positions': positions,
    }
