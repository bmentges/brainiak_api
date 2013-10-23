# -*- coding: utf-8 -*-

import unittest
from brainiak.schema.get_class import items_from_range


class ItemsFromRangeTestCase(unittest.TestCase):

    def test_items_from_range_date(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#date"),
                          {"type": "string", "format": "date", "datatype": "http://www.w3.org/2001/XMLSchema#date"})

    def test_items_from_range_integer(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#integer"),
                          {'datatype': "http://www.w3.org/2001/XMLSchema#integer", 'type': 'integer'})

    def test_items_from_range_float(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#float"),
                          {'datatype': "http://www.w3.org/2001/XMLSchema#float", 'type': 'number'})

    def test_items_from_range_string(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#string"),
                          {'datatype': "http://www.w3.org/2001/XMLSchema#string", 'type': 'string'})

    def test_items_from_range_string_any_uri(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#anyURI"),
                          {'datatype': "http://www.w3.org/2001/XMLSchema#anyURI", 'type': 'string'})

    def test_items_from_range_unmapped(self):
        self.assertEqual(items_from_range("http://some/strange/type/uri"),
                          {'datatype': 'http://some/strange/type/uri', 'type': 'string'})
