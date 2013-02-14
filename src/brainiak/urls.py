# -*- coding: utf-8 -*-
from brainiak.resources import SchemaResource

resources = [
    (r'/contexts/(?P<context_name>.+)/schemas/(?P<schema_name>.+)', SchemaResource)
]
