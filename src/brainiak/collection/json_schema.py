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


def schema(query_params):
    context_name = query_params['context_name']
    class_name = query_params['class_name']
    class_prefix = query_params.get('class_prefix', None)
    args = (context_name, class_name, class_prefix)

    if class_prefix is not None:
        schema_ref = u"/{0}/{1}/_schema?class_prefix={2}".format(*args)
        href = u"/{0}/{1}?class_prefix={2}".format(*args)
        link = u"/{0}/{1}/{{resource_id}}?class_prefix={{class_prefix}}&instance_prefix={{instance_prefix}}".format(*args)
    else:
        schema_ref = u'/{0}/{1}/_schema'.format(*args)
        href = u'/{0}/{1}'.format(*args)
        link = u"/{0}/{1}/{{resource_id}}?class_prefix={{class_prefix}}&instance_prefix={{instance_prefix}}".format(*args)

    base = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Collection Schema that lists instances",
        "type": "object",
        "required": ["items", "_class_prefix", "@id"],
        "properties": {
            "_class_prefix": {"type": "string"},
            "do_item_count": {"type": "integer"},
            "item_count": {"type": "integer"},
            "@id": {"type": "string", "format": "uri"},
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "@id", "resource_id", "instance_prefix"],
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
                        {
                            "href": "/_search?graph_uri={0}&class_uri={1}".format(query_params['graph_uri'],
                                                                                  query_params['class_uri']),
                            "method": "GET",
                            "rel": "search",
                            "schema": SEARCH_PARAM_SCHEMA
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
                "href": u"/{0}".format(context_name),
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

    base_pagination_url = u'/{0}/{1}'.format(context_name, class_name)
    extra_url_params = '&class_prefix={_class_prefix}'
    pagination_dict = pagination_schema(base_pagination_url, extra_url_params)
    merge_schemas(base, pagination_dict)
    return base
