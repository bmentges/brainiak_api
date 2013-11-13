# -*- coding: utf-8 -*-

import unittest

from mock import patch

from brainiak.schema.get_class import items_from_range


class ItemsFromRangeTestCase(unittest.TestCase):

    @patch("brainiak.schema.get_class.logger")
    def test_items_from_range_date(self, log):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#date"),
                         {"type": "string", "format": "date", "datatype": "http://www.w3.org/2001/XMLSchema#date"})

    @patch("brainiak.schema.get_class.logger")
    def test_items_from_range_integer(self, log):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#integer"),
                         {'datatype': "http://www.w3.org/2001/XMLSchema#integer", 'type': 'integer'})

    @patch("brainiak.schema.get_class.logger")
    def test_items_from_range_float(self, log):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#float"),
                         {'datatype': "http://www.w3.org/2001/XMLSchema#float", 'type': 'number'})

    @patch("brainiak.schema.get_class.logger")
    def test_items_from_range_string(self, log):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#string"),
                         {'datatype': "http://www.w3.org/2001/XMLSchema#string", 'type': 'string'})

    @patch("brainiak.schema.get_class.logger")
    def test_items_from_range_string_any_uri(self, log):
        self.assertEqual(items_from_range("http://www.w3.org/2001/XMLSchema#anyURI"),
                         {'datatype': "http://www.w3.org/2001/XMLSchema#anyURI", 'type': 'string'})

    @patch("brainiak.schema.get_class.logger")
    def test_items_from_range_unmapped(self, log):
        self.assertEqual(items_from_range("http://some/strange/type/uri"),
                         {'datatype': 'http://some/strange/type/uri', 'type': 'string'})
