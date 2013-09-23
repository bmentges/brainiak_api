# -*- coding: utf-8 -*-
from brainiak.utils.links import merge_schemas, pagination_schema


def schema(context_name, class_name, class_prefix):
    args = (context_name, class_name, class_prefix)
    if class_prefix is not None:
        schema_ref = "/{0}/{1}/_schema?class_prefix={2}".format(*args)
        href = "/{0}/{1}?class_prefix={2}".format(*args)
        link = "/{0}/{1}/{{resource_id}}?class_prefix={{class_prefix}}&instance_prefix={{instance_prefix}}".format(*args)
    else:
        schema_ref = '/{0}/{1}/_schema'.format(*args)
        href = '/{0}/{1}'.format(*args)
        link = "/{0}/{1}/{{resource_id}}?class_prefix={{class_prefix}}&instance_prefix={{instance_prefix}}".format(*args)

    base = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Collection Schema that lists instances",
        "type": "object",
        "required": ["items", "_class_prefix", "@id"],
        "properties": {
            "_class_prefix": {"type": "string"},
            "do_item_count": {"type": "integer"},
            "item_count": {"type": "integer"},
            "@id": {"type": "string", "format": "url"},
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "@id", "resource_id", "instance_prefix"],
                    "properties": {
                        "title": {"type": "string"},
                        "@id": {"type": "string"},
                        "resource_id": {"type": "string"},
                        "instance_prefix": {"type": "string", "format": "url"},
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
                "href": "{+_base_url}",
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

    base_pagination_url = '/{0}/{1}'.format(context_name, class_name)
    extra_url_params = '&class_prefix={_class_prefix}'
    pagination_dict = pagination_schema(base_pagination_url, extra_url_params)
    merge_schemas(base, pagination_dict)
    return base
