# -*- coding: utf-8 -*-
from brainiak import settings


class InvalidParam(Exception):
    pass


class ParamDict(dict):
    "Utility class to generate default params on demand and memoize results"
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        # preserve the order below, defaults come first to be overriden
        self._set_defaults()
        self.update(kw)

    def _set_defaults(self):
        "Define a set of predefined keys that "
        defaults = {}
        defaults["lang"] = self.get("context_name", "undefined")
        defaults["context_name"] = self.get("context_name", "invalid_context")
        defaults["class_name"] = self.get("class_name", "invalid_class")
        defaults["instance_id"] = self.get("instance_id", "invalid_instance")

        defaults["graph_prefix"] = settings.URI_PREFIX
        defaults["graph_uri"] = "{0}{1}/".format(defaults["graph_prefix"], defaults["context_name"])

        defaults["class_prefix"] = defaults.get("graph_uri")
        defaults["class_uri"] = "{0}{1}/".format(defaults["class_prefix"], defaults["class_name"])

        defaults["instance_prefix"] = defaults.get("class_uri")
        defaults["instance_uri"] = "{0}{1}".format(defaults["instance_prefix"], defaults["instance_id"])

        self.update(defaults)

    def override_with(self, request):
        "Override this dictionary with values whose keys are present in the request"
        for (query_param, default_value) in self.items():
            self[query_param] = request.get_argument(query_param, default_value)

        query_params_supported = set(self.keys())
        for arg in request.arguments:
            if arg not in query_params_supported:
                raise InvalidParam("Argument {0} is not supported".format(arg))

        self._post_override()

    def _post_override(self):
        "This method is called after override_with_arguments is called to do any post processing"
        if self["lang"] == "undefined":
            self["lang"] = ""  # empty string is False -> lang not set
