# -*- coding: utf-8 -*-

import unittest
from brainiak.type_mapper import OBJECT_PROPERTY, items_from_type, DATATYPE_PROPERTY, items_from_range


class PrefixesTestCase(unittest.TestCase):

    def test_items_from_type(self):
        self.assertEqual(items_from_type(OBJECT_PROPERTY), {"type": "string", "format": "uri"})

    def test_items_from_range_date(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#date"),
                          {"type": "string", "format": "date"})

    def test_items_from_range_integer(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#integer"),
                          {"type": "integer"})

    def test_items_from_range_float(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#float"),
                          {"type": "number"})

    def test_items_from_range_string(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#string"),
                          {"type": "string"})
