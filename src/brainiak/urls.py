# -*- coding: utf-8 -*-
from brainiak.resources import SchemaResource, InstanceResource, VersionResource, HealthcheckResource, VirtuosoStatusResource

resources = [
    (r'/(?P<context_name>.+)/schemas/(?P<schema_name>.+)', SchemaResource),
    (r'/(?P<context_name>.+)/collection/(?P<schema_name>.+)', InstanceResource),

    (r'/healthcheck', HealthcheckResource),
    (r'/version', VersionResource),
    (r'/status/virtuoso', VirtuosoStatusResource),
    (r'/(?P<context_name>.+)/schemas/(?P<schema_name>.+)', SchemaResource)
]
