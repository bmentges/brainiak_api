# -*- coding: utf-8 -*-
from brainiak.resources import HealthcheckResource, SchemaResource, VersionResource, VirtuosoStatusResource


resources = [
    (r'/healthcheck', HealthcheckResource),
    (r'/version', VersionResource),
    (r'/status/virtuoso', VirtuosoStatusResource),
    (r'/(?P<context_name>.+)/schemas/(?P<schema_name>.+)', SchemaResource)
]
