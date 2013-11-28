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


def schema(context_name, class_name):
    schema_ref = u"/{0}/{1}/_schema?class_prefix={{_class_prefix}}".format(context_name, class_name)
    href = u"/{0}/{1}/?class_prefix={{_class_prefix}}".format(context_name, class_name)
    link = u"/{0}/{1}/_?instance_uri={{id}}".format(context_name, class_name)
    search_url = "/{0}/{1}/_search?graph_uri={{_graph_uri}}&class_uri={{_class_uri}}&pattern={{pattern}}"

    base = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "",
        "type": "object",
        "required": ["items", "_class_prefix", "@id"],
        "properties": {
            "pattern": {"type": "string"},  # used in _search service responses
            "_graph_uri": {"type": "string"},  # used in _search service responses
            "_context_name": {"type": "string"},  # used in _search service responses
            "_class_name": {"type": "string"},  # used in _search service responses
            "_class_prefix": {"type": "string"},  # used in _search service responses
            "_class_uri": {"type": "string"},  # used in _search service responses
            "do_item_count": {"type": "integer"},
            "item_count": {"type": "integer"},
            "@id": {"type": "string", "format": "uri"},
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "id", "resource_id", "instance_prefix"],
                    "properties": {
                        "title": {"type": "string"},
                        "id": {"type": "string"},
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
                        }
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
            },
            {
                "href": search_url.format(context_name, class_name),
                "method": "GET",
                "rel": "search",
                "schema": SEARCH_PARAM_SCHEMA
            },
            {
                "href": href,
                "method": "GET",
                "rel": "list"
            },
            {
                "href": href,
                "method": "GET",
                "rel": "collection"
            }

        ]
    }

    base_pagination_url = u'/{0}/{1}/_search'.format(context_name, class_name)
    extra_url_params = '&graph_uri={_graph_uri}&class_uri={_class_uri}'
    pagination_dict = pagination_schema(base_pagination_url, extra_url_params)
    merge_schemas(base, pagination_dict)
    return base
