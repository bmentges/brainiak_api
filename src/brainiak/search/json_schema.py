# -*- coding: utf-8 -*-
from brainiak.utils.links import merge_schemas, pagination_schema

SEARCH_PARAM_SCHEMA = {}


def schema():
    base = {}
    merge_schemas(base, pagination_schema('/', method="POST"))
    return base
