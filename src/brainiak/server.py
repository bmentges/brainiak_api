# -*- coding: utf-8 -*-

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application as TornadoApplication

import settings
from .resources import SchemaResource


class Application(TornadoApplication):

    def __init__(self, debug=False):
        resources = [(r'/contexts/(?P<context_name>.+)/(?P<collection_name>.+)', SchemaResource)]
        super(Application, self).__init__(resources, debug=debug)


def main(args):
    application = Application(debug=args.debug)
    server = HTTPServer(application)
    server.listen(settings.SERVER_PORT)
    IOLoop.instance().start()


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description=settings.DESCRIPTION)
    parser.add_argument('-d', '--debug', action='store_const', const=True, default=False, help='debug mode')
    args = parser.parse_args()
    main(args)
