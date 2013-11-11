# -*- coding: utf-8 -*-
from brainiak.utils.links import merge_schemas, pagination_schema

SEARCH_PARAM_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "Describe the parameters given to the search primitive",
    "type": "object",
    "required": ["pattern"],
    "additionalProperties": False,
    "properties": {
        "pattern": {"type": "string"},
    }
}


def schema():
    base = {}
    merge_schemas(base, pagination_schema('/', method="POST"))
    return base
