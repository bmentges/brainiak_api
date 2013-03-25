# -*- coding: utf-8 -*-
import httplib
import json
import sys
import traceback

from tornado.web import HTTPError, RequestHandler, URLSpec
from tornado.httpclient import HTTPResponse


from brainiak import __version__, log, settings, triplestore
from brainiak.schema import resource as schema_resource
from brainiak.instance.get_resource import get_instance
from brainiak.instance.list_resource import filter_instances
from brainiak.instance.delete_resource import delete_instance
from brainiak.instance.create_resource import create_instance
from brainiak.prefixes import safe_slug_to_prefix
from greenlet_tornado import greenlet_asynchronous


def get_routes():
    return [
        URLSpec(r'/healthcheck', HealthcheckHandler),
        URLSpec(r'/version', VersionHandler),
        URLSpec(r'/status/virtuoso', VirtuosoStatusHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema', SchemaHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/(?P<instance_id>[\w\-]+)', InstanceHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)', CollectionHandler),
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

        response = schema_resource.get_schema(self.query_params)

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
        query_params = {
            "context_name": context_name,
            "class_name": class_name,
            "class_uri": "{0}{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            "instance_id": instance_id,
            "request": self.request,
            "lang": settings.DEFAULT_LANG,
            "instance_prefix": "",
            "graph_uri": "{0}{1}".format(settings.URI_PREFIX, context_name),
            "instance_uri": "{0}{1}/{2}/{3}".format(settings.URI_PREFIX, context_name, class_name, instance_id),
        }

        query_params = self.override_defaults_with_arguments(query_params)

        if query_params.get("instance_prefix"):
            prefix = safe_slug_to_prefix(query_params["instance_prefix"])
            query_params["instance_uri"] = "%s%s" % (prefix, query_params["instance_id"])

        response = get_instance(query_params)

        self.query_params = query_params
        self.finalize(response)

    @greenlet_asynchronous
    def delete(self, context_name, class_name, instance_id):
        query_params = {
            "context_name": context_name,
            "class_name": class_name,
            "instance_id": instance_id,
            "graph_uri": "{0}{1}".format(settings.URI_PREFIX, context_name),
            "instance_uri": "{0}{1}/{2}/{3}".format(settings.URI_PREFIX, context_name, class_name, instance_id),
        }
        self.query_params = self.override_defaults_with_arguments(query_params)

        deleted = delete_instance(self.query_params)

        if deleted:
            response = 204
        else:
            response = None

        self.finalize(response)

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            msg = "Instance ({instance_id}) of class ({class_name}) in graph ({context_name}) was not found."
            raise HTTPError(404, log_message=msg.format(**self.query_params))
        elif isinstance(response, dict):
            self.write(response)
        elif isinstance(response, int):  # status code
            self.set_status(response)
            self.finish()


class CollectionHandler(BrainiakRequestHandler):

    DEFAULT_PER_PAGE = "10"
    DEFAULT_PAGE = "0"

    def __init__(self, *args, **kwargs):
        super(CollectionHandler, self).__init__(*args, **kwargs)

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

    @greenlet_asynchronous
    def post(self, context_name, class_name):
        query_params = {
            "context_name": context_name,
            "class_name": class_name,
            "class_prefix": "",
            "class_uri": "{0}{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            "request": self.request,
            "lang": settings.DEFAULT_LANG,
            "graph_uri": "{0}{1}/".format(settings.URI_PREFIX, context_name)
        }

        if self.request.arguments:
            query_params = self.override_defaults_with_arguments(query_params)

        # TODO: test
        class_prefix = query_params["class_prefix"]
        if class_prefix:
            query_params["class_uri"] = "%s/%s" % (class_prefix, class_name)

        schema = schema_resource.get_schema(query_params)
        if schema is None:
            raise HTTPError(404, log_message="Class {0} doesn't exist in context {1}.".format(class_name, context_name))

        try:
            instance_data = json.loads(self.request.body)
        except ValueError:
            raise HTTPError(400, log_message="No JSON object could be decoded")

        resource_id = create_instance(query_params, instance_data)

        self.set_status(201)
        self.set_header("location", resource_id)
        self.query_params = query_params
        self.finalize("")

    def finalize(self, response):
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            # TODO separate filter message logic (e.g. if response is None and ("p" in self.query_params or "o" in self.query_params))
            filter_message = []
            if self.query_params['p'] != "?predicate":
                filter_message.append(" with predicate={0} ".format(self.query_params['p']))
            if self.query_params['o'] != "?object":
                filter_message.append(" with object={0} ".format(self.query_params['o']))
            self.query_params["filter_message"] = "".join(filter_message)
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
