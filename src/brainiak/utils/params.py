# -*- coding: utf-8 -*-
from brainiak import settings


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

    def _set_defaults(self):
        "Define a set of predefined keys that "
        defaults = {}
        defaults["lang"] = self.get("lang", settings.DEFAULT_LANG)
        defaults["context_name"] = self.get("context_name", "invalid_context")
        defaults["class_name"] = self.get("class_name", "invalid_class")
        defaults["instance_id"] = self.get("instance_id", "invalid_instance")

        defaults["graph_prefix"] = settings.URI_PREFIX
        defaults["graph_uri"] = "{0}{1}/".format(defaults["graph_prefix"], defaults["context_name"])

        defaults["class_prefix"] = defaults.get("graph_uri")
        defaults["class_uri"] = "{0}{1}".format(defaults["class_prefix"], defaults["class_name"])

        defaults["instance_prefix"] = defaults.get("class_uri")
        defaults["instance_uri"] = "{0}{1}".format(defaults["instance_prefix"], defaults["instance_id"])

        self.update(defaults)

    def _override_with(self, handler):
        "Override this dictionary with values whose keys are present in the request"
        for (query_param, default_value) in self.items():
            self[query_param] = handler.get_argument(query_param, default_value)

        query_params_supported = set(self.keys())
        for arg in self['request'].arguments:
            if arg not in query_params_supported:
                raise InvalidParam(arg)

    def _post_override(self):
        "This method is called after override_with() is called to do any post processing"
        if self["lang"] == "undefined":
            self["lang"] = ""  # empty string is False -> lang not set

        # In order to keep up with Repos, pages numbering start at 1.
        # As for Virtuoso pages start at 0, we convert page, if provided
        if "page" in self['request'].arguments:
            self["page"] = str(int(self["page"]) - 1)
