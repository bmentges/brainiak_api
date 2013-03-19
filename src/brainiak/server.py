# -*- coding: utf-8 -*-
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application as TornadoApplication

from brainiak import __doc__, log, settings
from brainiak import urls
from brainiak.greenlet_tornado import greenlet_set_ioloop

server = None


class Application(TornadoApplication):

    def __init__(self, debug=False):
        log.initialize()
        super(Application, self).__init__(urls.get_routes(), debug=debug)

application = Application()


def main(args):  # pragma: no cover
    application = Application(debug=args.debug)
    server = HTTPServer(application)
    server.listen(settings.SERVER_PORT)
    io_loop = IOLoop.instance()
    greenlet_set_ioloop(io_loop)
    io_loop.start()


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--debug', action='store_const', const=True, default=settings.DEBUG, help='debug mode')
    args = parser.parse_args()

    main(args)
