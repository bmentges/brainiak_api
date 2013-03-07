# -*- coding: utf-8 -*-
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application as TornadoApplication

from brainiak import __doc__, log, settings
from brainiak import urls

server = None


class Application(TornadoApplication):

    def __init__(self, debug=False):
        super(Application, self).__init__(urls.get_routes(), debug=debug)

application = Application()


def main(args):  # pragma: no cover
    log.initialize()
    application = Application(debug=args.debug)
    server = HTTPServer(application)
    server.listen(settings.SERVER_PORT)
    IOLoop.instance().start()


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--debug', action='store_const', const=True, default=settings.DEBUG, help='debug mode')
    args = parser.parse_args()

    main(args)
