# -*- coding: utf-8 -*-
from brainiak.utils.links import merge_schemas, pagination_schema


def schema(context_name, class_name):
    vars = (context_name, class_name)
    base = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Instance List Schema",
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
                        "resource_id": {"type": "string"},
                        "instance_prefix": {"type": "string", "format": "uri"},
                        "class_prefix": {"type": "string", "format": "uri"},
                    },
                    "links": [
                        {
                            "href": "/{0}/{1}/{{resource_id}}?class_prefix={{class_prefix}}&instance_prefix={{instance_prefix}}".format(*vars),
                            "method": "GET",
                            "rel": "item"
                        },
                        {
                            "href": "/{0}/{1}/{{resource_id}}?class_prefix={{class_prefix}}&instance_prefix={{instance_prefix}}".format(*vars),
                            "method": "GET",
                            "rel": "instance"
                        },
                        {   "href": "/{0}/{1}/{{resource_id}}?class_prefix={{_class_prefix}}".format(*vars),
                            "method": "POST",
                            "rel": "add",
                            "schema": {"$ref": "/{0}/{1}/{{resource_id}}/_schema?class_prefix={{_class_prefix}}".format(*vars)}
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
            },
            {
                "href": "{+_schema_url}",
                "method": "GET",
                "rel": "class"
            }
        ]
    }

    merge_schemas(base, pagination_schema('/{0}/'.format(context_name)))
    return base
