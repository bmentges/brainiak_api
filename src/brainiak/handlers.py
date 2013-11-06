# -*- coding: utf-8 -*-
import sys
import traceback
from contextlib import contextmanager

import ujson as json
from urllib import unquote
from tornado.httpclient import HTTPError as HTTPClientError
from tornado.web import HTTPError, RequestHandler, URLSpec
from tornado_cors import CorsMixin, custom_decorator
from jsonschema import validate, ValidationError

# must be imported before other modules
from brainiak.log import get_logger

from brainiak import __version__, event_bus, triplestore, settings
from brainiak.collection.get_collection import filter_instances
from brainiak.collection.json_schema import schema as collection_schema
from brainiak.context.get_context import list_classes
from brainiak.context.json_schema import schema as context_schema
from brainiak.event_bus import NotificationFailure, notify_bus
from brainiak.greenlet_tornado import greenlet_asynchronous
from brainiak.instance.create_instance import create_instance
from brainiak.instance.delete_instance import delete_instance
from brainiak.instance.edit_instance import edit_instance, instance_exists
from brainiak.instance.get_instance import get_instance
from brainiak.prefixes import normalize_all_uris_recursively, list_prefixes, SHORTEN
from brainiak.root.get_root import list_all_contexts
from brainiak.root.json_schema import schema as root_schema
from brainiak.schema import get_class as schema_resource
from brainiak.schema.get_class import SchemaNotFound
from brainiak.suggest.json_schema import schema as suggest_schema
from brainiak.suggest.json_schema import SUGGEST_PARAM_SCHEMA
from brainiak.suggest.suggest import do_suggest
from brainiak.utils import cache
from brainiak.utils.cache import memoize
from brainiak.utils.links import build_schema_url_for_instance, content_type_profile, build_schema_url
from brainiak.utils.params import CACHE_PARAMS, CLASS_PARAMS, InvalidParam, LIST_PARAMS, GRAPH_PARAMS, INSTANCE_PARAMS, PAGING_PARAMS, ParamDict, DEFAULT_PARAMS, RequiredParamMissing, DefaultParamsDict
from brainiak.utils.resources import check_messages_when_port_is_mentioned, LazyObject
from brainiak.utils.sparql import extract_po_tuples, clean_up_reserved_attributes, InvalidSchema


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
        msg = u"Argument {0:s} is not supported.".format(ex)
        if valid_params is not None:
            params_msg = ", ".join(sorted(valid_params.keys() + DEFAULT_PARAMS.keys()))
            msg += u" The supported querystring arguments are: {0}.".format(params_msg)
        if body_params is not None:
            body_msg = ", ".join(body_params)
            msg += u" The supported body arguments are: {0}.".format(body_msg)
        raise HTTPError(400, log_message=msg)
    except RequiredParamMissing as ex:
        msg = u"Required parameter ({0:s}) was not given.".format(ex)
        raise HTTPError(400, log_message=unicode(msg))


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
        URLSpec(r'/_suggest/?', SuggestHandler),
        URLSpec(r'/_suggest/_schema_list/?', SuggestJsonSchemaHandler),
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
            purge_all = int(self.request.headers.get('X-Cache-all', '0'))
            if purge_all:
                cache.purge("*")
                return

            path = self.request.path
            recursive = int(self.request.headers.get('X-Cache-recursive', '0'))
            if recursive:
                cache.purge(path)
            else:
                cache.delete(path)

        else:
            raise HTTPError(405, log_message="Cache is disabled (Brainaik's settings.ENABLE_CACHE is set to False)")

    def _request_summary(self):
        return u"{0} {1} ({2})".format(
            self.request.method, self.request.host, self.request.remote_ip)

    def _handle_request_exception(self, e):
        if hasattr(e, "status_code"):  # and e.code in httplib.responses:
            status_code = e.status_code
        else:
            status_code = 500

        error_message = u"[{0}] on {1}".format(status_code, self._request_summary())

        if isinstance(e, NotificationFailure):
            message = unicode(e)
            logger.error(message)
            self.send_error(status_code, message=message)

        elif isinstance(e, HTTPClientError):
            message = u"Access to backend service failed.  {0:s}.".format(unicode(e))
            extra_messages = check_messages_when_port_is_mentioned(unicode(e))
            if extra_messages:
                for msg in extra_messages:
                    message += msg

            if hasattr(e, "response") and e.response is not None and \
               hasattr(e.response, "body") and e.response.body is not None:
                    message += u"\nResponse:\n" + unicode(str(e.response.body).decode("utf-8"))

            logger.error(message)
            self.send_error(status_code, message=message)

        elif isinstance(e, InvalidSchema):
            logger.error(u"Ontology inconsistency: {0}\n".format(error_message))
            self.send_error(status_code, message=e.message)

        elif isinstance(e, HTTPError):
            if e.log_message:
                error_message += u"\n  {0}".format(e.log_message)
            if status_code == 500:
                logger.error(u"Unknown HTTP error [{0}]:\n  {1}\n".format(e.status_code, error_message))
                self.send_error(status_code, exc_info=sys.exc_info(), message=e.log_message)
            else:
                logger.error(u"HTTP error: {0}\n".format(error_message))
                self.send_error(status_code, message=e.log_message)

        else:
            logger.error(u"Uncaught exception: {0}\n".format(error_message), exc_info=True)
            self.send_error(status_code, exc_info=sys.exc_info())

    def add_cache_headers(self, meta):
        cache_verb = meta['cache']
        cache_msg = u"{0} from {1}".format(cache_verb, self.request.host)
        self.set_header("X-Cache", cache_msg)
        self.set_header("Last-Modified", meta['last_modified'])

    def _notify_bus(self, **kwargs):
        if kwargs.get("instance_data"):
            instance_data = kwargs["instance_data"]
            clean_instance_data = clean_up_reserved_attributes(instance_data)
            kwargs["instance_data"] = clean_instance_data

        notify_bus(instance=self.query_params["instance_uri"],
                   klass=self.query_params["class_uri"],
                   graph=self.query_params["graph_uri"],
                   **kwargs)

    def write_error(self, status_code, **kwargs):
        # Tornado clear the headers in case of errors, and the CORS headers are lost, we call prepare to reset CORS
        self.prepare()

        error_message = u"HTTP error: %d" % status_code
        if "message" in kwargs and kwargs.get("message") is not None:
            error_message += u"\n{0}".format(kwargs.get("message"))
        if "exc_info" in kwargs:
            etype, value, tb = kwargs.get("exc_info")
            exception_msg = u'\n'.join(traceback.format_exception(etype, value, tb))
            error_message += u"\nException:\n{0}".format(exception_msg)

        error_json = {"errors": [error_message]}
        self.finish(error_json)

    def build_resource_url(self, resource_id):
        request_uri = self.request.uri
        if not request_uri.endswith("/"):
            request_uri = u"{0}/".format(request_uri)
        url = u"{0}://{1}{2}{3}".format(self.request.protocol, self.request.host, request_uri, resource_id)
        if self.request.query:
            url = u"{0}?{1}".format(url, self.request.query)
        return url

    def finalize(self, response):
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
        del context_name

        response = list_classes(self.query_params)
        if response is None:
            raise HTTPError(404, log_message=u"Context {0} not found".format(self.query_params['graph_uri']))

        self.finalize(response)

    def finalize(self, response):
        self.write(response)
        self.set_header("Content-Type", content_type_profile(build_schema_url(self.query_params)))


class ClassHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(ClassHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        self.request.query = unquote(self.request.query)

        valid_params = {}
        with safe_params(valid_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          **valid_params)
        del context_name
        del class_name

        response = schema_resource.get_schema(self.query_params)
        if response is None:
            msg = u"Schema for class {0} in context {1} was not found."
            error_message = msg.format(self.query_params['class_uri'], self.query_params['graph_uri'])
            raise HTTPError(404, log_message=error_message)

        if self.query_params['expand_uri'] == "0":
            response = normalize_all_uris_recursively(response, mode=SHORTEN)

        self.finalize(response)


class CollectionJsonSchemaHandler(BrainiakRequestHandler):

    def get(self, context_name, class_name):
        query_params = ParamDict(self, context_name=context_name, class_name=class_name)
        self.finalize(collection_schema(context_name, class_name, query_params.get('class_prefix', None)))


class CollectionHandler(BrainiakRequestHandler):

    def __init__(self, *args, **kwargs):
        super(CollectionHandler, self).__init__(*args, **kwargs)

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        valid_params = LIST_PARAMS + CLASS_PARAMS + DefaultParamsDict(direct_instances_only='0')
        with safe_params(valid_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          **valid_params)
        del context_name
        del class_name

        response = filter_instances(self.query_params)

        if self.query_params['expand_uri'] == "0":
            response = normalize_all_uris_recursively(response, mode=SHORTEN)

        self.finalize(response)

    @greenlet_asynchronous
    def post(self, context_name, class_name):
        valid_params = CLASS_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          **valid_params)
        del context_name
        del class_name

        schema = schema_resource.get_schema(self.query_params)
        if schema is None:
            class_uri = self.query_params["class_uri"]
            graph_uri = self.query_params["graph_uri"]
            raise HTTPError(404, log_message=u"Class {0} doesn't exist in context {1}.".format(class_uri, graph_uri))

        try:
            instance_data = json.loads(self.request.body)
        except ValueError:
            raise HTTPError(400, log_message=u"No JSON object could be decoded")

        instance_data = normalize_all_uris_recursively(instance_data)

        try:
            (instance_uri, instance_id) = create_instance(self.query_params, instance_data)
        except InvalidSchema as ex:
            raise HTTPError(500, log_message=unicode(ex))

        instance_url = self.build_resource_url(instance_id)

        self.set_header("location", instance_url)

        self.query_params["instance_uri"] = instance_uri
        self.query_params["instance_id"] = instance_id
        self.query_params["expand_object_properties"] = "1"

        instance_data = get_instance(self.query_params)

        if settings.NOTIFY_BUS:
            self._notify_bus(action="POST", instance_data=instance_data)

        self.finalize(201)

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
                    filter_message.append(u" with p{0}=({1})".format(index, p))
                if not o.startswith("?"):
                    filter_message.append(u" with o{0}=({1})".format(index, o))
            self.query_params["filter_message"] = "".join(filter_message)
            self.query_params["page"] = int(self.query_params["page"]) + 1  # Showing real page in response
            msg = u"Instances of class ({class_uri}) in graph ({graph_uri}){filter_message}, language=({lang}) and in page=({page}) were not found."

            response = {
                "warning": msg.format(**self.query_params),
                "items": []
            }
            self.write(response)
        elif isinstance(response, int):  # status code
            self.set_status(response)
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
        del context_name
        del class_name
        del instance_id

        response = get_instance(self.query_params)
        if response is None:
            error_message = u"Instance ({0}) of class ({1}) in graph ({2}) was not found.".format(
                self.query_params['instance_uri'],
                self.query_params['class_uri'],
                self.query_params['graph_uri'])
            raise HTTPError(404, log_message=error_message)

        if self.query_params["expand_uri"] == "0":
            response = normalize_all_uris_recursively(response, mode=SHORTEN)

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
        del context_name
        del class_name
        del instance_id

        try:
            instance_data = json.loads(self.request.body)
        except ValueError:
            raise HTTPError(400, log_message="No JSON object could be decoded")

        instance_data = normalize_all_uris_recursively(instance_data)

        try:
            if not instance_exists(self.query_params):
                schema = schema_resource.get_schema(self.query_params)
                if schema is None:
                    msg = u"Class {0} doesn't exist in graph {1}."
                    raise HTTPError(404, log_message=msg.format(self.query_params["class_uri"],
                                                                self.query_params["graph_uri"]))
                instance_uri, instance_id = create_instance(self.query_params, instance_data, self.query_params["instance_uri"])
                resource_url = self.request.full_url()
                status = 201
                self.set_header("location", resource_url)
            else:
                edit_instance(self.query_params, instance_data)
                status = 200
        except InvalidSchema as ex:
            raise HTTPError(400, log_message=unicode(ex))
        except SchemaNotFound as ex:
            raise HTTPError(404, log_message=unicode(ex))

        self.query_params["expand_object_properties"] = "1"
        instance_data = get_instance(self.query_params)

        if instance_data and settings.NOTIFY_BUS:
            self.query_params["instance_uri"] = instance_data["@id"]
            self._notify_bus(action="PUT", instance_data=instance_data)

        self.finalize(status)

    @greenlet_asynchronous
    def delete(self, context_name, class_name, instance_id):
        valid_params = INSTANCE_PARAMS
        with safe_params(valid_params):
            self.query_params = ParamDict(self,
                                          context_name=context_name,
                                          class_name=class_name,
                                          instance_id=instance_id,
                                          **valid_params)
        del context_name
        del class_name
        del instance_id

        deleted = delete_instance(self.query_params)
        if deleted:
            response = 204
            if settings.NOTIFY_BUS:
                self._notify_bus(action="DELETE")
        else:
            msg = u"Instance ({0}) of class ({1}) in graph ({2}) was not found."
            error_message = msg.format(self.query_params["instance_uri"],
                                       self.query_params["class_uri"],
                                       self.query_params["graph_uri"])
            raise HTTPError(404, log_message=error_message)
        self.finalize(response)

    def finalize(self, response):
        if isinstance(response, dict):
            self.write(response)
            schema_url = build_schema_url_for_instance(self.query_params)
            header_value = content_type_profile(schema_url)
            self.set_header("Content-Type", header_value)
        elif isinstance(response, int):  # status code
            self.set_status(response)
            # A call to finalize() was removed from here! -- rodsenra 2013/04/25


class SuggestJsonSchemaHandler(BrainiakRequestHandler):

    def get(self):
        self.finalize(suggest_schema())


class SuggestHandler(BrainiakRequestHandler):

    @greenlet_asynchronous
    def post(self):
        valid_params = PAGING_PARAMS

        with safe_params(valid_params):

            try:
                raw_body_params = json.loads(self.request.body)
            except ValueError:
                error_message = "JSON malformed. Received: {0}."
                raise HTTPError(400, log_message=error_message.format(self.request.body))

            body_params = normalize_all_uris_recursively(raw_body_params)
            if '@context' in body_params:
                del body_params['@context']

            try:
                validate(body_params, SUGGEST_PARAM_SCHEMA)
            except ValidationError as ex:
                raise HTTPError(400, log_message=u"Invalid json parameter passed to suggest.\n {0:s}".format(ex))

            self.query_params = ParamDict(self, **valid_params)
            self.query_params.validate_required(self, valid_params)

        response = do_suggest(self.query_params, body_params)
        if self.query_params['expand_uri'] == "0":
            response = normalize_all_uris_recursively(response, mode=SHORTEN)
        self.finalize(response)

    def finalize(self, response):
        if response is None:
            msg = "There were no search results."
            raise HTTPError(404, log_message=msg)
        elif isinstance(response, dict):
            self.write(response)
            self.set_header("Content-Type", content_type_profile(build_schema_url(self.query_params)))
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
        raise HTTPError(404, log_message=u"The URL ({0}) is not recognized.".format(self.request.full_url()))

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
