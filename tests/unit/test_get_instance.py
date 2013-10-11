# -*- coding: utf-8 -*-
import unittest

from mock import Mock, patch

from brainiak import settings, triplestore
from brainiak.instance import get_instance
from brainiak.prefixes import MemorizeContext, SHORTEN, EXPAND
from brainiak.utils.params import ParamDict
from tests.mocks import MockRequest, MockHandler
from tests.sparql import strip


class TestCaseInstanceResource(unittest.TestCase):

    def setUp(self):
        self.original_query_all_properties_and_objects = get_instance.query_all_properties_and_objects
        self.original_assemble_instance_json = get_instance.assemble_instance_json
        self.original_query_sparql = triplestore.query_sparql

    def tearDown(self):
        get_instance.query_all_properties_and_objects = self.original_query_all_properties_and_objects
        get_instance.assemble_instance_json = self.original_assemble_instance_json
        triplestore.query_sparql = self.original_query_sparql

    @patch("brainiak.instance.get_instance.query_all_properties_and_objects", return_value={"results": {"bindings": ["not_empty"]}})
    @patch("brainiak.instance.get_instance.assemble_instance_json", return_value="ok")
    @patch("brainiak.schema.get_class.get_cached_schema", return_value={})
    def test_get_instance_with_result(self, get_cached_schema, assemble_instance_json, query_all_properties_and_objects):
        query_params = {'request': MockRequest(instance="instance"),
                        'class_name': 'Country',
                        'class_uri': 'http://www.onto.sample/place/Country',
                        'context_name': 'place',
                        'expand_uri_keys': '0',
                        'expand_uri_values': '0',
                        'graph_uri': 'http://www.onto.sample/place',
                        'instance_id': 'Brazil',
                        'instance_uri': settings.URI_PREFIX + 'place/Country/Brazil',
                        'lang': 'pt'}

        response = get_instance.get_instance(query_params)

        self.assertEqual(response, "ok")
        self.assertTrue(assemble_instance_json.called)
        self.assertTrue(get_cached_schema.called)
        self.assertTrue(query_all_properties_and_objects.called)

    @patch("brainiak.instance.get_instance.query_all_properties_and_objects", return_value={"results": {"bindings": []}})
    @patch("brainiak.instance.get_instance.assemble_instance_json", return_value="ok")
    @patch("brainiak.schema.get_class.get_cached_schema", return_value={})
    def test_get_instance_without_result(self, get_cached_schema, assemble_instance_json, query_all_properties_and_objects):
        query_params = {'request': MockRequest(instance="instance"),
                        'class_name': 'Country',
                        'class_uri': 'http://www.onto.sample/place/Country',
                        'context_name': 'place',
                        'expand_uri_keys': '0',
                        'expand_uri_values': '0',
                        'graph_uri': 'http://www.onto.sample/place',
                        'instance_id': 'Brazil',
                        'instance_uri': settings.URI_PREFIX + 'place/Country/Brazil',
                        'lang': 'pt'}

        response = get_instance.get_instance(query_params)

        self.assertEqual(response, None)
        self.assertFalse(assemble_instance_json.called)
        self.assertFalse(get_cached_schema.called)
        self.assertTrue(query_all_properties_and_objects.called)

    def test_query_all_properties_and_objects_with_expand_object_properties(self):
        triplestore.query_sparql = lambda query, query_params: query

        class Params(dict):
            triplestore_config = {}

        params = Params({})
        params.update({
            "instance_uri": "instance_uri",
            "class_uri": "class_uri",
            "lang": "en",
            "expand_object_properties": "1"
        })

        computed = get_instance.query_all_properties_and_objects(params)
        expected = """
            DEFINE input:inference <http://semantica.globo.com/ruleset>
            SELECT DISTINCT ?predicate ?object ?object_label ?super_property {
                <instance_uri> a <class_uri> ;
                    ?predicate ?object .
            OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
            OPTIONAL { ?object rdfs:label ?object_label } .
            FILTER((langMatches(lang(?object), "en") OR langMatches(lang(?object), "")) OR (IsURI(?object))) .
            }
            """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_all_properties_and_objects_without_expand_object_properties(self):
        triplestore.query_sparql = lambda query, query_params: query

        class Params(dict):
            triplestore_config = {}

        params = Params({})
        params.update({
            "instance_uri": "instance_uri",
            "class_uri": "class_uri",
            "lang": "en",
            "expand_object_properties": "0"
        })

        computed = get_instance.query_all_properties_and_objects(params)
        expected = """
            DEFINE input:inference <http://semantica.globo.com/ruleset>
            SELECT DISTINCT ?predicate ?object  ?super_property {
                <instance_uri> a <class_uri> ;
                    ?predicate ?object .
            OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .

            FILTER((langMatches(lang(?object), "en") OR langMatches(lang(?object), "")) OR (IsURI(?object))) .
            }
            """
        self.assertEqual(strip(computed), strip(expected))


class AssembleTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.original_build_items = get_instance.build_items_dict
        get_instance.build_items_dict = lambda context, bindings, class_uri, expand_direct_properties, class_schema: {}

    def tearDown(self):
        get_instance.build_items_dict = self.original_build_items

    def prepare_params(self, instance_uri="http://mock.test.com/schema/klass/instance", meta_properties=None):
        param_dict = {
            'context_name': 'schema',
            'class_name': 'klass',
            'instance_prefix': 'http://schema.org/klass/',
            'instance_id': 'instance',
            'expand_uri': SHORTEN
        }
        if meta_properties:
            param_dict.update({'meta_properties': meta_properties})
        handler = MockHandler(uri=instance_uri, **param_dict)
        self.query_params = ParamDict(handler, **param_dict)
        self.query_params["class_schema"] = {}
        self.query_result_dict = {'results': {'bindings': []}}

    def assertResults(self, computed):
        self.assertEqual(computed["@id"], "http://schema.org/klass/instance")
        self.assertEqual(computed["@type"], "schema:klass")
        self.assertEqual(computed["@context"], {'schema': 'http://schema.org/'})

    def test_assemble_instance_json_links(self):
        self.prepare_params()
        computed = get_instance.assemble_instance_json(self.query_params, self.query_result_dict)
        self.assertResults(computed)

    def test_assemble_instance_json_links_with_context(self):
        self.prepare_params()
        context = MemorizeContext(normalize_keys=SHORTEN, normalize_values=SHORTEN)
        computed = get_instance.assemble_instance_json(self.query_params, self.query_result_dict, context)
        self.assertResults(computed)

    def test_assemble_instance_json_links_with_context_expanding_uri(self):
        self.prepare_params(instance_uri="http://mock.test.com/schema/klass/instance?expand_uri=1")
        context = MemorizeContext(normalize_keys=EXPAND, normalize_values=EXPAND)
        computed = get_instance.assemble_instance_json(self.query_params, self.query_result_dict, context)
        self.assertEqual(computed["@type"], "http://schema.org/klass")

    def test_assemble_instance_json_with_no_meta_properties(self):
        self.prepare_params(meta_properties="0")
        computed = get_instance.assemble_instance_json(self.query_params, self.query_result_dict)
        expected = {}  # because build_items is empty
        self.assertEqual(computed, expected)


class BuildItemsDictTestCase(unittest.TestCase):

    def test_build_items_dict(self):
        bindings = [
            {"predicate": {"value": "key1"}, "object": {"value": "value1"}, "label": {"value": "label1"}},
            {"predicate": {"value": "key1"}, "object": {"value": "value2"}, "label": {"value": "label1"}},
            {"predicate": {"value": "key2"}, "object": {"value": "value2"}, "label": {"value": "label1"}}
        ]
        class_schema = {
            "properties": {
                "key1": {"type": "array"},
                "key2": {"type": "string"},
                "rdf:type": {"type": "string"}
            }
        }
        context = MemorizeContext(normalize_keys=SHORTEN, normalize_values=SHORTEN)
        response = get_instance.build_items_dict(context, bindings, "some:Class", True, class_schema)
        expected = {
            "key1": ["value1", "value2"],
            "key2": "value2",
            "rdf:type": "some:Class"
        }
        self.assertEqual(response, expected)

    def test_assemble_instance_json_with_object_labels(self):

        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                u'object': {u'type': u'literal', u'value': u'Cricket becomes the most popular sport of Brazil'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://brmedia.com/related_to'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/Cricket'},
                u'object_label': {u'type': u'literal', u'value': u'Cricket'}
            }
        ]
        class_schema = {
            "properties": {
                u'http://www.w3.org/2000/01/rdf-schema#label': {"type": "string"},
                u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': {"type": "string"},
                u'http://brmedia.com/related_to': {"type": "object"}
            }
        }
        context = MemorizeContext(normalize_keys=SHORTEN, normalize_values=SHORTEN)
        computed = get_instance.build_items_dict(context, bindings, "dbpedia:News", 1, class_schema)

        expected = {
            'rdfs:label': u'Cricket becomes the most popular sport of Brazil',
            'rdf:type': 'dbpedia:News',
            'http://brmedia.com/related_to': {"@id": "dbpedia:Cricket", "title": "Cricket"}
        }
        self.assertEqual(computed, expected)

    def prepare_input_and_expected_output(self, object_value):
        bindings = [
            {
                "predicate": {"value": "birthCity"},
                "object": {"value": "Rio de Janeiro"},
                "label": {"value": "birth place"},
                "super_property": {"value": "birthPlace"}
            },
            {
                "predicate": {"value": "birthPlace"},
                "object": {"value": object_value},
                "label": {"value": "birth place"}
            }
        ]
        return bindings

    def test_build_items_dict_with_super_property_and_same_value(self):
        bindings = self.prepare_input_and_expected_output(object_value="Rio de Janeiro")
        class_schema = {
            "properties": {
                "birthPlace": {"type": "string"},
                "birthCity": {"type": "string"}
            }
        }
        expected = {
            "birthCity": "Rio de Janeiro",
            'rdf:type': 'http://class.uri'
        }
        context = MemorizeContext(normalize_keys=SHORTEN, normalize_values=SHORTEN)
        response = get_instance.build_items_dict(context, bindings, "http://class.uri", False, class_schema)
        self.assertEqual(response, expected)

    def test_build_items_dict_with_super_property_and_different_values(self):
        bindings = self.prepare_input_and_expected_output(object_value="Brasil")
        class_schema = {
            "properties": {
                "birthCity": {"type": "string"},
                "birthPlace": {"type": "string"},
                "rdf:type": {"type": "string"}
            }
        }
        expected = {
            "birthCity": "Rio de Janeiro",
            "birthPlace": "Brasil",
            'rdf:type': 'http://class.uri'
        }
        context = MemorizeContext(normalize_keys=SHORTEN, normalize_values=SHORTEN)
        response = get_instance.build_items_dict(context, bindings, "http://class.uri", False, class_schema)
        self.assertEqual(response, expected)

    def test_build_items_dict_with_super_property_and_different_values_expanding_uri(self):
        bindings = self.prepare_input_and_expected_output(object_value="Brasil")
        context = MemorizeContext(normalize_keys=EXPAND, normalize_values=EXPAND)
        class_schema = {
            "properties": {
                "birthCity": {"type": "string"},
                "birthPlace": {"type": "string"},
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": {"type": "string"}
            }
        }
        expected = {
            "birthCity": "Rio de Janeiro",
            "birthPlace": "Brasil",
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://class.uri'
        }
        response = get_instance.build_items_dict(context, bindings, "http://class.uri", False, class_schema)
        self.assertEqual(response, expected)
