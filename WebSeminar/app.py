#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import uuid

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler
import django.core.handlers.wsgi
import tornado.wsgi
import tornado.httpserver
from tornado.options import options, define, parse_command_line
import django
from VideoChat.wsgi import application as vc_wsgi_app


os.environ['DJANGO_SETTINGS_MODULE'] = 'VideoChat.settings'
django.setup()

rel = lambda *x: os.path.abspath(os.path.join(os.path.dirname(__file__), *x))

global_rooms = {}


class Room(object):
    def __init__(self, name, clients=[]):
        self.name = name
        self.clients = clients

    def __repr__(self):
        return self.name


class MainHandler(RequestHandler):
    def get(self):
        room = str(uuid.uuid4().hex.upper()[0:6])
        self. redirect('/room/'+room)


class RoomHandler(RequestHandler):
    def get(self, slug):
        self.render('room.html')


class EchoWebSocket(WebSocketHandler):
    def open(self, slug):
        if slug in global_rooms:
            global_rooms[slug].clients.append(self)
        else:
            global_rooms[slug] = Room(slug, [self])
        self.room = global_rooms[slug]
        if len(self.room.clients) > 2:
            self.write_message('fullhouse')
        elif len(self.room.clients) == 1:
            self.write_message('initiator')
        else:
            self.write_message('not initiator')
        logging.info(
            'WebSocket connection opened from %s', self.request.remote_ip)

    def on_message(self, message):
        logging.info(
            'Received message from %s: %s', self.request.remote_ip, message)
        for client in self.room.clients:
            if client is self:
                continue
            client.write_message(message)

    def on_close(self):
        logging.info('WebSocket connection closed.')
        self.room.clients.remove(self)


def main():
    wsgi_app = tornado.wsgi.WSGIContainer(
   vc_wsgi_app)

    settings = dict(
        template_path=rel('templates/chat'),
        static_path=rel('static'),
        debug=True
    )

    application = Application([
         (r'/', MainHandler),
        (r"/room/([^/]*)", RoomHandler),
        (r'/ws/([^/]*)', EchoWebSocket),
        ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
    ], **settings)

    server = tornado.httpserver.HTTPServer(application)
    application.listen(address='127.0.0.1', port=8080)
    logging.info("Started listening at 127.0.0.1:8080.")
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
