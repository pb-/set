import time
from json import loads, dumps

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler

from . import game, messages


class Handler(WebSocketHandler):
    def handle_message(self, message):
        self.context['state'], commands = game.update(
            self.context['state'], time.time(),
            {**message, 'id': self.player_id})

        # self.handle_commands(commands)

    def handle_commands(self, commands):
        messages = []
        while messages or commands:
            pass #  TODO

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

        self.handle_message(decoded)

    def on_close(self):
        del self.context['clients'][self.player_id]
        self.handle_message(messages.player_left(self.player_id))


def run():
    context = {
        'state': game.initial_state(),
        'clients': {},
    }

    Application([
        (r'/', Handler, dict(context=context)),
    ]).listen(8000)

    IOLoop.current().start()
