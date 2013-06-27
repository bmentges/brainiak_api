# -*- coding: utf-8 -*-

import unittest
from brainiak.root.json_schema import schema as root_schema


class TestRootJsonSchema(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.base_url = 'http://localhost:5100/'

    def test_valid_structure(self):
        computed_schema = root_schema(self.base_url)
        self.assertEqual(type(computed_schema), dict)

    def test_list_contexts(self):
        computed_schema = root_schema(self.base_url)
        expected_links = [
            {'href': 'http://localhost:5100', 'method': 'GET', 'rel': 'self'},
            {'href': 'http://localhost:5100/{resource_id}', 'method': 'GET', 'rel': 'list'},
            {'href': 'http://localhost:5100/{resource_id}', 'method': 'GET', 'rel': 'context'},
            {'href': 'http://localhost:5100', 'method': 'GET', 'rel': 'first',
             'schema': {'required': ['page'], 'type': 'object',
                        'properties': {'per_page': {'default': 10, 'minimum': 1, 'type': 'integer'}, 'page': {'minimum': 1, 'type': 'integer'}}}},
            {'href': 'http://localhost:5100', 'method': 'GET', 'rel': 'next',
             'schema': {'required': ['page'], 'type': 'object',
                        'properties': {'per_page': {'default': 10, 'minimum': 1, 'type': 'integer'}, 'page': {'minimum': 1, 'type': 'integer'}}}}
        ]
        self.assertEqual(sorted(computed_schema["links"]), sorted(expected_links))
