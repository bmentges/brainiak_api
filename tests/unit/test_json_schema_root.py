# -*- coding: utf-8 -*-

import unittest
from brainiak.root.json_schema import schema as root_schema


class TestRootJsonSchema(unittest.TestCase):

    maxDiff = None

    def test_valid_structure(self):
        base_url = 'http://localhost:5100/'
        computed_schema = root_schema(base_url)
        self.assertEqual(type(computed_schema), dict)
