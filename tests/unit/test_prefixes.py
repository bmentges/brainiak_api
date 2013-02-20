# -*- coding: utf-8 -*-

import unittest
from brainiak.prefixes import uri_to_prefix, prefix_to_uri, replace_prefix


class TriplestoreTestCase(unittest.TestCase):

    def test_uri_to_prefix(self):
        self.assertEquals(uri_to_prefix('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'rdf')

    def test_prefix_to_uri(self):
        self.assertEquals(prefix_to_uri('rdf'), 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_replace_prefix_success(self):
        self.assertEquals(replace_prefix("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), "rdf:type")

    def test_replace_prefix_fails(self):
        self.assertEquals(replace_prefix("http://some/invalid/uri"), "http://some/invalid/uri")
