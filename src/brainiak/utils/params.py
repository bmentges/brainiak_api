# -*- coding: utf-8 -*-
from brainiak import settings


class ParamDict(dict):
    "Utility class to generate default params on demand and memoize results"
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        # preserve the order below, defaults come first to be overriden
        self._set_defaults()
        self.update(kw)

    def _set_defaults(self):
        context_name = self.get("context_name", "invalid_context")
        class_name = self.get("class_name", "invalid_class")
        defaults = {}
        defaults["graph_prefix"] = settings.URI_PREFIX
        defaults["graph_uri"] = "{0}{1}/".format(defaults.get("graph_prefix"), context_name)
        defaults["class_prefix"] = defaults.get("graph_uri")
        defaults["class_uri"] = "{0}{1}/".format(defaults.get("class_prefix"), class_name)
        defaults["instance_prefix"] = defaults.get("class_uri")
        defaults["instance_uri"] = "{0}{1}".format(defaults.get("instance_prefix"), class_name)
        self.update(defaults)
