# -*- coding: utf-8 -*-
from brainiak.resources import SchemaResource, VersionResource, HealthcheckResource  # InstanceResource,

resources = [
    (r'/(?P<context_name>.+)/schemas/(?P<schema_name>.+)', SchemaResource),
#    (r'/(?P<context_name>.+)/collection/(?P<schema_name>.+)', InstanceResource),
    (r'/healthcheck', HealthcheckResource),
    (r'/version', VersionResource)
]
