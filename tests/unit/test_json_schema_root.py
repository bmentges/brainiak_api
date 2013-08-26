# -*- coding: utf-8 -*-

import unittest
from brainiak.root.json_schema import schema as root_schema


class TestRootJsonSchema(unittest.TestCase):

    maxDiff = None

    def test_valid_structure(self):
        computed_schema = root_schema()
        self.assertEqual(type(computed_schema), dict)

    def test_list_contexts(self):
        computed_schema = root_schema()
        expected_links = [
            {'href': '?{+_first_args}', 'method': 'GET', 'rel': 'first'},
            {'href': '?{+_last_args}', 'method': 'GET', 'rel': 'last'},
            {'href': '?{+_next_args}', 'method': 'GET', 'rel': 'next'},
            {'href': '?{+_previous_args}', 'method': 'GET', 'rel': 'previous'},
            {'href': '{+_base_url}', 'method': 'GET', 'rel': 'self'},
            {
                'href': '/_range_search',
                'method': 'POST',
                'rel': 'suggest',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'pattern': {'required': True, 'type': 'string'},
                        'predicate': {'format': 'uri',
                                      'required': True,
                                      'type': 'string'},
                        'search_classes': {'items': {'format': 'uri', 'type': 'string'},
                                           'required': False,
                                           'type': 'array'},
                        'search_fields': {'items': {'format': 'uri', 'type': 'string'},
                                          'required': False,
                                          'type': 'array'},
                        'search_graphs': {'items': {'format': 'uri', 'type': 'string'},
                                          'required': False,
                                          'type': 'array'}

                    }
                }
            },
            {
                'href': '/{{context_id}}/{{collection_id}}',
                'method': 'GET',
                'rel': 'collection',
                'schema': {
                    'properties': {
                        'class_prefix': {'type': 'string'}
                    },
                    'type': 'object'}
            },
            {
                'href': '/{{context_id}}/{{collection_id}}/{{resource_id}}',
                'method': 'GET',
                'rel': 'instance',
                'schema': {
                    'properties': {
                        'class_prefix': {'type': 'string'},
                        'instance_prefix': {'type': 'string'}
                    },
                    'type': 'object'
                }
            }
        ]

        self.assertEqual(sorted(computed_schema["links"]), sorted(expected_links))
