# -*- coding: utf-8 -*-

import unittest
from brainiak.prefixes import SHORTEN, MemorizeContext
from brainiak.schema.get_class import items_from_range


class ItemsFromRangeTestCase(unittest.TestCase):

    def setUp(self):
        self.context = MemorizeContext(normalize_uri_mode=SHORTEN)

    def test_items_from_range_date(self):
        self.assertEqual(items_from_range(self.context, "http://www.w3.org/2001/XMLSchema#date"),
                          {"type": "string", "format": "date"})

    def test_items_from_range_integer(self):
        self.assertEqual(items_from_range(self.context, "http://www.w3.org/2001/XMLSchema#integer"),
                          {'format': 'xsd:integer', 'type': 'integer'})

    def test_items_from_range_float(self):
        self.assertEqual(items_from_range(self.context, "http://www.w3.org/2001/XMLSchema#float"),
                          {'format': 'xsd:float', 'type': 'number'})

    def test_items_from_range_string(self):
        self.assertEqual(items_from_range(self.context, "http://www.w3.org/2001/XMLSchema#string"),
                          {'format': 'xsd:string', 'type': 'string'})

    def test_items_from_range_unmapped(self):
        self.assertEqual(items_from_range(self.context, "http://some/strange/type/uri"),
                          {'format': 'http://some/strange/type/uri', 'type': 'object'})
