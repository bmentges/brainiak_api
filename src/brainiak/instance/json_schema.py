# -*- coding: utf-8 -*-
from brainiak.utils.links import merge_schemas, pagination_schema


def schema(context_name, class_name, class_prefix):
    vars = (context_name, class_name, class_prefix)
    if class_prefix is not None:
        schema_ref = "/{0}/{1}/_schema?class_prefix={2}".format(*vars)
        href = "/{0}/{1}?class_prefix={2}".format(*vars)
        link = "/{0}/{1}/{{resource_id}}?class_prefix={2}&instance_prefix={{instance_prefix}}".format(*vars)
    else:
        schema_ref = '/{0}/{1}/_schema'.format(*vars)
        href = '/{0}/{1}'.format(*vars)
        link = "/{0}/{1}/{{resource_id}}?instance_prefix={{instance_prefix}}".format(*vars)

    base = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Collection Schema",
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
                    },
                    "links": [
                        {
                            "href": link,
                            "method": "GET",
                            "rel": "item"
                        },
                        {
                            "href": link,
                            "method": "GET",
                            "rel": "instance"
                        },
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
            },
            {
                "href": "/{0}".format(context_name),
                "method": "GET",
                "rel": "context"
            },
            {
                "href": href,
                "method": "POST",
                "rel": "add",
                "schema": {"$ref": schema_ref}
            }
        ]
    }

    merge_schemas(base, pagination_schema('/{0}/{1}'.format(context_name, class_name)))
    return base
