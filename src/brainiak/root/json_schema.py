# -*- coding: utf-8 -*-
from brainiak.settings import DEFAULT_PER_PAGE
from brainiak.utils.links import remove_last_slash


def schema(base_url):
    base_url = remove_last_slash(base_url)
    response = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Context List Schema",
        "type": "object",
        "required": ["items"],
        "properties": {
            "item_count": {"type": "integer"},
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
            "links": [
                {
                    "href": base_url,
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
                },
                {
                    "href": base_url,
                    "method": "GET",
                    "rel": "first",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "per_page": {
                                "type": "integer",
                                "minimum": 1,
                                "default": int(DEFAULT_PER_PAGE)
                            },
                            "page": {
                                "type": "integer",
                                "minimum": 1,
                            }
                        },
                        "required": ["page"]
                    }
                },
                {
                    "href": base_url,
                    "method": "GET",
                    "rel": "next",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "per_page": {
                                "type": "integer",
                                "minimum": 1,
                                "default": int(DEFAULT_PER_PAGE)
                            },
                            "page": {
                                "type": "integer",
                                "minimum": 1,
                            }
                        },
                        "required": ["page"]
                    }
                },

            ]
        }
    }
    return response
