# -*- coding: utf-8 -*-
import sys
import traceback

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application as TornadoApplication

from brainiak import log, settings
from brainiak.greenlet_tornado import greenlet_set_ioloop
from brainiak import event_bus
from brainiak.utils.cache import flushall

# Annotation API
from brainiak.handlers import *
from tornado.web import URLSpec


server = None

define("debug", default=settings.DEBUG, help="Debug mode", type=bool)


class Application(TornadoApplication):

    def __init__(self, debug=False):
        try:
            log.initialize()
            event_bus.initialize()
            # Wipeout all entries to avoid inconsistencies due to algorithmic changes between releases
            flushall()
            super(Application, self).__init__(get_routes(), debug=debug)
        except Exception as e:
            sys.stdout.write(u"Failed to initialize application. {0}".format(unicode(e)))
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)

application = Application()


def get_routes():
    return [
        # INTERNAL resources for monitoring and meta-infromation inspection
        URLSpec(r'/healthcheck/?', HealthcheckHandler),
        URLSpec(r'/_version/?', VersionHandler),
        URLSpec(r'/_prefixes/?', PrefixHandler),
        URLSpec(r'/_status/?$', StatusHandler),
        URLSpec(r'/_status/activemq/?', EventBusStatusHandler),
        URLSpec(r'/_status/cache/?', CacheStatusHandler),
        URLSpec(r'/_status/virtuoso/?', VirtuosoStatusHandler),

        URLSpec(r'/_schema_list/?', RootJsonSchemaHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_search/_schema_list/?', SearchJsonSchemaHandler),
        URLSpec(r'/_suggest/_schema_list/?', SuggestJsonSchemaHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/_schema_list/?', ContextJsonSchemaHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema_list/?', CollectionJsonSchemaHandler),

        # TEXTUAL search
        URLSpec(r'/_suggest/?', SuggestHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_search/?', SearchHandler),

        # Annotation API
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_annotation/?', AnnotationHandler),

        # resources that represents CONCEPTS
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema/?', ClassHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/?', CollectionHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/(?P<instance_id>[\w\-]+)/?', InstanceHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/?', ContextHandler),
        URLSpec(r'/$', RootHandler),
        URLSpec(r'/.*$', UnmatchedHandler),
    ]


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
