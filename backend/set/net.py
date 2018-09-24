"""
Pure functions to create Server -> client messages.
"""

STATE = 'state'
CARDS_DENIED = 'cards-denied'


def state(state):
    """
    state returns a trimmed down version of the game state.
    """
    return {
        'type': STATE,
        'players': [{
            'name': p['name'],
            'points': p['points'],
            'wants_cards': p['wants_cards'],
            } for p in state['players']
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
