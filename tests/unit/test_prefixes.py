# -*- coding: utf-8 -*-

import unittest
from brainiak.prefixes import uri_to_prefix, prefix_to_uri


class TriplestoreTestCase(unittest.TestCase):

    def test_uri_to_prefix(self):
        self.assertEquals(uri_to_prefix('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'rdf')

    def test_prefix_to_uri(self):
        self.assertEquals(prefix_to_uri('rdf'), 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
