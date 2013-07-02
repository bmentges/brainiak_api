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
            {'href': '{+id}', 'method': 'GET', 'rel': 'self'},
            {'href': '/?page=1&per_page={per_page}&do_item_count={do_item_count}', 'method': 'GET', 'rel': 'first'},
            {'href': '/?page={next_page}&per_page={per_page}&do_item_count={do_item_count}', 'method': 'GET', 'rel': 'next'},
            {'href': '/?page={previous_page}&per_page={per_page}&do_item_count={do_item_count}', 'method': 'GET', 'rel': 'previous'}
        ]
        self.assertEqual(sorted(computed_schema["links"]), sorted(expected_links))
