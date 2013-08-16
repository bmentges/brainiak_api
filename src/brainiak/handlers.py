# -*- coding: utf-8 -*-
import sys
import traceback
from contextlib import contextmanager

import ujson as json
from tornado.curl_httpclient import CurlError
from tornado.web import HTTPError, RequestHandler, URLSpec
from tornado_cors import CorsMixin, custom_decorator

from brainiak import __version__, event_bus, triplestore, settings
from brainiak.collection.get_collection import filter_instances
from brainiak.collection.json_schema import schema as collection_schema
from brainiak.context.get_context import list_classes
from brainiak.context.json_schema import schema as context_schema
from brainiak.event_bus import NotificationFailure, notify_bus, MiddlewareError
from brainiak.greenlet_tornado import greenlet_asynchronous
from brainiak.instance.create_instance import create_instance
from brainiak.instance.delete_instance import delete_instance
from brainiak.instance.edit_instance import edit_instance, instance_exists
from brainiak.instance.get_instance import get_instance
from brainiak.log import get_logger
from brainiak.prefix.get_prefixes import list_prefixes
from brainiak.prefixes import expand_all_uris_recursively
from brainiak.range_search.range_search import do_range_search, SUGGEST_OPTIONAL_PARAMS, SUGGEST_REQUIRED_PARAMS
from brainiak.root.get_root import list_all_contexts
from brainiak.root.json_schema import schema as root_schema
from brainiak.schema import get_class as schema_resource
from brainiak.utils import cache
from brainiak.utils.cache import memoize
from brainiak.utils.links import build_schema_url_for_instance, content_type_profile, build_schema_url
from brainiak.utils.params import CACHE_PARAMS, CLASS_PARAMS, InvalidParam, LIST_PARAMS, GRAPH_PARAMS, INSTANCE_PARAMS, PAGING_PARAMS, ParamDict, optionals, RequiredParamMissing, validate_body_params
from brainiak.utils.resources import check_messages_when_port_is_mentioned, LazyObject
from brainiak.utils.sparql import extract_po_tuples


logger = LazyObject(get_logger)

custom_decorator.wrapper = greenlet_asynchronous


class ListServiceParams(ParamDict):
    """Customize parameters for services with pagination"""
    optionals = LIST_PARAMS


@contextmanager
def safe_params(valid_params=None, body_params=None):
    try:
        yield
    except InvalidParam as ex:
        msg = "Argument {0:s} is not supported.".format(ex)
        if valid_params is not None:
            params_msg = ", ".join(valid_params.keys())
            msg += " The supported querystring arguments are: {0}.".format(params_msg)
        if body_params is not None:
            body_msg = ", ".join(body_params)
            msg += " The supported body arguments are: {0}.".format(body_msg)
        raise HTTPError(400, log_message=msg)
    except RequiredParamMissing as ex:
        msg = "Required parameter ({0:s}) was not given.".format(ex)
        raise HTTPError(400, log_message=str(msg))


def get_routes():
    return [
        # internal resources for monitoring and meta-infromation inspection
        URLSpec(r'/healthcheck/?', HealthcheckHandler),
        URLSpec(r'/_version/?', VersionHandler),
        URLSpec(r'/_prefixes/?', PrefixHandler),
        URLSpec(r'/_status/?$', StatusHandler),
        URLSpec(r'/_status/activemq/?', EventBusStatusHandler),
        URLSpec(r'/_status/cache/?', CacheStatusHandler),
        URLSpec(r'/_status/virtuoso/?', VirtuosoStatusHandler),
        # json-schemas
        URLSpec(r'/_schema_list/?', RootJsonSchemaHandler),
        URLSpec(r'/_range_search/?', RangeSearchHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/_schema_list/?', ContextJsonSchemaHandler),
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema_list/?', CollectionJsonSchemaHandler),
        # resources that represents concepts
        URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema/?', ClassHandler),
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

    @greenlet_asynchronous
    def purge(self):
        if settings.ENABLE_CACHE:
            path = self.request.path
            recursive = int(self.request.headers.get('X-Cache-recursive', '0'))
            if recursive:
                cache.purge(path)
            else:
                cache.delete(path)
        else:
            raise HTTPError(405, log_message="Cache is disabled (Brainaik's settings.ENABLE_CACHE is set to False)")

    def _request_summary(self):
        return "{0} {1} ({2})".format(
            self.request.method, self.request.host, self.request.remote_ip)

    def _handle_request_exception(self, e):
        if hasattr(e, "status_code"):  # and e.code in httplib.responses:
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

    def add_cache_headers(self, meta):
        cache_verb = meta['cache']
        cache_msg = "{0} from {1}".format(cache_verb, self.request.host)
        self.set_header("X-Cache", cache_msg)
        self.set_header("Last-Modified", meta['last_modified'])

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


class RootJsonSchemaHandler(BrainiakRequestHandler):

    SUPPORTED_METHODS = list(BrainiakRequestHandler.SUPPORTED_METHODS) + ["PURGE"]

    def get(self):
        valid_params = CACHE_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self, **valid_params)
        response = memoize(self.query_params, root_schema)
        self.add_cache_headers(response['meta'])
        self.finalize(response['body'])


class RootHandler(BrainiakRequestHandler):

    SUPPORTED_METHODS = list(BrainiakRequestHandler.SUPPORTED_METHODS) + ["PURGE"]

    @greenlet_asynchronous
    def get(self):
        valid_params = PAGING_PARAMS + CACHE_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self, **valid_params)
        response = memoize(self.query_params,
                           list_all_contexts,
                           function_arguments=self.query_params)
        self.add_cache_headers(response['meta'])
        self.finalize(response['body'])

    def finalize(self, response):
        if isinstance(response, dict):
            self.write(response)
            self.set_header("Content-Type", content_type_profile(build_schema_url(self.query_params)))


class ContextJsonSchemaHandler(BrainiakRequestHandler):

    def get(self, context_name):
        self.finalize(context_schema(context_name))


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
            self.set_header("Content-Type", content_type_profile(build_schema_url(self.query_params)))


class ClassHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(ClassHandler, self).__init__(*args, **kwargs)

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


class CollectionJsonSchemaHandler(BrainiakRequestHandler):

    def get(self, context_name, class_name):
        query_params = ParamDict(self, context_name=context_name, class_name=class_name)
        self.finalize(collection_schema(context_name, class_name, query_params.get('class_prefix', None)))


class CollectionHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(CollectionHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        valid_params = LIST_PARAMS + CLASS_PARAMS
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
                # TODO: uncomment below
                instance_data_for_bus = expand_all_uris_recursively(instance_data)
                notify_bus(instance=instance_uri,
                           klass=self.query_params["class_uri"],
                           graph=self.query_params["graph_uri"],
                           action="POST",
                           instance_data=instance_data_for_bus)
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
            po_tuples = extract_po_tuples(self.query_params)
            sorted_po_tuples = sorted(po_tuples, key=lambda po: po[2])
            for (p, o, index) in sorted_po_tuples:
                if not index:
                    index = ''
                if not p.startswith("?"):
                    filter_message.append(" with p{0}=({1})".format(index, p))
                if not o.startswith("?"):
                    filter_message.append(" with o{0}=({1})".format(index, o))
            self.query_params["filter_message"] = "".join(filter_message)
            msg = "Instances of class ({class_uri}) in graph ({graph_uri}){filter_message} and in language=({lang}) were not found."
            raise HTTPError(404, log_message=msg.format(**self.query_params))
        else:
            self.write(response)
            self.set_header("Content-Type", content_type_profile(build_schema_url(self.query_params)))


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
            notify_bus(instance=response["@id"],
                       klass=self.query_params["class_uri"],
                       graph=self.query_params["graph_uri"],
                       action="PUT",
                       instance_data=response)

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
            self.set_header("Content-Type", content_type_profile(build_schema_url_for_instance(self.query_params)))
        elif isinstance(response, int):  # status code
            self.set_status(response)
            # A call to finalize() was removed from here! -- rodsenra 2013/04/25


class RangeSearchHandler(BrainiakRequestHandler):

    @greenlet_asynchronous
    def post(self):
        valid_params = PAGING_PARAMS

        body_params = json.loads(self.request.body)

        with safe_params(valid_params, SUGGEST_REQUIRED_PARAMS + SUGGEST_OPTIONAL_PARAMS):
            validate_body_params(body_params, SUGGEST_REQUIRED_PARAMS, SUGGEST_OPTIONAL_PARAMS)
            self.query_params = ParamDict(self, **valid_params)
            self.query_params.validate_required(valid_params)

        response = None   # do_range_search(self.query_params)

        self.finalize(response)

    def finalize(self, response):
        if response is None:
            msg = "There were no search results."
            raise HTTPError(404, log_message=msg)
        elif isinstance(response, dict):
            self.write(response)
            self.set_header("Content-Type", content_type_profile(build_schema_url_for_instance(self.query_params)))
        elif isinstance(response, int):  # status code
            self.set_status(response)
            # A call to finalize() was removed from here! -- rodsenra 2013/04/25


class PrefixHandler(BrainiakRequestHandler):

    @greenlet_asynchronous
    def get(self):
        valid_params = LIST_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self, **valid_params)

        response = list_prefixes()

        self.finalize(response)


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
