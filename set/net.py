"""
Server -> client messages.
"""

STATE = 'state'
CARDS_DENIED = 'cards-denied'


def state(state):
    return {
        'type': STATE,
        'players': [
            {'name': p['name'], 'points': p['points']}
            for p in state['players']
        ],
        'game': {
            'board': state['game']['board'],
            'game_over': state['game']['game_over'],
        } if state['game'] else None,
    }


def cards_denied():
    return {
        'type': CARDS_DENIED,
    }
