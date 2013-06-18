# -*- coding: utf-8 -*-
import httplib
import sys
import traceback
from contextlib import contextmanager
from copy import copy

import ujson as json

from tornado.curl_httpclient import CurlError
from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.web import HTTPError, RequestHandler, URLSpec
from tornado_cors import custom_decorator
from tornado_cors import CorsMixin

from brainiak import __version__, event_bus, triplestore, settings
from brainiak.utils.cache import memoize
from brainiak.log import get_logger
from brainiak.event_bus import notify_bus, MiddlewareError
from brainiak.greenlet_tornado import greenlet_asynchronous
from brainiak.context.list_resource import list_classes
from brainiak.instance.create_resource import create_instance
from brainiak.instance.delete_resource import delete_instance
from brainiak.instance.edit_resource import edit_instance, instance_exists
from brainiak.instance.get_resource import get_instance
from brainiak.instance.list_resource import filter_instances
from brainiak.prefix.list_resource import list_prefixes
from brainiak.root.get import list_all_contexts
from brainiak.schema import resource as schema_resource
from brainiak.utils import cache
from brainiak.utils.params import CACHE_PARAMS, ParamDict, InvalidParam, LIST_PARAMS, FILTER_PARAMS, optionals, INSTANCE_PARAMS, CLASS_PARAMS, GRAPH_PARAMS
from brainiak.utils.links import build_schema_url
from brainiak.utils.resources import LazyObject
from brainiak.utils.resources import check_messages_when_port_is_mentioned
from brainiak.event_bus import NotificationFailure


logger = LazyObject(get_logger)

custom_decorator.wrapper = greenlet_asynchronous


class ListServiceParams(ParamDict):
    "Customize parameters for services with pagination"
    optionals = LIST_PARAMS


@contextmanager
def safe_params(valid_params=None):
    try:
        yield
    except InvalidParam as ex:
        msg = "Argument {0:s} is not supported. ".format(ex)
        if valid_params is not None:
            params_msg = ", ".join(valid_params.keys())
            msg += "The supported arguments are: {0}.".format(params_msg)
        raise HTTPError(400, log_message=msg)


def get_routes():
    return [
        URLSpec(r'/healthcheck/?', HealthcheckHandler),
        URLSpec(r'/version/?', VersionHandler),
        URLSpec(r'/prefixes/?', PrefixHandler),
        URLSpec(r'/_status/?$', StatusHandler),
        URLSpec(r'/_status/activemq/?', EventBusStatusHandler),
        URLSpec(r'/_status/cache/?', CacheStatusHandler),
        URLSpec(r'/_status/virtuoso/?', VirtuosoStatusHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema/?', SchemaHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/?', CollectionHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/(?P<instance_id>[\w\-]+)/?', InstanceHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/?', ContextHandler),
        URLSpec(r'/$', RootHandler),
        URLSpec(r'/.*$', UnmatchedHandler),
    ]


class BrainiakRequestHandler(CorsMixin, RequestHandler):

    CORS_ORIGIN = '*'
    CORS_HEADERS = settings.CORS_HEADERS

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

        if isinstance(e, NotificationFailure):
            message = str(e)
            logger.error(message)
            self.send_error(status_code, message=message)

        elif isinstance(e, CurlError):
            message = "Access to backend service failed.  {0:s}.".format(e)
            extra_messages = check_messages_when_port_is_mentioned(str(e))
            if extra_messages:
                for msg in extra_messages:
                    message += msg

            logger.error(message)
            self.send_error(status_code, message=message)

        if isinstance(e, ClientHTTPError):
            if e.code == 401:
                message = str(e)
                logger.error(message)
                self.send_error(status_code, message=message)

        elif isinstance(e, HTTPError):
            if e.log_message:
                error_message += "\n  {0}".format(e.log_message)
            if status_code == 500:
                logger.error("Unknown HTTP error [{0}]:\n  {1}\n".format(e.status_code, error_message))
                self.send_error(status_code, exc_info=sys.exc_info(), message=e.log_message)
            else:
                logger.error("HTTP error: {0}\n".format(error_message))
                self.send_error(status_code, message=e.log_message)

        else:
            logger.error("Uncaught exception: {0}\n".format(error_message), exc_info=True)
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
        request_uri = self.request.uri
        if not request_uri.endswith("/"):
            request_uri = "{0}/".format(request_uri)
        url = "{0}://{1}{2}{3}".format(self.request.protocol, self.request.host, request_uri, resource_id)
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
        self.write(triplestore.status())


class CacheStatusHandler(BrainiakRequestHandler):

    def get(self):
        self.write(cache.status())


class EventBusStatusHandler(BrainiakRequestHandler):

    def get(self):
        self.write(event_bus.status())


class StatusHandler(BrainiakRequestHandler):

    def get(self):
        triplestore_status = triplestore.status()
        event_bus_status = event_bus.status()
        output = []
        if "SUCCEED" not in triplestore_status:
            output.append(triplestore_status)
        if "FAILED" in event_bus_status:
            output.append(event_bus_status)
        if output:
            response = "\n".join(output)
        else:
            response = "WORKING"
        self.write(response)


class SchemaHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(SchemaHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        valid_params = optionals('graph_uri')
        with safe_params(valid_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          **valid_params)
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
        optional_params = INSTANCE_PARAMS
        with safe_params(optional_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          instance_id=instance_id,
                                          **optional_params)

        response = get_instance(self.query_params)

        self.finalize(response)

    @greenlet_asynchronous
    def put(self, context_name, class_name, instance_id):
        valid_params = INSTANCE_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          instance_id=instance_id,
                                          **valid_params)

        try:
            instance_data = json.loads(self.request.body)
        except ValueError:
            raise HTTPError(400, log_message="No JSON object could be decoded")

        if not instance_exists(self.query_params):
            schema = schema_resource.get_schema(self.query_params)
            if schema is None:
                raise HTTPError(404, log_message="Class {0} doesn't exist in context {1}.".format(class_name, context_name))
            instance_uri, instance_id = create_instance(self.query_params, instance_data, self.query_params["instance_uri"])
            resource_url = self.request.full_url()
            self.set_status(201)
            self.set_header("location", resource_url)
        else:
            edit_instance(self.query_params, instance_data)

        response = get_instance(self.query_params)

        if response and settings.NOTIFY_BUS:
            instance_dict = copy(response)
            instance_dict.pop("links", None)
            notify_bus(instance=instance_dict["@id"], klass=self.query_params["class_uri"],
                       graph=self.query_params["graph_uri"], action="PUT", instance_data=instance_dict)

        self.finalize(response)

    @greenlet_asynchronous
    def delete(self, context_name, class_name, instance_id):
        valid_params = INSTANCE_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          instance_id=instance_id,
                                          **valid_params)

        deleted = delete_instance(self.query_params)
        if deleted:
            response = 204
            if settings.NOTIFY_BUS:
                notify_bus(instance=self.query_params["instance_uri"], klass=self.query_params["class_uri"],
                           graph=self.query_params["graph_uri"], action="DELETE")
        else:
            response = None
        self.finalize(response)

    def finalize(self, response):
        if response is None:
            msg = "Instance ({instance_uri}) of class ({class_uri}) in graph ({graph_uri}) was not found."
            raise HTTPError(404, log_message=msg.format(**self.query_params))
        elif isinstance(response, dict):
            self.write(response)
            schema_url = build_schema_url(self.query_params)
            content_type = "application/json; profile={0}".format(schema_url)
            self.set_header("Content-Type", content_type)
        elif isinstance(response, int):  # status code
            self.set_status(response)
            # A call to finalize() was removed from here! -- rodsenra 2013/04/25


class CollectionHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(CollectionHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        valid_params = LIST_PARAMS + FILTER_PARAMS + CLASS_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          **valid_params)

        response = filter_instances(self.query_params)

        self.finalize(response)

    @greenlet_asynchronous
    def post(self, context_name, class_name):
        valid_params = CLASS_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          **valid_params)

        schema = schema_resource.get_schema(self.query_params)
        if schema is None:
            raise HTTPError(404, log_message="Class {0} doesn't exist in context {1}.".format(class_name, context_name))

        try:
            instance_data = json.loads(self.request.body)
        except ValueError:
            raise HTTPError(400, log_message="No JSON object could be decoded")

        (instance_uri, instance_id) = create_instance(self.query_params, instance_data)
        instance_url = self.build_resource_url(instance_id)

        self.set_status(201)
        self.set_header("location", instance_url)

        self.query_params["instance_uri"] = instance_uri
        self.query_params["instance_id"] = instance_id
        instance_data = get_instance(self.query_params)

        if settings.NOTIFY_BUS:
            try:
                instance_data_without_links = copy(instance_data)
                instance_data_without_links.pop("links", None)
                notify_bus(instance=instance_uri, klass=self.query_params["class_uri"],
                           graph=self.query_params["graph_uri"], action="POST", instance_data=instance_data_without_links)
            except MiddlewareError:
                # rollback data insertion
                self.query_params['instance_id'] = instance_id
                response = delete_instance(self.query_params)
                if not response:
                    msg = "Could not notify bus and failed to rollback insertion of {0}. ALERT: Search engines are not in sync anymore!"
                else:
                    msg = "Could not notify bus about insertion of {0}, rollback was successful."
                raise NotificationFailure(msg.format(self.query_params['instance_uri']))

        self.finalize(instance_data)

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


class RootHandler(BrainiakRequestHandler):

    #SUPPORTED_METHODS = list(BrainiakRequestHandler.SUPPORTED_METHODS) + ["PURGE"]
    #def purge(self):
    #    self.finalize({"oi": "xubiru"})

    @greenlet_asynchronous
    def get(self):
        valid_params = LIST_PARAMS + CACHE_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self, **valid_params)

        response = memoize(list_all_contexts, self.query_params)

        self.finalize(response)


class ContextHandler(BrainiakRequestHandler):

    @greenlet_asynchronous
    def get(self, context_name):
        valid_params = LIST_PARAMS + GRAPH_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self, context_name=context_name, **valid_params)

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
        valid_params = LIST_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self, **valid_params)

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
