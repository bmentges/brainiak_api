# -*- coding: utf-8 -*-
from brainiak.resources import SchemaResource, VersionResource, HealthcheckResource, VirtuosoStatusResource  # InstanceResource

resources = [
    (r'/(?P<context_name>.+)/(?P<class_name>.+)/_schema', SchemaResource),
#    (r'/(?P<context_name>.+)/collection/(?P<schema_name>.+)', InstanceResource),
    (r'/healthcheck', HealthcheckResource),
    (r'/version', VersionResource),
    (r'/status/virtuoso', VirtuosoStatusResource)
]
