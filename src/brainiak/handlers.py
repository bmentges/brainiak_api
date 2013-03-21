# -*- coding: utf-8 -*-
from tornado.web import HTTPError, RequestHandler
from tornado.web import URLSpec

import httplib
import sys
import traceback

from brainiak import settings, triplestore
from brainiak import __version__
from brainiak.schema.resource import get_schema
from brainiak.instance.resource import filter_instances, get_instance
from brainiak.instance.delete_instance import delete_instance
from greenlet_tornado import greenlet_asynchronous
from brainiak import log


def get_routes():
    return [
        URLSpec(r'/healthcheck', HealthcheckHandler),
        URLSpec(r'/version', VersionHandler),
        URLSpec(r'/status/virtuoso', VirtuosoStatusHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema', SchemaHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/(?P<instance_id>[\w\-]+)', InstanceHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)', InstanceListHandler),
        URLSpec(r'/.*$', UnmatchedHandler),
    ]


class BrainiakRequestHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(BrainiakRequestHandler, self).__init__(*args, **kwargs)

    def _request_summary(self):
        return "{0} {1} ({2})".format(
            self.request.method, self.request.host, self.request.remote_ip)

    def _handle_request_exception(self, e):
        if hasattr(e, "status_code") and e.status_code in httplib.responses:
            status_code = e.status_code
        else:
            status_code = 500
        error_message = "[{0}] on {1}".format(status_code, self._request_summary())
        if isinstance(e, HTTPError):
            if e.log_message:
                error_message += "\n  {0}".format(e.log_message)
            if status_code == 500:
                log.logger.error("Unknown HTTP error [{0}]:\n  {1}\n".format(e.status_code, error_message))
                self.send_error(status_code, exc_info=sys.exc_info(), message=e.log_message)
            else:
                log.logger.error("HTTP error: {0}\n".format(error_message))
                self.send_error(status_code, message=e.log_message)

        else:
            log.logger.error("Uncaught exception: {0}\n".format(error_message), exc_info=True)
            self.send_error(status_code, exc_info=sys.exc_info())

    def write_error(self, status_code, **kwargs):
        error_message = "HTTP error: %d" % status_code
        if "message" in kwargs and kwargs.get("message") is not None:
            error_message += "\n{0}".format(kwargs.get("message"))
        if "exc_info" in kwargs:
            etype, value, tb = kwargs.get("exc_info")
            exception_msg = '\n'.join(traceback.format_exception(etype, value, tb))
            error_message += "\nException:\n{0}".format(exception_msg)

        error_json = {"error": error_message}
        self.finish(error_json)

    def override_defaults_with_arguments(self, immutable_params):
        overriden_params = {}
        for (query_param, default_value) in immutable_params.items():
            overriden_params[query_param] = self.get_argument(query_param, default_value)

        if overriden_params.get("lang", None) == "undefined":
            overriden_params["lang"] = False

        query_params_supported = set(overriden_params.keys())
        for arg in self.request.arguments:
            if arg not in query_params_supported:
                raise HTTPError(400, log_message="Argument {0} is not supported".format(arg))

        return overriden_params

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            raise HTTPError(404, log_message="")
        else:
            self.write(response)
            # self.finish() -- this is automagically called by greenlet_asynchronous


class HealthcheckHandler(BrainiakRequestHandler):

    def get(self):
        self.write("WORKING")


class VersionHandler(BrainiakRequestHandler):

    def get(self):
        self.write(__version__)


class VirtuosoStatusHandler(BrainiakRequestHandler):

    def get(self):
        if settings.ENVIRONMENT == 'prod':
            raise HTTPError(404)

        self.write(triplestore.status())


class SchemaHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(SchemaHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        query_params = {
            "context_name": context_name,
            "class_name": class_name,
            "class_uri": "{0}{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            "graph_uri": "{0}{1}/".format(settings.URI_PREFIX, context_name),
            "lang": self.get_argument("lang", settings.DEFAULT_LANG)
        }
        self.query_params = self.override_defaults_with_arguments(query_params)

        response = get_schema(self.query_params)

        self.finalize(response)

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            msg = "Class ({class_name}) in graph ({context_name}) was not found."
            raise HTTPError(404, log_message=msg.format(**self.query_params))
        else:
            self.write(response)


class InstanceHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(InstanceHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name, instance_id):
        # TODO refactor graph_uri, class_uri, instance_uri
        query_params = {
            "context_name": context_name,
            "class_name": class_name,
            "instance_id": instance_id,
            "request": self.request,
            "lang": self.get_argument("lang", settings.DEFAULT_LANG)
        }
        self.query_params = self.override_defaults_with_arguments(query_params)

        response = get_instance(self.query_params)

        self.finalize(response)

    @greenlet_asynchronous
    def delete(self, context_name, class_name, instance_id):
        # TODO graph_uri, instance_uri
        query_params = {
            "context_name": context_name,
            "class_name": class_name,
            "instance_id": instance_id,
            "graph_uri": "{0}{1}".format(settings.URI_PREFIX, context_name),
            "instance_uri": "{0}{1}/{2}/{3}".format(settings.URI_PREFIX, context_name, class_name, instance_id),
        }
        self.query_params = self.override_defaults_with_arguments(query_params)

        response = delete_instance(self.query_params)

        self.finalize(response)

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            msg = "Instance ({instance_id}) of class ({class_name}) in graph ({context_name}) was not found."
            raise HTTPError(404, log_message=msg.format(**self.query_params))
        else:
            self.write(response)


class InstanceListHandler(BrainiakRequestHandler):

    DEFAULT_PER_PAGE = "10"
    DEFAULT_PAGE = "0"

    def __init__(self, *args, **kwargs):
        super(InstanceListHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        query_params = {
            "context_name": context_name,
            "class_name": class_name,
            "request": self.request,
            "class_uri": "{0}{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            "graph_uri": "{0}{1}/".format(settings.URI_PREFIX, context_name),
            "lang": self.get_argument("lang", settings.DEFAULT_LANG),
            "page": self.DEFAULT_PAGE,
            "per_page": self.DEFAULT_PER_PAGE,
            "p": "?predicate",
            "o": "?object"
        }
        self.query_params = self.override_defaults_with_arguments(query_params)
        # In order to keep up with Repos, pages numbering start at 1.
        # As for Virtuoso pages start at 0, we convert page, if provided
        if "page" in self.request.arguments:
            self.query_params["page"] = str(int(self.query_params["page"]) - 1)

        response = filter_instances(self.query_params)

        self.finalize(response)

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            if "p" in self.query_params or "o" in self.query_params:
                filter_message = " with filter predicate={p} object={o} ".format(**self.query_params)
                self.query_params["filter_message"] = filter_message
            msg = "Instances of class ({class_uri}) in graph ({graph_uri}) {filter_message} were not found."
            raise HTTPError(404, log_message=msg.format(**self.query_params))
        else:
            self.write(response)


class UnmatchedHandler(BrainiakRequestHandler):

    def default_action(self):
        raise HTTPError(404, log_message="The URL ({0}) is not recognized.".format(self.request.full_url()))

    @greenlet_asynchronous
    def get(self):
        self.default_action()

    @greenlet_asynchronous
    def post(self):
        self.default_action()

    @greenlet_asynchronous
    def put(self):
        self.default_action()

    @greenlet_asynchronous
    def delete(self):
        self.default_action()

    @greenlet_asynchronous
    def patch(self):
        self.default_action()
