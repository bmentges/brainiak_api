# -*- coding: utf-8 -*-
from tornado.web import HTTPError, RequestHandler
import httplib
import sys
import traceback

from brainiak import settings, triplestore
from brainiak import __version__
from brainiak.schema.resource import get_schema
from brainiak.instance.resource import filter_instances, get_instance
from greenlet_tornado import greenlet_asynchronous
from brainiak import log


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
            exception_msg = ''.join(traceback.format_exception(etype, value, tb))
            error_message += "\nException:\n{0}".format(exception_msg)

        error_json = {"error": error_message}
        self.finish(error_json)

    def override_defaults_with_arguments(self, immutable_params):
        overriden_params = {}
        for (query_param, default_value) in immutable_params.items():
            overriden_params[query_param] = self.get_argument(query_param, default_value)

        if overriden_params["lang"] == "undefined":
            overriden_params["lang"] = False

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
            "class_uri": "{0}{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            "graph_uri": "{0}{1}/".format(settings.URI_PREFIX, context_name),
            "lang": self.get_argument("lang", settings.DEFAULT_LANG)
        }
        query_params = self.override_defaults_with_arguments(query_params)

        response = get_schema(query_params)

        self.finalize(response)

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            raise HTTPError(404, log_message="Class not found in the triplestore.")
        else:
            self.write(response)


class InstanceHandler(BrainiakRequestHandler):

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

        response = get_instance(query_params)

        self.finalize(response)

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            raise HTTPError(404, log_message="Instance not found in the triplestore.")
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

        query_params = self.override_defaults_with_arguments(query_params)

        # In order to keep up with Repos, pages numbering start at 1.
        # As for Virtuoso pages start at 0, we convert page, if provided
        if "page" in self.request.arguments:
            query_params["page"] = str(int(query_params["page"]) - 1)

        response = filter_instances(query_params)

        self.finalize(response)

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            raise HTTPError(404, log_message="There is no instances of this class in the triplestore.")
        else:
            self.write(response)
