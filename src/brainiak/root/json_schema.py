# -*- coding: utf-8 -*-
from brainiak.utils.links import merge_schemas, pagination_schema


def schema():
    base = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Context List Schema",
        "type": "object",
        "required": ["items"],
        "properties": {
            "do_item_count": {"type": "integer"},
            "item_count": {"type": "integer"},
            "id": {"type": "string", "format": "uri"},
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["@id", "title", "resource_id"],
                    "properties": {
                        "title": {"type": "string"},
                        "@id": {"type": "string"},
                        "resource_id": {"type": "string"}
                    }
                }
            },
        },
        "links": [
            {
                "href": "{+id}",
                "method": "GET",
                "rel": "self"
            },
            {
                "href": "/{resource_id}",
                "method": "GET",
                "rel": "list"
            },
            {
                "href": "/{resource_id}",
                "method": "GET",
                "rel": "context"
            }

        ]
    }

    merge_schemas(base, pagination_schema())
    return base
