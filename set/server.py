import time
import random
from json import loads, dumps

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler

from . import game, messages, commands


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
        self.player_id = 1 + (
            max(context['clients'].keys()) if context['clients'] else 0)

        self.context['clients'][self.player_id] = self

    def on_message(self, message):
        decoded = loads(message)

        # TODO verify all the fields
        if decoded.get('type', None) not in messages.CLIENT_MESSAGES:
            return

        self.handle_player_message(decoded)

    def on_close(self):
        del self.context['clients'][self.player_id]
        self.handle_player_message(messages.player_left(self.player_id))


def run():
    context = {
        'state': game.initial_state(),
        'clients': {},
    }

    Application([
        (r'/', Handler, dict(context=context)),
    ]).listen(8000)

    IOLoop.current().start()
