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
            {'href': '{+_base_url}', 'method': 'GET', 'rel': 'self'},
            {'href': '/?page=1&per_page={per_page}&do_item_count={do_item_count}', 'method': 'GET', 'rel': 'first'},
            {
                'href': '/?page={last_page}&per_page={per_page}&do_item_count={do_item_count}',
                'method': 'GET',
                'rel': 'last'
            },
            {
                'href': '/?page={next_page}&per_page={per_page}&do_item_count={do_item_count}',
                'method': 'GET',
                'rel': 'next'
            },
            {
                'href': '/?page={previous_page}&per_page={per_page}&do_item_count={do_item_count}',
                'method': 'GET',
                'rel': 'previous'
            },
            {
                'href': '/{{context_id}}/{{collection_id}}',
                'method': 'GET',
                'rel': 'collection',
                'schema': {'properties': {'class_prefix': {'type': 'string'}}, 'type': 'object'}
            },
            {
                'href': '/{{context_id}}/{{collection_id}}/{{resource_id}}',
                'method': 'GET',
                'rel': 'instance',
                'schema': {
                    'properties':
                        {
                            'class_prefix': {'type': 'string'},
                            'instance_prefix': {'type': 'string'}
                        },
                    'type': 'object'
                }
            }
        ]
        self.assertEqual(sorted(computed_schema["links"]), sorted(expected_links))
