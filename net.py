"""
Server -> client messages.
"""

STATE = 'state'
CARDS_DENIED = 'cards-denied'


def state(state):
    # TODO filter secrets and unneeded data
    return {
        **state,
        'type': STATE,
    }


def cards_denied():
    return {
        'type': CARDS_DENIED,
    }
