# -*- coding: utf-8 -*-
import unittest
from mock import Mock

from brainiak import settings, triplestore
from brainiak.instance import get_instance
from brainiak.prefixes import MemorizeContext, SHORTEN
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
        triplestore.query_sparql = lambda query: query
        params = {
            "instance_uri": "instance_uri",
            "class_uri": "class_uri",
            "lang": "en"

        }
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

    def tearDown(self):
        get_instance.build_items_dict = self.original_build_items

    def test_assemble_instance_json_links(self):
        param_dict = {'context_name': 'schema',
                      'class_name': 'klass',
                      'instance_id': 'instance'}

        handler = MockHandler(uri="http://mock.test.com/schema/klass/instance", **param_dict)
        query_params = ParamDict(handler, **param_dict)

        query_result_dict = {'results': {'bindings': []}}

        get_instance.build_items_dict = lambda context, bindings, class_uri: {}
        computed = get_instance.assemble_instance_json(query_params, query_result_dict)

        self.assertEqual(computed["@id"], "http://schema.org/klass/instance")
        self.assertEqual(computed["@type"], "schema:klass")
        self.assertEqual(computed["@context"], {'schema': 'http://schema.org/'})

    def test_assemble_instance_json_links_with_context(self):

        context = MemorizeContext(normalize_uri_mode=SHORTEN)
        param_dict = {'context_name': 'schema',
                      'class_name': 'klass',
                      'instance_id': 'instance'}
        handler = MockHandler(uri="http://mock.test.com/schema/klass/instance", **param_dict)
        query_params = ParamDict(handler, **param_dict)

        query_result_dict = {'results': {'bindings': []}}
        get_instance.build_items_dict = lambda context, bindings, class_uri: {}
        computed = get_instance.assemble_instance_json(query_params, query_result_dict, context)

        self.assertEqual(computed["@id"], "http://schema.org/klass/instance")
        self.assertEqual(computed["@type"], "schema:klass")
        self.assertEqual(computed["@context"], {'schema': 'http://schema.org/'})


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
        response = get_instance.build_items_dict(MemorizeContext(normalize_uri_mode=SHORTEN), bindings, "some:Class")
        self.assertEqual(response, expected)

    def test_build_items_dict_with_super_property_and_same_value(self):
        bindings = [
            {
                "predicate": {"value": "birthCity"},
                "object": {"value": "Rio de Janeiro"},
                "label": {"value": "birth place"},
                "super_property": {"value": "birthPlace"}
            },
            {
                "predicate": {"value": "birthPlace"},
                "object": {"value": "Rio de Janeiro"},
                "label": {"value": "birth place"}
            }
        ]
        expected = {"birthCity": "Rio de Janeiro", 'rdf:type': 'http://class.uri'}
        context = MemorizeContext(normalize_uri_mode=SHORTEN)
        response = get_instance.build_items_dict(context, bindings, "http://class.uri")
        self.assertEqual(response, expected)

    def test_build_items_dict_with_super_property_and_different_values(self):
        bindings = [
            {
                "predicate": {"value": "birthCity"},
                "object": {"value": "Rio de Janeiro"},
                "label": {"value": "birth place"},
                "super_property": {"value": "birthPlace"}
            },
            {
                "predicate": {"value": "birthPlace"},
                "object": {"value": "Brasil"},
                "label": {"value": "birth place"}
            }
        ]
        expected = {
            "birthCity": "Rio de Janeiro",
            "birthPlace": "Brasil",
            'rdf:type': 'http://class.uri'
        }
        context = MemorizeContext(normalize_uri_mode=SHORTEN)
        response = get_instance.build_items_dict(context, bindings, "http://class.uri")
        self.assertEqual(response, expected)
