# -*- coding: utf-8 -*-

from tornado.web import HTTPError, RequestHandler

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


class ValidatingHandler(RequestHandler):
    """Class that defines a common processing pattern to several primitives of the API.
    Currently it supports: argument validation and CORS.
    """
    def __init__(self, *args, **kwargs):
        super(ValidatingHandler, self).__init__(*args, **kwargs)

    def override_defaults_with_arguments(self, immutable_params):
        overriden_params = {}
        for (query_param, default_value) in immutable_params.items():
            overriden_params[query_param] = self.get_argument(query_param, default_value)

        query_string_keys = set(self.request.arguments.keys())
        query_params_supported = set(overriden_params.keys())
        for arg in self.request.arguments:
            if arg not in query_params_supported:
                raise HTTPError(400, log_message="Argument {0} passed is not supported".format(arg))

        return overriden_params

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            raise HTTPError(404, log_message="")
        else:
            self.write(response)
            # self.finish() -- this is automagically called by greenlet_asynchronous


class SchemaHandler(ValidatingHandler):

    def __init__(self, *args, **kwargs):
        super(SchemaHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        query_params = {
            "class_uri": "{0}{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            "graph_uri": "{0}{1}/".format(settings.URI_PREFIX, context_name),
            "lang": self.get_argument("lang", settings.DEFAULT_LANG)
        }
        query_params = self.override_defaults_with_arguments(query_params)

        response = get_schema(query_params)

        self.finalize(response)


class InstanceHandler(ValidatingHandler):

    def __init__(self, *args, **kwargs):
        super(InstanceHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name, instance_id):
        query_params = {
            "context_name": context_name,
            "class_name": class_name,
            "instance_id": instance_id,
            "request": self.request,
            "lang": self.get_argument("lang", settings.DEFAULT_LANG)
        }
        query_params = self.override_defaults_with_arguments(query_params)

        response = get_instance(self.request, context_name, class_name, instance_id)

        self.finalize(response)


class InstanceListHandler(ValidatingHandler):

    DEFAULT_PER_PAGE = "10"
    DEFAULT_PAGE = "0"

    def __init__(self, *args, **kwargs):
        super(InstanceListHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        query_params = {
            "class_uri": "{0}{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            "graph_uri": "{0}{1}/".format(settings.URI_PREFIX, context_name),
            "lang": self.get_argument("lang", settings.DEFAULT_LANG),
            "page": self.DEFAULT_PAGE,
            "per_page": self.DEFAULT_PER_PAGE,
            "p": "?predicate",
            "o": "?object"
        }
        query_params = self.override_defaults_with_arguments(query_params)

        # In order to keep up with Repos, pages numbering start at 1.
        # As for Virtuoso pages start at 0, we convert page, if provided
        if "page" in self.request.arguments:
            query_params["page"] = str(int(query_params["page"]) - 1)

        response = filter_instances(query_params)

        self.finalize(response)
