# -*- coding: utf-8 -*-
import unittest
from mock import patch

from brainiak import prefixes
from brainiak.prefixes import (expand_uri, extract_prefix, is_compressed_uri, MemorizeContext, prefix_from_uri,
                               prefix_to_slug, PrefixError, safe_slug_to_prefix, shorten_uri, slug_to_prefix,
                               uri_to_slug, SHORTEN, EXPAND, InvalidModeForNormalizeUriError, normalize_all_uris_recursively, get_prefixes_dict, list_prefixes, _MAP_SLUG_TO_PREFIX)


class PrefixesTestCase(unittest.TestCase):

    maxDiff = None

    def test_prefix_contains_obligatory_keys(self):
        existing_keys = sorted(prefixes._MAP_SLUG_TO_PREFIX.keys())
        expected_keys = ['nodeID', 'base', 'dbpedia', 'dc', 'dct', 'ego', 'esportes',
                         'eureka', 'event', 'foaf', 'g1', 'geo', 'glb', 'organization',
                         'owl', 'person', 'place', 'rdf', 'rdfs', 'schema', 'time', 'tvg',
                         'upper', 'xsd']
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

    def test_expand_uri_whatever(self):
        self.assertEqual("http://schema.org/whatever", expand_uri("schema:whatever"))

    def test_expand_uri_that_is_already_a_uri(self):
        self.assertEqual("http://oi", expand_uri("http://oi"))

    def test_expand_uri_that_is_already_a_uri_with_https(self):
        self.assertEqual("https://secure", expand_uri("https://secure"))

    def test_expand_uri_with_value_string_containing_double_colon(self):
        misleading_value = "Some value: this is no CURIE"
        self.assertEqual(misleading_value, expand_uri(misleading_value))

    def test_is_compressed_uri_given_a_literal(self):
        self.assertEqual(is_compressed_uri("oi"), False)

    def test_is_compressed_uri_given_a_compressed_uri(self):
        self.assertEqual(is_compressed_uri("person:Person"), True)

    def test_is_compressed_uri_given_a_compressed_uri_with_invalid_prefix_slug(self):
        self.assertEqual(is_compressed_uri("unexistent:Xubi"), False)

    def test_is_compressed_uri_given_a_uncompressed_uri(self):
        self.assertEqual(is_compressed_uri("http://something.org/xubiru", {}), False)

    def test_is_compressed_uri_given_a_compressed_and_prefixes(self):
        self.assertEqual(is_compressed_uri("newslug:xubiru", {"newslug": "http://newslug.com"}), True)

    def test_get_prefixes_dict(self):
        MAP_PREFIX_TO_SLUG = get_prefixes_dict()
        self.assertIn('geo', MAP_PREFIX_TO_SLUG)
        self.assertIn('organization', MAP_PREFIX_TO_SLUG)
        self.assertIn('eureka', MAP_PREFIX_TO_SLUG)


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


class NormalizationTestCase(unittest.TestCase):

    def test_expand_uri(self):
        context = MemorizeContext(normalize_uri=EXPAND)
        self.assertEqual(context.normalize_uri("rdf:type"), "http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

    def test_shorten_uri(self):
        context = MemorizeContext(normalize_uri=SHORTEN)
        self.assertEqual(context.normalize_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), "rdf:type")

    def test_normalize_uri_invalid_mode(self):
        context = MemorizeContext(normalize_uri='INVALID_MODE')
        self.assertRaises(InvalidModeForNormalizeUriError, context.normalize_uri, "rdf:type")

    def test_normalize_prefix_to_shorten(self):
        prefix = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        context = MemorizeContext(normalize_uri=SHORTEN)
        normalized = context.normalize_prefix_value(prefix)
        self.assertEqual(normalized, 'rdf')

    def test_normalize_prefix_to_expand(self):
        prefix = "rdf"
        context = MemorizeContext(normalize_uri=EXPAND)
        normalized = context.normalize_prefix_value(prefix)
        self.assertEqual(normalized, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_normalize_prefix_to_shorten_inversed(self):
        prefix = "rdf"
        context = MemorizeContext(normalize_uri=SHORTEN)
        normalized = context.normalize_prefix_value(prefix)
        self.assertEqual(normalized, 'rdf')

    def test_normalize_prefix_to_expand_inversed(self):
        prefix = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        context = MemorizeContext(normalize_uri=EXPAND)
        normalized = context.normalize_prefix_value(prefix)
        self.assertEqual(normalized, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_normalize_prefix_invalid_mode(self):
        context = MemorizeContext(normalize_uri='INVALID_MODE')
        self.assertRaises(InvalidModeForNormalizeUriError, context.normalize_prefix_value, "rdf:type")


VALID_COMPRESSED_INSTANCE_DATA = {
    'rdf:type': 'place:City',
    'upper:name': u'Globoland',
    '_base_url': 'http://localhost:5100/place/City/',
    '_resource_id': '173ed3bf-2863-4e4a-8d37-024f8df72aa3',
    'rdfs:comment': u"City of Globo's companies. Ação is to test the preservation of special characters.",
    'place:longitude': u'-43.407133',
    'place:latitude': -43.407133,
    'frbr:summarizationOf': {'dct:isPartOf': ['base:UF_RJ', 'base:UF_RJ']},
    '@context': {
        'upper': 'http://semantica.globo.com/upper/',
        'base': "http://semantica.globo.com/base/",
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'place': 'http://semantica.globo.com/place/',
        'dct': 'http://purl.org/dc/terms/',
        'schema': 'http://schema.org/',
        'frbr': 'http://purl.org/vocab/frbr/core#',
    },
    '@id': 'http://semantica.globo.com/place/City/173ed3bf-2863-4e4a-8d37-024f8df72aa3',
    '@type': 'place:City'
}

EXPECTED_UNCOMPRESSED_INSTANCE_DATA = {
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://semantica.globo.com/place/City',
    'http://semantica.globo.com/upper/name': u'Globoland',
    '_base_url': 'http://localhost:5100/place/City/',
    '_resource_id': '173ed3bf-2863-4e4a-8d37-024f8df72aa3',
    'http://www.w3.org/2000/01/rdf-schema#comment': u"City of Globo's companies. Ação is to test the preservation of special characters.",
    'http://semantica.globo.com/place/longitude': u'-43.407133',
    'http://semantica.globo.com/place/latitude': -43.407133,
    'http://purl.org/vocab/frbr/core#summarizationOf': {
        'http://purl.org/dc/terms/isPartOf': ['http://semantica.globo.com/base/UF_RJ',
                                             'http://semantica.globo.com/base/UF_RJ']
    },
    '@id': 'http://semantica.globo.com/place/City/173ed3bf-2863-4e4a-8d37-024f8df72aa3',
    '@type': 'http://semantica.globo.com/place/City'
}


class ExpansionTestCase(unittest.TestCase):
    maxDiff = None

    @patch("brainiak.prefixes.expand_uri", side_effect=PrefixError('Anything'))
    def test_normalize_recusively_with_invalid_prefix(self, mock):
        expected = compressed = 'invalid_prefix'
        self.assertEqual(normalize_all_uris_recursively(compressed), expected)

    def test_normalize_recusively_with_valid_input(self):
        self.assertDictEqual(normalize_all_uris_recursively(VALID_COMPRESSED_INSTANCE_DATA), EXPECTED_UNCOMPRESSED_INSTANCE_DATA)

    def test_normalize_recursively_with_invalid_type(self):
        d = {'invalid': 3}
        self.assertDictEqual(normalize_all_uris_recursively(d), d)

    def test_real_resource(self):
        input_data = {'rdfs:comment': u'Some kind of monster.'}
        expected_output = {'http://www.w3.org/2000/01/rdf-schema#comment': u'Some kind of monster.'}
        self.assertDictEqual(normalize_all_uris_recursively(input_data), expected_output)


class ListPrefixesTestCase(unittest.TestCase):
    maxDiff = None

    def test_list_prefixes(self):
        list_of_prefixes = list_prefixes()
        for key in list_of_prefixes['@context']:
            self.assertIn(key, _MAP_SLUG_TO_PREFIX)
