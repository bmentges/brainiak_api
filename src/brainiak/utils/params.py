# -*- coding: utf-8 -*-
from urllib import urlencode
from brainiak import settings
from brainiak.prefixes import safe_slug_to_prefix, ROOT_CONTEXT


class InvalidParam(Exception):
    pass


class DefaultParamsDict(dict):
    def __add__(self, other):
        new_dict = {}
        new_dict.update(self)
        new_dict.update(other)
        return new_dict

FILTER_PARAMS = DefaultParamsDict(p="?predicate", o="?object")

LIST_PARAMS = DefaultParamsDict(page=settings.DEFAULT_PAGE,
                                per_page=settings.DEFAULT_PER_PAGE,
                                sort_by="",
                                sort_order="ASC",
                                sort_include_empty="1")


def normalize_last_slash(url):
    return url if url.endswith("/") else url + "/"


class ParamDict(dict):
    "Utility class to generate default params on demand and memoize results"
    extra_params = {}
    essential_params = ('graph_prefix', 'class_prefix', 'instance_prefix', 'graph_uri', 'class_uri', 'instance_uri', 'lang')

    def __init__(self, handler, *args, **kw):
        dict.__init__(self, *args, **kw)
        # preserve the order below, defaults come first to be overriden
        request = self["request"] = handler.request
        self.base_url = "{0}://{1}{2}".format(request.protocol, request.host, normalize_last_slash(request.path))
        self.resource_url = self.base_url + "{resource_id}"

        self._set_defaults()
        # Add to the mix the default params customized at class level
        self.update(self.extra_params)
        # Add to the mix the arguments given to the initializer
        self.update(kw)
        # Override params with arguments passed in the handler's request object
        self._override_with(handler)
        self._post_override()

    def args(self, **kw):
        effective_args = {}
        effective_args.update(kw)
        for key in ParamDict.essential_params:
            if key in self["request"].arguments:
                effective_args[key] = self[key]
        return urlencode(effective_args, doseq=True)

    def __setitem__(self, key, value):
        """Process collateral effects in params that are related.
        Changes in *_prefix should reflect in *_uri.
        """
        if key in ('graph_uri', 'class_uri'):
            dict.__setitem__(self, key, safe_slug_to_prefix(value))

        elif key == "graph_prefix":
            dict.__setitem__(self, key, safe_slug_to_prefix(value))
            if self["context_name"] != ROOT_CONTEXT:
                dict.__setitem__(self, "graph_uri", "{0}{1}/".format(self["graph_prefix"], self["context_name"]))
            else:
                dict.__setitem__(self, "graph_uri", settings.URI_PREFIX)

        elif key == "class_prefix":
            dict.__setitem__(self, key, safe_slug_to_prefix(value))
            dict.__setitem__(self, "class_uri", "{0}{1}".format(self["class_prefix"], self["class_name"]))

        elif key == "instance_prefix":
            dict.__setitem__(self, key, safe_slug_to_prefix(value))
            dict.__setitem__(self, "instance_uri", "{0}{1}".format(self["instance_prefix"], self["instance_id"]))

        else:
            dict.__setitem__(self, key, value)

    def _set_defaults(self):
        "Define a set of predefined keys that "
        self["lang"] = self.get("lang", settings.DEFAULT_LANG)
        self["context_name"] = self.get("context_name", "invalid_context")
        self["class_name"] = self.get("class_name", "invalid_class")
        self["instance_id"] = self.get("instance_id", "invalid_instance")

        self["graph_prefix"] = settings.URI_PREFIX
        self["class_prefix"] = self.get("graph_uri")
        self["instance_prefix"] = self.get("class_uri") + "/"

    def _override_with(self, handler):
        "Override this dictionary with values whose keys are present in the request"
        query_params_supported = set(self.keys())
        for arg in self['request'].arguments:
            if arg not in query_params_supported:
                raise InvalidParam(arg)

        # sorted is critical below because *_uri should be set before *_prefix
        for query_param_to_override in reversed(sorted(self['request'].arguments)):
            self[query_param_to_override] = handler.get_argument(query_param_to_override)

    def _post_override(self):
        "This method is called after override_with() is called to do any post processing"
        if self["lang"] == "undefined":
            self["lang"] = ""  # empty string is False -> lang not set

        # In order to keep up with Repos, pages numbering start at 1.
        # As for Virtuoso pages start at 0, we convert page, if provided
        if "page" in self['request'].arguments:
            self["page"] = str(int(self["page"]) - 1)

        if "sort_order" in self['request'].arguments:
            self["sort_order"] = self["sort_order"].upper()
