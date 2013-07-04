# -*- coding: utf-8 -*-
from brainiak.utils.links import merge_schemas, pagination_schema


def schema(context_name):
    base = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Context Schema",
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
                    },
                    "links": [
                        {
                            "href": "/{0}/{{resource_id}}?class_prefix={{class_prefix}}".format(context_name),
                            "method": "GET",
                            "rel": "list"
                        },
                        {
                            "href": "/{0}/{{resource_id}}?class_prefix={{class_prefix}}".format(context_name),
                            "method": "GET",
                            "rel": "collection"
                        }
                    ]
                }
            },
        },
        "links": [
            {
                "href": "{+id}",
                "method": "GET",
                "rel": "self"
            }
        ]
    }

    merge_schemas(base, pagination_schema('/{0}/'.format(context_name)))
    return base
