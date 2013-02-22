# -*- coding: utf-8 -*-
from brainiak.resources import SchemaResource

resources = [
    (r'/(?P<context_name>.+)/schemas/(?P<schema_name>.+)', SchemaResource)
]
