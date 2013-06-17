# -*- coding: utf-8 -*-
from urllib import urlencode
from copy import copy
from brainiak import settings
from brainiak.prefixes import safe_slug_to_prefix


class InvalidParam(Exception):
    pass


class DefaultParamsDict(dict):
    def __add__(self, other):
        new_dict = DefaultParamsDict()
        new_dict.update(self)
        new_dict.update(other)
        return new_dict


def optionals(*args):
    """Build an instance of DefaultParamsDict from a list of parameter names"""
    result = {key: None for key in args}
    return DefaultParamsDict(**result)

# The parameters below as given to ParamDict with other keyword arguments,
# but they are not URL arguments because they are part of the URL path
NON_ARGUMENT_PARAMS = ('context_name', 'class_name', 'instance_id')

CACHE_PARAMS = DefaultParamsDict(purge="1")

FILTER_PARAMS = DefaultParamsDict(p="?predicate", o="?object")

LIST_PARAMS = DefaultParamsDict(page=settings.DEFAULT_PAGE,
                                per_page=settings.DEFAULT_PER_PAGE,
                                sort_by="",
                                sort_order="ASC",
                                sort_include_empty="1")

INSTANCE_PARAMS = optionals('graph_uri', 'class_prefix', 'class_uri', 'instance_prefix', 'instance_uri')

CLASS_PARAMS = optionals('graph_uri', 'class_prefix', 'class_uri')

GRAPH_PARAMS = optionals('graph_uri')


def normalize_last_slash(url):
    return url if url.endswith("/") else url + "/"


def valid_pagination(total, page, per_page):
    "Verify if the given pagination is valid to the existent total items"
    return (page * per_page) < total


# Define possible params and their processing order
VALID_PARAMS = ('lang',
                'graph_uri',
                'context_name', 'class_name', 'class_prefix', 'class_uri',
                'instance_id', 'instance_prefix', 'instance_uri',
                'page', 'per_page',
                'sort_by', 'sort_order', 'sort_include_empty',
                'p', 'o')


class ParamDict(dict):
    "Utility class to generate default params on demand and memoize results"

    def __init__(self, handler, **kw):
        dict.__init__(self)
        # preserve the order below, defaults come first to be overriden
        request = self["request"] = handler.request

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
        if kw:
            raise InvalidParam(kw.popitem()[0])

        # Override params with arguments passed in the handler's request object
        self._override_with(handler)
        self._post_override()

    def args(self, exclude_keys=None, **kw):
        if exclude_keys is None:
            exclude_keys = NON_ARGUMENT_PARAMS
        else:
            exclude_keys = []
            exclude_keys.extends(NON_ARGUMENT_PARAMS)

        effective_args = {}
        for key in VALID_PARAMS:
            if key in self["request"].arguments and key not in exclude_keys:
                value = self[key]
                if value:
                    effective_args[key] = value

        effective_args.update(kw)
        return urlencode(effective_args, doseq=True)

    def __setitem__(self, key, value):
        """Process collateral effects in params that are related.
        Changes in *_prefix should reflect in *_uri.
        """
        if key in ('graph_uri', 'class_uri'):
            dict.__setitem__(self, key, safe_slug_to_prefix(value))

        elif key == "context_name":
            dict.__setitem__(self, key, value)
            uri = safe_slug_to_prefix(value)
            dict.__setitem__(self, "graph_uri", uri)
            dict.__setitem__(self, "class_prefix", uri)

        elif key == "class_name":
            dict.__setitem__(self, key, value)
            dict.__setitem__(self, "class_uri", "{0}{1}".format(self["class_prefix"], self["class_name"]))

        elif key == "instance_id":
            dict.__setitem__(self, key, value)
            dict.__setitem__(self, "instance_uri", "{0}{1}/{2}".format(self["class_prefix"], self["class_name"], self["instance_id"]))

        elif key == "class_prefix":
            dict.__setitem__(self, key, safe_slug_to_prefix(value))
            dict.__setitem__(self, "class_uri", "{0}{1}".format(self["class_prefix"], self["class_name"]))

        elif key == "instance_prefix":
            dict.__setitem__(self, key, safe_slug_to_prefix(value))
            dict.__setitem__(self, "instance_uri", "{0}{1}".format(self["instance_prefix"], self["instance_id"]))

        else:
            dict.__setitem__(self, key, value)

    # FIXME: test
    def _set_if_optional(self, key, value):
        if (key in self.optionals) and (value is not None):
            self[key] = value

    def _set_defaults(self):
        "Define a set of predefined keys that "
        self["lang"] = self.optionals.get("lang", settings.DEFAULT_LANG)

        self._set_if_optional("context_name", self.optionals.get("context_name", "invalid_context"))
        self._set_if_optional("class_name", self.optionals.get("class_name", "invalid_class"))
        self._set_if_optional("instance_id", self.optionals.get("instance_id", "invalid_instance"))

        # if the context name is defined, the graph_uri should follow it by default, but it can be overriden
        if "context_name" in self:
            self["graph_uri"] = safe_slug_to_prefix(self.optionals["context_name"])

        self._set_if_optional("class_prefix", self.optionals.get("graph_uri", ''))

        class_uri = self.optionals.get("class_uri", "")
        if class_uri is not None:
            self._set_if_optional("instance_prefix", class_uri + "/")

    def _override_with(self, handler):
        "Override this dictionary with values whose keys are present in the request"
        for arg in self['request'].arguments:
            if arg not in self:
                raise InvalidParam(arg)

        # order is critical below because *_uri should be set before *_prefix
        for key in VALID_PARAMS:
            if key in self["request"].arguments:
                value = handler.get_argument(key)
                if value is not None:
                    self[key] = value

    def _post_override(self):
        "This method is called after override_with() is called to do any post processing"
        if self.get("lang", '') == "undefined":
            self["lang"] = ""  # empty string is False -> lang not set

        # In order to keep up with Repos, pages numbering start at 1.
        # As for Virtuoso pages start at 0, we convert page, if provided
        if "page" in self['request'].arguments:
            self["page"] = str(int(self["page"]) - 1)

        if "sort_order" in self['request'].arguments:
            self["sort_order"] = self["sort_order"].upper()
