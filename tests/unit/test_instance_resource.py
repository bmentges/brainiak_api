# -*- coding: utf-8 -*-
import unittest
from mock import Mock

from brainiak import settings, triplestore
from brainiak.instance import get_instance
from brainiak.prefixes import MemorizeContext
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
            SELECT DISTINCT ?predicate ?object ?label ?super_property {
                <instance_uri> a <class_uri>;
                    rdfs:label ?label;
                    ?predicate ?object .
            OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
            FILTER((langMatches(lang(?object), "en") OR langMatches(lang(?object), "")) OR (IsURI(?object))) .
            FILTER(langMatches(lang(?label), "en") OR langMatches(lang(?label), "")) .
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
        # expected_links = [
        #     {'rel': 'self', 'href': 'http://mock.test.com/schema/klass/instance', 'method': 'GET'},
        #     {'rel': 'class', 'href': 'http://mock.test.com/schema/klass/_schema', 'method': 'GET'},
        #     {'rel': 'collection', 'href': 'http://mock.test.com/schema/klass', 'method': 'GET'},
        #     {'rel': 'delete', 'href': 'http://mock.test.com/schema/klass/instance', 'method': 'DELETE'},
        #     {'rel': 'replace', 'href': 'http://mock.test.com/schema/klass/instance', 'method': 'PUT', 'schema': {'$ref': 'http://mock.test.com/schema/klass/_schema'}}
        # ]

        self.assertEqual(computed["@id"], "http://schema.org/klass/instance")
        self.assertEqual(computed["@type"], "schema:klass")
        self.assertEqual(computed["@context"], {})
        #self.assertEqual(sorted(computed["links"]), sorted(expected_links))

    def test_assemble_instance_json_links_with_context(self):

        class InnerContextMock():
            pass

        class ContextMock():
            context = InnerContextMock()
            object_properties = {"person": "person:Person"}

        context = ContextMock()
        param_dict = {'context_name': 'schema',
                      'class_name': 'klass',
                      'instance_id': 'instance'}
        handler = MockHandler(uri="http://mock.test.com/schema/klass/instance", **param_dict)
        query_params = ParamDict(handler, **param_dict)

        query_result_dict = {'results': {'bindings': []}}
        get_instance.build_items_dict = lambda context, bindings, class_uri: {}
        computed = get_instance.assemble_instance_json(query_params, query_result_dict, context)
        # expected_links = [
        #     {'rel': 'self', 'href': 'http://mock.test.com/schema/klass/instance', 'method': 'GET'},
        #     {'rel': 'class', 'href': 'http://mock.test.com/schema/klass/_schema', 'method': 'GET'},
        #     {'rel': 'collection', 'href': 'http://mock.test.com/schema/klass', 'method': 'GET'},
        #     {'rel': 'delete', 'href': 'http://mock.test.com/schema/klass/instance', 'method': 'DELETE'},
        #     {'rel': 'replace', 'href': 'http://mock.test.com/schema/klass/instance', 'method': 'PUT', 'schema': {'$ref': 'http://mock.test.com/schema/klass/_schema'}},
        #     {'rel': 'person', 'href': '/person/Person'}
        # ]

        self.assertEqual(computed["@id"], "http://schema.org/klass/instance")
        self.assertEqual(computed["@type"], "schema:klass")
        self.assertIsInstance(computed["@context"], InnerContextMock)
        #self.assertItemsEqual(computed["links"], expected_links)

    # def test_assemble_instance_json_links_with_context_with_class_prefix_and_instance_prefix(self):
    #
    #     class InnerContextMock():
    #         pass
    #
    #     class ContextMock():
    #         context = InnerContextMock()
    #         object_properties = {"person": "person:Person"}
    #
    #     context = ContextMock()
    #
    #     param_dict = {'context_name': 'schema',
    #                   'class_name': 'klass',
    #                   'instance_id': 'instance',
    #                   'instance_prefix': 'fake_instance_prefix'}
    #     handler = MockHandler(uri="http://mock.test.com/schema/klass/instance", querystring="class_prefix=CLASS_PREFIX&instance_prefix=INSTANCE_PREFIX", **param_dict)
    #     query_params = ParamDict(handler, **param_dict)
    #
    #     query_result_dict = {'results': {'bindings': []}}
    #     get_resource.build_items_dict = lambda context, bindings, class_uri: {}
    #     computed = get_resource.assemble_instance_json(query_params, query_result_dict, context)
    #     expected_links = [
    #         {'rel': 'self', 'href': 'http://mock.test.com/schema/klass/instance?class_prefix=CLASS_PREFIX&instance_prefix=INSTANCE_PREFIX', 'method': 'GET'},
    #         {'rel': 'class', 'href': 'http://mock.test.com/schema/klass/_schema?class_prefix=CLASS_PREFIX', 'method': 'GET'},
    #         {'rel': 'collection', 'href': 'http://mock.test.com/schema/klass?class_prefix=CLASS_PREFIX', 'method': 'GET'},
    #         {'rel': 'delete', 'href': 'http://mock.test.com/schema/klass/instance?class_prefix=CLASS_PREFIX&instance_prefix=INSTANCE_PREFIX', 'method': 'DELETE'},
    #         {'rel': 'replace', 'href': 'http://mock.test.com/schema/klass/instance?class_prefix=CLASS_PREFIX&instance_prefix=INSTANCE_PREFIX', 'method': 'PUT', 'schema': {'$ref': 'http://mock.test.com/schema/klass/_schema?class_prefix=CLASS_PREFIX'}},
    #         {'rel': 'person', 'href': '/person/Person'}
    #     ]
    #     self.assertEquals(len(computed["links"]), 6)
    #     for link in expected_links:
    #         self.assertIn(link, computed["links"])


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
            'rdfs:label': 'label1',
            "rdf:type": "some:Class"}
        response = get_instance.build_items_dict(MemorizeContext(), bindings, "some:Class")
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
        expected = {"birthCity": "Rio de Janeiro", 'rdfs:label': "birth place", 'rdf:type': 'http://class.uri'}
        context = MemorizeContext()
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
            'rdfs:label': "birth place",
            'rdf:type': 'http://class.uri'
        }
        context = MemorizeContext()
        response = get_instance.build_items_dict(context, bindings, "http://class.uri")
        self.assertEqual(response, expected)
