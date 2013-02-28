# -*- coding: utf-8 -*-

import unittest
from brainiak.prefixes import prefix_to_slug, slug_to_prefix, shorten_uri, MemorizeContext, uri_to_slug, prefix_from_uri


class PrefixesTestCase(unittest.TestCase):

    def test_prefix_to_slug(self):
        self.assertEquals(prefix_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'rdf')

    def test_uri_to_slug(self):
        self.assertEquals(uri_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), 'rdf')

    def test_slug_to_prefix(self):
        self.assertEquals(slug_to_prefix('rdf'), 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_shorten_uri_success(self):
        self.assertEquals(shorten_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), "rdf:type")

    def test_shorten_uri_fails(self):
        self.assertEquals(shorten_uri("http://some/invalid/uri"), "http://some/invalid/uri")

    def test_prefix_from_uri(self):
        self.assertEquals("http://test/person/", prefix_from_uri("http://test/person/Person"))


class MemorizeContextTestCase(unittest.TestCase):

    def setUp(self):
        self.context = MemorizeContext()

    def test_unique_object_properties(self):
        self.context.add_object_property("ctx:field_name", "upper:Entity")
        self.assertIn('ctx:field_name', self.context.object_properties)

    def test_prefix_to_slug(self):
        self.assertEquals(self.context.prefix_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'rdf')
        self.assertIn('rdf', self.context.context)
        self.assertEquals(self.context.context['rdf'], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_shorten_uri(self):
        self.assertEquals(self.context.shorten_uri('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), 'rdf:type')
        self.assertIn('rdf', self.context.context)
        self.assertEquals(self.context.context['rdf'], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
