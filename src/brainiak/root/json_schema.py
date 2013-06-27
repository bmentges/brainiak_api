# -*- coding: utf-8 -*-
from brainiak.utils.links import remove_class_slash, merge_schemas, pagination_schema


def schema(base_url):
    base_url = remove_class_slash(base_url)
    base = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Context List Schema",
        "type": "object",
        "required": ["items"],
        "properties": {
            "item_count": {"type": "integer"},
            "@id": {"type": "string", "format": "uri"},
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
                "href": "{@id}",
                "method": "GET",
                "rel": "self"
            },
            {
                "href": base_url + "/{resource_id}",
                "method": "GET",
                "rel": "list"
            },
            {
                "href": base_url + "/{resource_id}",
                "method": "GET",
                "rel": "context"
            }

        ]
    }

    merge_schemas(base, pagination_schema(base_url))
    return base
