# -*- coding: utf-8 -*-

import unittest
from brainiak.type_mapper import OBJECT_PROPERTY, DATATYPE_PROPERTY, items_from_range


class PrefixesTestCase(unittest.TestCase):

    def test_items_from_range_date(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#date"),
                          {"type": "string", "format": "date"})

    def test_items_from_range_integer(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#integer"),
                          {'format': 'xsd:integer', 'type': 'integer'})

    def test_items_from_range_float(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#float"),
                          {'format': 'xsd:float', 'type': 'number'})

    def test_items_from_range_string(self):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#string"),
                          {'format': 'xsd:string', 'type': 'string'})
