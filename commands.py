DELAY = 'delay'
GENERATE_RANDOM = 'generate_random'
BROADCAST = 'broadcast'


def delay(seconds, message):
    return {
        'type': DELAY,
        'seconds': seconds,
        'message': message,
    }


def generate_random(message_func):
    return {
        'type': GENERATE_RANDOM,
        'message_func': message_func,
    }


def broadcast(data):
    return {
        'type': BROADCAST,
        'data': data,
    }
