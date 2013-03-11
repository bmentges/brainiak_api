# -*- coding: utf-8 -*-

import unittest
from brainiak.prefixes import expand_uri, prefix_to_slug, safe_slug_to_prefix, shorten_uri, slug_to_prefix, MemorizeContext, uri_to_slug, prefix_from_uri, PrefixError


class PrefixesTestCase(unittest.TestCase):

    def test_prefix_to_slug(self):
        self.assertEquals(prefix_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'rdf')

    def test_uri_to_slug(self):
        self.assertEquals(uri_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), 'rdf')

    def test_safe_slug_to_prefix_when_prefix_is_defined(self):
        self.assertEquals(safe_slug_to_prefix('rdf'), 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_safe_slug_to_prefix_when_prefix_is_not_defined(self):
        self.assertEquals(safe_slug_to_prefix('bigoletinha'), 'bigoletinha')

    def test_slug_to_prefix_when_prefix_is_defined(self):
        self.assertEquals(slug_to_prefix('dct'), 'http://purl.org/dc/terms/')

    def test_slug_to_prefix_when_prefix_is_not_defined(self):
        self.assertRaises(PrefixError, slug_to_prefix, 'alchueyr')

    def test_shorten_uri_success(self):
        self.assertEquals(shorten_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), "rdf:type")

    def test_shorten_uri_fails(self):
        self.assertEquals(shorten_uri("http://some/invalid/uri"), "http://some/invalid/uri")

    def test_prefix_from_uri(self):
        self.assertEquals("http://test/person/", prefix_from_uri("http://test/person/Person"))

    def test_expand_uri(self):
        self.assertEquals("http://www.w3.org/2003/01/geo/wgs84_pos#Brasil", expand_uri("geo:Brasil"))

    def test_expand_uri(self):
        self.assertEquals("http://schema.org/whatever", expand_uri("schema:whatever"))

    def test_expand_uri_that_is_already_a_uri(self):
        self.assertEquals("http://oi", expand_uri("http://oi"))

    def test_expand_uri_that_is_already_a_uri_with_https(self):
        self.assertEquals("https://secure", expand_uri("https://secure"))


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
