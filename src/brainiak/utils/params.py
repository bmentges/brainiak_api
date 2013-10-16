# -*- coding: utf-8 -*-
from copy import copy
from urllib import urlencode
from urlparse import unquote, parse_qs

from tornado.web import HTTPError

from brainiak import settings
from brainiak.prefixes import expand_uri, safe_slug_to_prefix, extract_prefix
from brainiak.utils.sparql import PATTERN_O, PATTERN_P
from brainiak.utils.config_parser import ConfigParserNoSectionError, parse_section


class InvalidParam(Exception):
    pass


class RequiredParamMissing(Exception):
    pass


class DefaultParamsDict(dict):

    def __init__(self, **kw):
        dict.__init__(self, **kw)
        self.required = []

    def set_required(self, required):
        self.required = list(set(required))

    def __add__(self, other):
        new_dict = DefaultParamsDict()
        new_dict.update(self)
        new_dict.update(other)
        new_dict.set_required(self.required + other.required)
        return new_dict


class RequiredParamsDict(DefaultParamsDict):
    "Class used to easily mark required parameters"
    def __init__(self, **kw):
        DefaultParamsDict.__init__(self, **kw)
        self.set_required(kw.keys())


def optionals(*args):
    """Build an instance of DefaultParamsDict from a list of parameter names"""
    result = {key: None for key in args}
    return DefaultParamsDict(**result)

# The parameters below as given to ParamDict with other keyword arguments,
# but they are not URL arguments because they are part of the URL path

DEFAULT_PARAMS = optionals('lang', 'graph_uri', 'expand_uri')

NON_ARGUMENT_PARAMS = ('context_name', 'class_name', 'instance_id')

CACHE_PARAMS = DefaultParamsDict(purge="0")

PAGING_PARAMS = DefaultParamsDict(page=settings.DEFAULT_PAGE,
                                  per_page=settings.DEFAULT_PER_PAGE,
                                  do_item_count="0")

LIST_PARAMS = PAGING_PARAMS + DefaultParamsDict(sort_by="",
                                                sort_order="ASC",
                                                sort_include_empty="1")

INSTANCE_PARAMS = optionals('graph_uri', 'class_prefix', 'class_uri', 'instance_prefix', 'instance_uri', 'expand_object_properties', 'meta_properties')

CLASS_PARAMS = optionals('graph_uri', 'class_prefix', 'class_uri')

GRAPH_PARAMS = optionals('graph_uri')


def normalize_last_slash(url):
    return url if url.endswith("/") else url + "/"


# Define possible params and their processing order
VALID_PARAMS = [
    'lang',
    'expand_uri',
    'graph_uri',
    'context_name', 'class_name', 'class_prefix', 'class_uri',
    'instance_id', 'instance_prefix', 'instance_uri',
    'page', 'per_page',
    'sort_by', 'sort_order', 'sort_include_empty',
    'purge',
    'do_item_count',
    'direct_instances_only',
    'expand_object_properties',
    'meta_properties'
]

VALID_PATTERNS = (
    PATTERN_P,
    PATTERN_O
)


class ParamDict(dict):
    "Utility class to generate default params on demand and memoize results"

    def __init__(self, handler, **kw):
        dict.__init__(self)
        # preserve the order below, defaults are overriden first
        request = self["request"] = handler.request

        self.triplestore_config = None
        self._set_triplestore_config(request)

        self.arguments = self._make_arguments_dict(handler)

        # preserve the specified optional parameters
        self.optionals = copy(kw)

        self.base_url = "{0}://{1}{2}".format(request.protocol, request.host, normalize_last_slash(request.path))
        self.resource_url = self.base_url + "{resource_id}"

        # Set params with value None first, just to mark them as valid parameters
        for key in [k for k, v in self.optionals.items() if v is None]:
            dict.__setitem__(self, key, None)

        self._set_defaults()

        # Update optionals in the appropriate order
        # Overriding default values if the override value is not None
        for key in VALID_PARAMS:
            if key in self.optionals:
                value = self.optionals[key]
                if value is not None:
                    # the value None is used as a flag to avoid override the default value
                    self[key] = self.optionals[key]
                del kw[key]  # I have consumed this item, remove it to check for invalid params

        # TODO: test
        unprocessed_keys = kw.keys()
        for key in unprocessed_keys:
            if self._matches_dynamic_pattern(key):
                value = self.optionals[key]
                if value is not None:
                    # the value None is used as a flag to avoid override the default value
                    self[key] = self.optionals[key]
                del kw[key]

        if kw:
            raise InvalidParam(kw.popitem()[0])

        # Override params with arguments passed in the handler's request object
        self._override_with(handler)
        self._post_override()

    def _make_arguments_dict(self, handler):
        query_string = unquote(self["request"].query)
        query_dict = parse_qs(query_string, keep_blank_values=True)
        return {key: handler.get_argument(key) for key in query_dict}

    def _set_triplestore_config(self, request):
        auth_client_id = request.headers.get('X-Brainiak-Client-Id', 'default')
        try:
            self.triplestore_config = parse_section(section=auth_client_id)
        except ConfigParserNoSectionError:
            raise HTTPError(404, u"Client-Id provided at 'X-Brainiak-Client-Id' ({0}) is not known".format(auth_client_id))

    def __setitem__(self, key, value):
        """Process collateral effects in params that are related.
        Changes in *_prefix should reflect in *_uri.
        """
        if key == 'graph_uri':
            dict.__setitem__(self, key, safe_slug_to_prefix(value))

        elif key == 'class_uri':
            dict.__setitem__(self, key, expand_uri(value))

        elif key == "context_name":
            dict.__setitem__(self, key, value)
            uri = safe_slug_to_prefix(value)
            dict.__setitem__(self, "graph_uri", uri)
            dict.__setitem__(self, "class_prefix", uri)

        elif key == "class_name":
            dict.__setitem__(self, key, value)
            class_prefix = self["class_prefix"]
            if not class_prefix.endswith('/'):
                class_prefix += "/"
            dict.__setitem__(self, "class_uri", "{0}{1}".format(class_prefix, self["class_name"]))

        elif key == "instance_id":
            dict.__setitem__(self, key, value)
            dict.__setitem__(self, "instance_uri", u"{0}{1}/{2}".format(self["class_prefix"], self["class_name"], self["instance_id"]))
            dict.__setitem__(self, "instance_prefix", extract_prefix(self["instance_uri"]))

        elif key == "class_prefix":
            dict.__setitem__(self, key, safe_slug_to_prefix(value))
            dict.__setitem__(self, "class_uri", u"{0}{1}".format(self["class_prefix"], self["class_name"]))

        elif key == "instance_prefix":
            dict.__setitem__(self, key, safe_slug_to_prefix(value))
            dict.__setitem__(self, "instance_uri", u"{0}{1}".format(self["instance_prefix"], self["instance_id"]))

        elif key == "instance_uri":
            dict.__setitem__(self, key, value)
            dict.__setitem__(self, "instance_prefix", extract_prefix(value))

        else:
            dict.__setitem__(self, key, value)

    # FIXME: test
    def _set_if_optional(self, key, value):
        if (key in self.optionals) and (value is not None):
            self[key] = value

    def _set_defaults(self):
        """Define a set of predefined keys"""
        self["lang"] = self.optionals.get("lang", settings.DEFAULT_LANG)

        self._set_if_optional("context_name", self.optionals.get("context_name", "invalid_context"))
        self._set_if_optional("class_name", self.optionals.get("class_name", "invalid_class"))
        self._set_if_optional("instance_id", self.optionals.get("instance_id", "invalid_instance"))

        self["expand_uri"] = self.optionals.get("expand_uri", settings.DEFAULT_URI_EXPANSION)

        # if the context name is defined, the graph_uri should follow it by default, but it can be overriden
        if "context_name" in self:
            self["graph_uri"] = safe_slug_to_prefix(self.optionals["context_name"])

        self._set_if_optional("class_prefix", self.optionals.get("graph_uri", ''))

        class_uri = self.optionals.get("class_uri")
        if class_uri is not None:
            self._set_if_optional("instance_prefix", class_uri + "/")

    def _matches_dynamic_pattern(self, key):
        return any([pattern.match(key) for pattern in VALID_PATTERNS])

    def _override_with(self, handler):
        "Override this dictionary with values whose keys are present in the request"
        # order is critical below because *_uri should be set before *_prefix
        for key in self.arguments:
            if (key not in self) and (not self._matches_dynamic_pattern(key)):
                raise InvalidParam(key)

            value = self.arguments.get(key, None)
            if value is not None:

                self[key] = value

    def _post_override(self):
        "This method is called after override_with() is called to do any post processing"
        if self.get("lang", '') == "undefined":
            self["lang"] = ""  # empty string is False -> lang not set

        # In order to keep up with Repos, pages numbering start at 1.
        # As for Virtuoso pages start at 0, we convert page, if provided
        if "page" in self.arguments:
            self["page"] = unicode(int(self["page"]) - 1)

        if "sort_order" in self.arguments:
            self["sort_order"] = self["sort_order"].upper()

    def format_url_params(self, exclude_keys=None, **kw):
        if exclude_keys is None:
            exclude_keys = NON_ARGUMENT_PARAMS
        else:
            exclude_keys.extend(NON_ARGUMENT_PARAMS)

        effective_args = {}
        for key in VALID_PARAMS:
            if key in self.arguments and key not in exclude_keys:
                value = self[key]
                if value:
                    effective_args[key] = value

        effective_args.update(kw)
        return urlencode(effective_args, doseq=True)

    def validate_required(self, handler, required_spec):
        "Check if all required params specified by required_spec are indeed present in the request"
        arguments = self._make_arguments_dict(handler).keys()
        for required_param in required_spec.required:
            if not required_param in arguments:
                raise RequiredParamMissing(required_param)
