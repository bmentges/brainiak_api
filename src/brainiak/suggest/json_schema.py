# -*- coding: utf-8 -*-
from brainiak.suggest.suggest import SUGGEST_PARAM_SCHEMA
from brainiak.utils.links import merge_schemas, pagination_schema


def schema():
    base = {
        "$schema": "http://json-schema.org/draft-03/schema#",
        "title": "Suggest Result List Schema",
        "type": "object",
        "properties": {
            #"do_item_count": {"type": "integer"},
            #"item_count": {"type": "integer"},
            "base_url": {"type": "string", "format": "uri"},
            "items": {
                "type": "array",
                "required": True,
                "items": {
                    "type": "object",
                    "properties": {
                        "@id": {"type": "string", "required": True},
                        "title": {"type": "string", "required": True},
                        "@type": {"type": "string", "required": True},
                        "type_title": {"type": "string", "required": True},
                        "class_fields": {"type": "object"},
                        "instance_fields": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "predicate_id": {"type": "string", "required": True},
                                    "predicate_title": {"type": "string", "required": True},
                                    "object_id": {"type": "string", "required": False},
                                    "object_title": {"type": "string", "required": True},
                                    "required": {"type": "boolean", "required": True}
                                }
                            },
                        }
                    },
                    "links": [
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
            },
        },
        "links": [
            {
                "href": "{+_base_url}",
                "method": "GET",
                "rel": "self"
            },
            {
                "href": "/_suggest",
                "method": "POST",
                "rel": "suggest",
                "schema": SUGGEST_PARAM_SCHEMA
            },
            {
                "href": "/{{context_id}}/{{collection_id}}",
                "method": "GET",
                "rel": "collection",
                "schema": {
                    "type": "object",
                    "properties": {
                        "class_prefix": {
                            "type": "string"
                        }
                    },
                }
            },
            {
                "href": "/{{context_id}}/{{collection_id}}/{{resource_id}}",
                "method": "GET",
                "rel": "instance",
                "schema": {
                    "type": "object",
                    "properties": {
                        "class_prefix": {
                            "type": "string"
                        },
                        "instance_prefix": {
                            "type": "string"
                        },
                    },
                }

            }
        ]
    }

    merge_schemas(base, pagination_schema('/', method="POST"))
    return base
