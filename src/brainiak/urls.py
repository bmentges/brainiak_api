# -*- coding: utf-8 -*-
from brainiak.resources import HealthcheckResource, SchemaResource, VersionResource


resources = [
    (r'/(?P<context_name>.+)/schemas/(?P<schema_name>.+)', SchemaResource),
    (r'/healthcheck', HealthcheckResource),
    (r'/version', VersionResource)
]
