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
        response = get_schema(context_name, class_name)
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            self.set_status(404)
        else:
            self.write(response)
        # self.finish() -- this is automagically called by greenlet_asynchronous


class InstanceHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(InstanceHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name, instance_id):
        response = get_instance(self.request, context_name, class_name, instance_id)
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            self.set_status(404)
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
            "class_uri": "{0}{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            "graph_uri": "{0}{1}/".format(settings.URI_PREFIX, context_name),
            "lang": "",
            "page": self.DEFAULT_PAGE,
            "per_page": self.DEFAULT_PER_PAGE,
            "p": "?predicate",
            "o": "?object"
        }

        for (query_param, default_value) in query_params.items():
            query_params[query_param] = self.get_argument(query_param, default_value)

        # In order to keep up with Repos, pages numbering start at 1.
        # As for Virtuoso pages start at 0, we convert page, if provided
        if "page" in self.request.arguments:
            query_params["page"] = str(int(query_params["page"]) - 1)

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
