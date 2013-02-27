# -*- coding: utf-8 -*-
from brainiak.handlers import SchemaResource, VersionResource, \
    HealthcheckResource, VirtuosoStatusResource, InstanceResource

resources = [
    (r'/(?P<context_name>.+)/(?P<class_name>.+)/_schema', SchemaResource),
    (r'/(?P<context_name>.+)/(?P<class_name>.+)/(?P<instance_id>.+)', InstanceResource),
    (r'/healthcheck', HealthcheckResource),
    (r'/version', VersionResource),
    (r'/status/virtuoso', VirtuosoStatusResource)
]
