# -*- coding: utf-8 -*-
from brainiak.handlers import SchemaHandler, VersionHandler, \
    HealthcheckHandler, VirtuosoStatusHandler, InstanceHandler

from tornado.web import URLSpec


def get_routes():
    return [
        URLSpec(r'/healthcheck', HealthcheckHandler),
        URLSpec(r'/version', VersionHandler),
        URLSpec(r'/status/virtuoso', VirtuosoStatusHandler),
        URLSpec(r'/(?P<context_name>.+)/(?P<class_name>.+)/_schema', SchemaHandler),
        URLSpec(r'/(?P<context_name>.+)/(?P<class_name>.+)/(?P<instance_id>.+)', InstanceHandler)
    ]
