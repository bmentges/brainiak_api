# -*- coding: utf-8 -*-
import unittest
from mock import patch

from brainiak import prefixes
from brainiak.prefixes import expand_uri, extract_prefix, is_compressed_uri, MemorizeContext, prefix_from_uri, prefix_to_slug, PrefixError, safe_slug_to_prefix, shorten_uri, slug_to_prefix, uri_to_slug, normalize_uri, SHORTEN, EXPAND, InvalidModeForNormalizeUriError


class PrefixesTestCase(unittest.TestCase):

    def test_prefix_contains_obligatory_keys(self):
        existing_keys = sorted(prefixes._MAP_SLUG_TO_PREFIX.keys())
        expected_keys = ['base', 'dbpedia', 'dc', 'dct', 'ego', 'esportes',
                         'eureka', 'event', 'foaf', 'G1', 'geo', 'glb', 'organization',
                         'owl', 'person', 'place', 'rdf', 'rdfs', 'schema', 'time', 'tvg',
                         'upper', 'xsd']
        self.assertEqual(len(existing_keys), 23)
        self.assertEqual(sorted(existing_keys), sorted(expected_keys))

    def test_prefix_to_slug(self):
        self.assertEqual(prefix_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'rdf')

    def test_uri_to_slug(self):
        self.assertEqual(uri_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), 'rdf')

    def test_safe_slug_to_prefix_when_prefix_is_defined(self):
        self.assertEqual(safe_slug_to_prefix('rdf'), 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_safe_slug_to_prefix_when_prefix_is_not_defined(self):
        self.assertEqual(safe_slug_to_prefix('bigoletinha'), 'bigoletinha')

    def test_slug_to_prefix_when_prefix_is_defined(self):
        self.assertEqual(slug_to_prefix('dct'), 'http://purl.org/dc/terms/')

    def test_slug_to_prefix_when_prefix_is_not_defined(self):
        self.assertRaises(PrefixError, slug_to_prefix, 'alchueyr')

    def test_shorten_uri_success(self):
        self.assertEqual(shorten_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), "rdf:type")

    def test_shorten_uri_fails(self):
        self.assertEqual(shorten_uri("http://some/invalid/uri"), "http://some/invalid/uri")

    @patch("brainiak.prefixes.extract_prefix", return_value="http://some/")
    def test_shorten_with_slash_in_item(self, mocked_extract_prefix):
        self.assertEqual(shorten_uri("http://some/invalid/uri"), "http://some/invalid/uri")

    def test_prefix_from_uri(self):
        self.assertEqual("http://test/person/", prefix_from_uri("http://test/person/Person"))

    def test_expand_uri(self):
        self.assertEqual("http://www.w3.org/2003/01/geo/wgs84_pos#Brasil", expand_uri("geo:Brasil"))

    def test_expand_uri(self):
        self.assertEqual("http://schema.org/whatever", expand_uri("schema:whatever"))

    def test_expand_uri_that_is_already_a_uri(self):
        self.assertEqual("http://oi", expand_uri("http://oi"))

    def test_expand_uri_that_is_already_a_uri_with_https(self):
        self.assertEqual("https://secure", expand_uri("https://secure"))

    def test_is_compressed_uri_given_a_literal(self):
        self.assertEqual(is_compressed_uri("oi"), False)

    def test_is_compressed_uri_given_a_compressed_uri(self):
        self.assertEqual(is_compressed_uri("person:Person"), True)

    def test_is_compressed_uri_given_a_compressed_uri_with_invalid_prefix_slug(self):
        self.assertEqual(is_compressed_uri("unexistent:Xubi"), False)

    def test_is_compressed_uri_given_a_uncompressed_uri(self):
        self.assertEqual(is_compressed_uri("http://something.org/xubiru"), False)

    def test_is_compressed_uri_given_a_compressed_and_prefixes(self):
        self.assertEqual(is_compressed_uri("newslug:xubiru", {"newslug": "http://newslug.com"}), True)

    def test_normalize_uri_shorten(self):
        self.assertEqual(normalize_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", mode=SHORTEN), "rdf:type")

    def test_normalize_uri_expand(self):
        self.assertEqual(normalize_uri("rdf:type", mode=EXPAND), "http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

    def test_normalize_uri_invalid_mode(self):
        self.assertRaises(InvalidModeForNormalizeUriError, normalize_uri, "rdf:type", mode='INVALID_MODE')

class ExtractPrefixTestCase(unittest.TestCase):

    def setUp(self):
        self.original_prefix_to_slug = prefixes._MAP_PREFIX_TO_SLUG
        prefixes._MAP_PREFIX_TO_SLUG = {}

    def tearDown(self):
        prefixes._MAP_PREFIX_TO_SLUG = self.original_prefix_to_slug

    def test_prefix_is_substring_of_other_prefix(self):
        prefixes._MAP_PREFIX_TO_SLUG["http://some"] = None
        prefixes._MAP_PREFIX_TO_SLUG["http://someprefix/place/"] = "place"
        prefixes._MAP_PREFIX_TO_SLUG["http://someprefix/place/City"] = "place"
        self.assertEqual("http://someprefix/place/City", extract_prefix("http://someprefix/place/City"))


class MemorizeContextTestCase(unittest.TestCase):

    def setUp(self):
        self.context = MemorizeContext()

    def test_unique_object_properties(self):
        self.context.add_object_property("ctx:field_name", "upper:Entity")
        self.assertIn('ctx:field_name', self.context.object_properties)

    def test_object_properties_with_URL(self):
        self.context.add_object_property("http://www.bbc.co.uk/ontologies/asset/Asset",
                                         "http://www.bbc.co.uk/ontologies/asset/primaryAsset")
        self.assertIn('http://www.bbc.co.uk/ontologies/asset/Asset', self.context.object_properties)
        self.assertEqual(self.context.object_properties['http://www.bbc.co.uk/ontologies/asset/Asset'],
                         "http://www.bbc.co.uk/ontologies/asset/primaryAsset")

    def test_prefix_to_slug(self):
        self.assertEqual(self.context.prefix_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'rdf')
        self.assertIn('rdf', self.context.context)
        self.assertEqual(self.context.context['rdf'], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_shorten_uri(self):
        self.assertEqual(self.context.shorten_uri('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), 'rdf:type')
        self.assertIn('rdf', self.context.context)
        self.assertEqual(self.context.context['rdf'], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')


class MemorizeContextTestCase(unittest.TestCase):

    def test_normalize_uri_expand(self):
        context_expand = MemorizeContext(normalize_uri_mode=EXPAND)
        self.assertEqual(context_expand.normalize_uri("rdf:type"), "http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

    def test_normalize_uri_shorten(self):
        context_expand = MemorizeContext(normalize_uri_mode=SHORTEN)
        self.assertEqual(context_expand.normalize_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), "rdf:type")
