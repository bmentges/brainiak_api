# -*- coding: utf-8 -*-
import logging
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application as TornadoApplication

from brainiak import settings
from brainiak.urls import resources


class Application(TornadoApplication):

    def __init__(self, debug=False):
        super(Application, self).__init__(resources, debug=debug)


def main(args):  # pragma: no cover
    application = Application(debug=args.debug)
    server = HTTPServer(application)
    server.listen(settings.SERVER_PORT)
    ioloop = IOLoop.instance().start()


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description=settings.DESCRIPTION)
    parser.add_argument('-d', '--debug', action='store_const', const=True, default=settings.DEBUG, help='debug mode')
    args = parser.parse_args()

    main(args)
