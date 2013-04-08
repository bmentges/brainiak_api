# -*- coding: utf-8 -*-
import httplib
import json
import sys
import traceback
from contextlib import contextmanager

from tornado.web import HTTPError, RequestHandler, URLSpec
from tornado_cors import custom_decorator
from tornado_cors import CorsMixin

from brainiak import __version__, log, settings, triplestore
from brainiak.schema import resource as schema_resource
from brainiak.instance.get_resource import get_instance
from brainiak.instance.list_resource import filter_instances
from brainiak.instance.delete_resource import delete_instance
from brainiak.instance.create_resource import create_instance
from brainiak.instance.edit_resource import edit_instance, instance_exists
from brainiak.context.list_resource import list_classes
from brainiak.prefix.list_resource import list_prefixes
from brainiak.domain.get import list_domains
from brainiak.utils.params import ParamDict, InvalidParam, LIST_PARAMS, FILTER_PARAMS
from brainiak.greenlet_tornado import greenlet_asynchronous

custom_decorator.wrapper = greenlet_asynchronous


class ListServiceParams(ParamDict):
    "Customize parameters for services with pagination"
    extra_params = LIST_PARAMS


class ListAndFilterServiceParams(ParamDict):
    "Customize parameters for services with pagination and filtering by ?p and ?o"
    extra_params = LIST_PARAMS + FILTER_PARAMS


@contextmanager
def safe_params():
    try:
        yield
    except InvalidParam as ex:
        raise HTTPError(400, log_message="Argument {0:s} is not supported".format(ex))


def get_routes():
    return [
        URLSpec(r'/healthcheck/?', HealthcheckHandler),
        URLSpec(r'/version/?', VersionHandler),
        URLSpec(r'/prefixes/?', PrefixHandler),
        URLSpec(r'/status/virtuoso/?', VirtuosoStatusHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema/?', SchemaHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/(?P<instance_id>[\w\-]+)/?', InstanceHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/?', CollectionHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/?', ContextHandler),
        URLSpec(r'/$', DomainHandler),
        URLSpec(r'/.*$', UnmatchedHandler),
    ]


class BrainiakRequestHandler(CorsMixin, RequestHandler):

    CORS_ORIGIN = '*'
    CORS_HEADERS = 'Content-Type'

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

    def build_resource_url(self, resource_id):
        url = "{0}://{1}{2}{3}".format(self.request.protocol, self.request.host, self.request.uri, resource_id)
        if self.request.query:
            url = "{0}?{1}".format(url, self.request.query)
        return url

    def finalize(self, response):
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
        with safe_params():
            self.query_params = ParamDict(self, context_name=context_name, class_name=class_name)
        response = schema_resource.get_schema(self.query_params)
        self.finalize(response)

    def finalize(self, response):
        if response is None:
            msg = "Class ({class_uri}) in graph ({graph_uri}) was not found."
            raise HTTPError(404, log_message=msg.format(**self.query_params))
        else:
            self.write(response)


class InstanceHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(InstanceHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name, instance_id):
        with safe_params():
            self.query_params = ParamDict(self, context_name=context_name, class_name=class_name, instance_id=instance_id)

        response = get_instance(self.query_params)

        self.finalize(response)

    @greenlet_asynchronous
    def put(self, context_name, class_name, instance_id):
        with safe_params():
            self.query_params = ParamDict(self, context_name=context_name, class_name=class_name, instance_id=instance_id)

        try:
            instance_data = json.loads(self.request.body)
        except ValueError:
            raise HTTPError(400, log_message="No JSON object could be decoded")

        if not instance_exists(self.query_params):
            schema = schema_resource.get_schema(self.query_params)
            if schema is None:
                raise HTTPError(404, log_message="Class {0} doesn't exist in context {1}.".format(class_name, context_name))
            create_instance(self.query_params, instance_data, self.query_params["instance_uri"])
            resource_url = self.request.full_url()
            self.set_status(201)
            self.set_header("location", resource_url)
        else:
            edit_instance(self.query_params, instance_data)

        response = get_instance(self.query_params)

        self.finalize(response)

    @greenlet_asynchronous
    def delete(self, context_name, class_name, instance_id):
        with safe_params():
            self.query_params = ParamDict(self, context_name=context_name, class_name=class_name, instance_id=instance_id)

        deleted = delete_instance(self.query_params)

        response = 204 if deleted else None

        self.finalize(response)

    def finalize(self, response):
        if response is None:
            msg = "Instance ({instance_uri}) of class ({class_uri}) in graph ({graph_uri}) was not found."
            raise HTTPError(404, log_message=msg.format(**self.query_params))
        elif isinstance(response, dict):
            self.write(response)
        elif isinstance(response, int):  # status code
            self.set_status(response)
            self.finish()


class CollectionHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(CollectionHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        with safe_params():
            self.query_params = ListServiceParams(self, context_name=context_name, class_name=class_name)

        response = filter_instances(self.query_params)

        self.finalize(response)

    @greenlet_asynchronous
    def post(self, context_name, class_name):
        with safe_params():
            self.query_params = ParamDict(self, context_name=context_name, class_name=class_name)

        schema = schema_resource.get_schema(self.query_params)
        if schema is None:
            raise HTTPError(404, log_message="Class {0} doesn't exist in context {1}.".format(class_name, context_name))

        try:
            instance_data = json.loads(self.request.body)
        except ValueError:
            raise HTTPError(400, log_message="No JSON object could be decoded")

        instance_id = create_instance(self.query_params, instance_data)
        instance_url = self.build_resource_url(instance_id)
        self.set_status(201)
        self.set_header("location", instance_url)
        self.finalize("")

    def finalize(self, response):
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


class DomainHandler(BrainiakRequestHandler):

    @greenlet_asynchronous
    def get(self):
        with safe_params():
            self.query_params = ListAndFilterServiceParams(self)

        response = list_domains(self.query_params, self.request)

        self.finalize(response)


class ContextHandler(BrainiakRequestHandler):

    @greenlet_asynchronous
    def get(self, context_name):
        with safe_params():
            self.query_params = ListAndFilterServiceParams(self, context_name=context_name)

        response = list_classes(self.query_params)

        self.finalize(response)

    def finalize(self, response):
        if response is None:
            msg = "No classes found in graph ({graph_uri})."
            raise HTTPError(404, log_message=msg.format(**self.query_params))
        else:
            self.write(response)


class PrefixHandler(BrainiakRequestHandler):

    @greenlet_asynchronous
    def get(self):
        with safe_params():
            self.query_params = ListAndFilterServiceParams(self)

        response = list_prefixes()

        self.finalize(response)


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
