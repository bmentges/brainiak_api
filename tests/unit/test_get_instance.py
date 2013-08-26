# -*- coding: utf-8 -*-
import unittest
from mock import Mock

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

    def test_get_instance_with_result(self):
        db_response = {"results": {"bindings": ["not_empty"]}}

        def mock_query_all_properties_and_objects(query_params):
            return db_response
        get_instance.query_all_properties_and_objects = mock_query_all_properties_and_objects

        mock_assemble_instance_json = Mock(return_value="ok")
        get_instance.assemble_instance_json = mock_assemble_instance_json
        query_params = {'request': MockRequest(instance="instance"),
                        'context_name': 'place',
                        'class_name': 'Country',
                        'instance_id': 'Brazil',
                        'instance_uri': settings.URI_PREFIX + 'place/Country/Brazil',
                        'lang': 'pt'}

        response = get_instance.get_instance(query_params)

        self.assertEqual(response, "ok")
        self.assertTrue(mock_assemble_instance_json.called)

    def test_get_instance_without_result(self):
        db_response = {"results": {"bindings": []}}

        def mock_query_all_properties_and_objects(query_params):
            return db_response
        get_instance.query_all_properties_and_objects = mock_query_all_properties_and_objects

        mock_assemble_instance_json = Mock(return_value="ok")
        get_instance.assemble_instance_json = mock_assemble_instance_json
        query_params = {'request': MockRequest(instance="instance"),
                        'context_name': 'place',
                        'class_name': 'Country',
                        'instance_id': 'Brazil',
                        'instance_uri': settings.URI_PREFIX + 'place/Country/Brazil',
                        'lang': 'pt'}

        response = get_instance.get_instance(query_params)

        self.assertEqual(response, None)
        self.assertFalse(mock_assemble_instance_json.called)

    def test_query_all_properties_and_objects(self):
        triplestore.query_sparql = lambda query, query_params: query

        class Params(dict):
            triplestore_config = {}

        params = Params({})
        params.update({
            "instance_uri": "instance_uri",
            "class_uri": "class_uri",
            "lang": "en"
        })

        computed = get_instance.query_all_properties_and_objects(params)
        expected = """
            DEFINE input:inference <http://semantica.globo.com/ruleset>
            SELECT DISTINCT ?predicate ?object ?super_property {
                <instance_uri> a <class_uri>;
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
        get_instance.build_items_dict = lambda context, bindings, class_uri: {}

    def tearDown(self):
        get_instance.build_items_dict = self.original_build_items

    def prepare_params(self, instance_uri="http://mock.test.com/schema/klass/instance"):
        param_dict = {'context_name': 'schema',
                      'class_name': 'klass',
                      'instance_prefix': 'http://schema.org/klass/',
                      'instance_id': 'instance',
                      'expand_uri': SHORTEN}
        handler = MockHandler(uri=instance_uri, **param_dict)
        self.query_params = ParamDict(handler, **param_dict)
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


class BuildItemsDictTestCase(unittest.TestCase):

    def test_build_items_dict(self):
        bindings = [
            {"predicate": {"value": "key1"}, "object": {"value": "value1"}, "label": {"value": "label1"}},
            {"predicate": {"value": "key1"}, "object": {"value": "value2"}, "label": {"value": "label1"}},
            {"predicate": {"value": "key2"}, "object": {"value": "value2"}, "label": {"value": "label1"}}
        ]
        expected = {
            "key1": ["value1", "value2"],
            "key2": "value2",
            "rdf:type": "some:Class"}
        context = MemorizeContext(normalize_keys=SHORTEN, normalize_values=SHORTEN)
        response = get_instance.build_items_dict(context, bindings, "some:Class")
        self.assertEqual(response, expected)

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
        expected = {"birthCity": "Rio de Janeiro", 'rdf:type': 'http://class.uri'}
        context = MemorizeContext(normalize_keys=SHORTEN, normalize_values=SHORTEN)
        response = get_instance.build_items_dict(context, bindings, "http://class.uri")
        self.assertEqual(response, expected)

    def test_build_items_dict_with_super_property_and_different_values(self):
        bindings = self.prepare_input_and_expected_output(object_value="Brasil")
        expected = {
            "birthCity": "Rio de Janeiro",
            "birthPlace": "Brasil",
            'rdf:type': 'http://class.uri'
        }
        context = MemorizeContext(normalize_keys=SHORTEN, normalize_values=SHORTEN)
        response = get_instance.build_items_dict(context, bindings, "http://class.uri")
        self.assertEqual(response, expected)

    def test_build_items_dict_with_super_property_and_different_values_expanding_uri(self):
        bindings = self.prepare_input_and_expected_output(object_value="Brasil")
        expected = {
            "birthCity": "Rio de Janeiro",
            "birthPlace": "Brasil",
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://class.uri'
        }
        context = MemorizeContext(normalize_keys=EXPAND, normalize_values=EXPAND)
        response = get_instance.build_items_dict(context, bindings, "http://class.uri")
        self.assertEqual(response, expected)
