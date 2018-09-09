PLAYER_JOINED = 'player-joined'
GAME_STARTED = 'game-started'
PLAYERS_READY = 'players-read'


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
