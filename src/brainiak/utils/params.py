# -*- coding: utf-8 -*-
from brainiak import settings
from brainiak.prefixes import safe_slug_to_prefix


class InvalidParam(Exception):
    pass


class DefaultParamsDict(dict):
    def __add__(self, other):
        self.update(other)
        return self

LIST_PARAMS = DefaultParamsDict(page=settings.DEFAULT_PAGE,
                                per_page=settings.DEFAULT_PER_PAGE)

FILTER_PARAMS = DefaultParamsDict(p="?predicate", o="?object")


class ParamDict(dict):
    "Utility class to generate default params on demand and memoize results"
    extra_params = {}

    def __init__(self, handler, *args, **kw):
        dict.__init__(self, *args, **kw)
        # preserve the order below, defaults come first to be overriden
        self["request"] = handler.request
        self._set_defaults()
        # Add to the mix the default params customized at class level
        self.update(self.extra_params)
        # Add to the mix the arguments given to the initializer
        self.update(kw)
        # Override params with arguments passed in the handler's request object
        self._override_with(handler)
        self._post_override()

    def __setitem__(self, key, value):
        "Process collateral effects in params that are related."
        if key == "graph_prefix":
            dict.__setitem__(self, key, safe_slug_to_prefix(value))
            dict.__setitem__(self, "graph_uri", "{0}{1}/".format(self["graph_prefix"], self["context_name"]))

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
