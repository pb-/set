"""
Entry point of the app. Contains impure functions and lots of side effects.
"""
import logging
import time
import random
from json import loads, dumps, JSONDecodeError
from functools import wraps
from argparse import ArgumentParser

from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from tornado.websocket import WebSocketHandler

from . import game, messages, commands


def with_log(update):
    @wraps(update)
    def wrapped_update(state_before, time, message):
        state_after, cmds = update(state_before, time, message)
        logging.debug(
            'update before=%s time=%f message=%s -> after=%s commands=%s',
            state_before, time, message, state_after, cmds)
        return state_after, cmds

    return wrapped_update


game.update = with_log(game.update)


class Handler(WebSocketHandler):
    def handle_player_message(self, message):
        self.handle_message({**message, 'id': self.player_id})

    def handle_message(self, message):
        self.context['state'], cmds = game.update(
            self.context['state'], time.time(), message)

        self.handle_commands(cmds)

    def handle_commands(self, cmds):
        for cmd in cmds:
            if cmd['type'] == commands.GENERATE_RANDOM:
                self.handle_message(
                    cmd['message_func'](random.randint(0, 2**64 - 1)))
            elif cmd['type'] == commands.DELAY:
                IOLoop.current().call_later(
                    cmd['seconds'], self.handle_message, cmd['message'])
            elif cmd['type'] == commands.BROADCAST:
                for client in self.context['clients'].values():
                    client.write_message(dumps(cmd['data']))

    def initialize(self, context):
        self.context = context
        self.player_id = 1 + self.context['last_id']

        self.context['last_id'] = self.player_id
        self.context['clients'][self.player_id] = self

    def on_message(self, message):
        try:
            decoded = loads(message)
        except JSONDecodeError:
            logging.debug('bad message encoding: `%s`', message)
            return

        if not messages.is_valid(decoded):
            logging.debug('bad message: `%s`', message)
            return

        self.handle_player_message(decoded)

    def on_close(self):
        del self.context['clients'][self.player_id]
        self.handle_player_message(messages.player_left(self.player_id))

    def check_origin(self, _):
        return True


def run():
    logging.basicConfig(level=logging.DEBUG)
    context = {
        'last_id': 0,
        'state': game.initial_state(),
        'clients': {},
    }

    parser = ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=8000)
    parser.add_argument('--root', '-r', default='../frontend/public')
    args = parser.parse_args()

    Application([
        (r'/socket', Handler, dict(context=context)),
        (r'/(.*)', StaticFileHandler, {
            'path': args.root,
            'default_filename': 'index.html'}),
    ], compress_response=True).listen(args.port)

    IOLoop.current().start()
