# -*- coding: utf-8 -*-

from tornado import gen
from tornado.web import asynchronous, HTTPError, RequestHandler

from brainiak import settings, triplestore
from brainiak import __version__
from brainiak.greenlet_tornado import greenlet_asynchronous
from brainiak.schema.resource import get_schema
from brainiak.instance.resource import filter_instances, get_instance


class HealthcheckHandler(RequestHandler):

    def get(self):
        self.write("WORKING")


class VersionHandler(RequestHandler):

    def get(self):
        self.write(__version__)


class VirtuosoStatusHandler(RequestHandler):

    def get(self):
        if settings.ENVIRONMENT == 'prod':
            raise HTTPError(404)

        self.write(triplestore.status())


class SchemaHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(SchemaHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        response = get_schema(context_name, class_name)
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            self.set_status(404)
        else:
            self.write(response)
        # self.finish() -- this is automagically called by greenlet_asynchronous


class InstanceHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(InstanceHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name, instance_id):
        response = get_instance(context_name, class_name, instance_id)
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            self.set_status(404)
        else:
            # TODO JSON parsing to JSON Schema format
            self.write(response)


class InstanceFilterHandler(RequestHandler):

    DEFAULT_PER_PAGE = "10"
    DEFAULT_PAGE = "0"

    def __init__(self, *args, **kwargs):
        super(InstanceFilterHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        query_params = {
            "class_uri": "{0}{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            # "graph_uri": TODO
            "page": self.DEFAULT_PAGE,
            "per_page": self.DEFAULT_PER_PAGE,
            "p": "?predicate",
            "o": "?object",
            "lang": ""}

        for (query_param, default_value) in query_params.items():
            query_params[query_param] = self.get_argument(query_param, default_value)

        query_string_keys = set(self.request.arguments.keys())
        query_params_supported = set(query_params.keys())
        if not query_string_keys.issubset(query_params_supported):
            self.set_status(400)
            return

        self.set_header('Access-Control-Allow-Origin', '*')
        response = filter_instances(query_params)
        if response is None:
            self.set_status(404)
        else:
            self.write(response)
