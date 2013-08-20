# -*- coding: utf-8 -*-
from brainiak.utils.links import merge_schemas, pagination_schema


def schema():
    base = {
        "$schema": "http://json-schema.org/draft-03/schema#",
        "title": "Context List Schema",
        "type": "object",
        "properties": {
            "do_item_count": {"type": "integer"},
            "item_count": {"type": "integer"},
            "base_url": {"type": "string", "format": "uri"},
            "items": {
                "type": "array",
                "required": True,
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "required": True},
                        "@id": {"type": "string", "required": True},
                        "resource_id": {"type": "string", "required": True}
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
                "href": "/_range_search",
                "method": "POST",
                "rel": "suggest",
                "schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "required": True,
                            "type": "string"
                        },
                        "predicate": {
                            "required": True,
                            "type": "string",
                            "format": "uri"
                        },
                        "search_fields": {
                            "required": False,
                            "type": "array",
                            "items": {
                                "type": "string",
                                "format": "uri"
                            }
                        },
                        "search_classes": {
                            "required": False,
                            "type": "array",
                            "items": {
                                "type": "string",
                                "format": "uri"
                            }
                        },
                        "search_graphs": {
                            "required": False,
                            "type": "array",
                            "items": {
                                "type": "string",
                                "format": "uri"
                            }
                        },
                    },
                }
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

    merge_schemas(base, pagination_schema('/'))
    return base
