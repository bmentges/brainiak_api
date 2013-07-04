# -*- coding: utf-8 -*-
import sys
import traceback

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application as TornadoApplication

from brainiak import log, settings
from brainiak.greenlet_tornado import greenlet_set_ioloop
from brainiak.handlers import get_routes
from brainiak import event_bus


server = None

define("debug", default=settings.DEBUG, help="Debug mode", type=bool)


class Application(TornadoApplication):

    def __init__(self, debug=False):
        try:
            log.initialize()
            event_bus.initialize()
            super(Application, self).__init__(get_routes(), debug=debug)
        except Exception as e:
            sys.stdout.write("Failed to initialize application. {0}".format(str(e)))
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)

application = Application()


def main():  # pragma: no cover
    define("port", default=settings.SERVER_PORT, help="Run app on the given port", type=int)
    parse_command_line()
    application = Application(debug=options.debug)
    server = HTTPServer(application)
    server.listen(options.port)
    io_loop = IOLoop.instance()
    greenlet_set_ioloop(io_loop)
    io_loop.start()


if __name__ == '__main__':
    main()
