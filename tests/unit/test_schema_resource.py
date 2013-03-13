# -*- coding: utf-8 -*-

import json
import unittest
import mock

import brainiak.schema.resource as schema
from brainiak.result_handler import build_predicate_dict
from brainiak import prefixes
from brainiak.schema.resource import _extract_cardinalities

from tests import TornadoAsyncTestCase


class MockResponse(object):
    def __init__(self, body):
        self.body = json.dumps(body)


class GetSchemaTestCase(TornadoAsyncTestCase):
    def setUp(self):
        super(TornadoAsyncTestCase, self).setUp()
        self.original_query_class_schema = schema.query_class_schema
        self.original_get_predicates_and_cardinalities = schema.get_predicates_and_cardinalities

    def tearDown(self):
        schema.query_class_schema = self.original_query_class_schema
        schema.get_predicates_and_cardinalities = self.original_get_predicates_and_cardinalities
        super(TornadoAsyncTestCase, self).tearDown()

    def test_query_get_schema(self):
        # Mocks
        def mock_query_class_schema(class_uri, remember):
            class_schema = {"results": {"bindings": [{"dummy_key": "dummy_value"}]}}
            tornado_response = MockResponse(class_schema)
            return tornado_response

        schema.query_class_schema = mock_query_class_schema

        def mock_get_predicates_and_cardinalities(class_uri, class_schema, remember):
            return "property_dict"

        schema.get_predicates_and_cardinalities = mock_get_predicates_and_cardinalities

        response = schema.get_schema("test_context", "test_class")
        schema_response = response

        self.assertIn("title", schema_response)
        self.assertIn("type", schema_response)
        self.assertIn("@id", schema_response)
        self.assertIn("properties", schema_response)

        self.assertEqual(schema_response["properties"], "property_dict")
        # FIXME: enhance the structure of the response
        self.stop()


class GetPredicatesCardinalitiesTestCase(TornadoAsyncTestCase):
    maxDiff = None

    def setUp(self):
        super(TornadoAsyncTestCase, self).setUp()
        self.original_query_cardinalities = schema.query_cardinalities
        self.original_query_predicates = schema.query_predicates
        self.original_extract_cardinalities = schema._extract_cardinalities

    def tearDown(self):
        schema.query_cardinalities = self.original_query_cardinalities
        schema.query_predicates = self.original_query_predicates
        schema._extract_cardinalities = self.original_extract_cardinalities
        super(TornadoAsyncTestCase, self).tearDown()

    def test_get_predicates_and_cardinalities(self):
        context = prefixes.MemorizeContext()
        class_uri = "http://test/person/gender"
        class_schema = None

        # Mocks
        def mock_query_predicates(class_uri, context):
            fake_response = mock.MagicMock(body="""
            { "results": { "bindings": [
                  { "predicate": { "type": "uri", "value": "http://test/person/root_gender" },
                    "predicate_graph": { "type": "uri", "value": "http://test/person/" },
                    "type": { "type": "uri", "value": "http://www.w3.org/2002/07/owl#ObjectProperty" },
                    "range": { "type": "uri", "value": "http://test/person/Gender" },
                    "title": { "type": "literal", "xml:lang": "pt", "value": "Root (to be removed from answer)" },
                    "grafo_do_range": { "type": "uri", "value": "http://test/person/" }},
                  { "predicate": { "type": "uri", "value": "http://test/person/gender" },
                    "super_property": {"type": "uri", "value": "http://test/person/root_gender"},
                    "predicate_graph": { "type": "uri", "value": "http://test/person/" },
                    "predicate_comment": { "type": "literal", "xml:lang": "pt", "value": "G\u00EAnero." },
                    "type": { "type": "uri", "value": "http://www.w3.org/2002/07/owl#ObjectProperty" },
                    "range": { "type": "uri", "value": "http://test/person/Gender" },
                    "title": { "type": "literal", "xml:lang": "pt", "value": "Sexo" },
                    "grafo_do_range": { "type": "uri", "value": "http://test/person/" },
                    "label_do_range": { "type": "literal", "xml:lang": "pt", "value": "G\u00EAnero da Pessoa" }}]}}
            """)
            return fake_response

        def mock_query_cardinalities(class_uri, class_schema, context):
            fake_response = mock.MagicMock(body="""
                {"results": {
                    "bindings": [
                        {"max": {"datatype": "http://www.w3.org/2001/XMLSchema#integer", "type": "typed-literal", "value": "1"},
                         "predicate": {"type": "uri", "value": "http://test/person/gender"},
                         "range": {"type": "uri", "value": "http://test/person/Gender"}
                        },
                        {"min": {"datatype": "http://www.w3.org/2001/XMLSchema#integer", "type": "typed-literal", "value": "1"},
                         "predicate": {"type": "uri", "value": "http://test/person/gender"},
                         "range": {"type": "uri", "value": "http://test/person/Gender"}
                        },
                        {"enumerated_value": {"type": "uri", "value": "http://test/person/Gender/Male"},
                         "enumerated_value_label": {"type": "literal", "value": "Masculino", "xml:lang": "pt"},
                         "predicate": {"type": "uri", "value": "http://test/person/gender"},
                         "range": {"type": "bnode", "value": "nodeID://b72146"}
                        },
                        {"enumerated_value": {"type": "uri", "value": "http://test/person/Gender/Female"},
                         "enumerated_value_label": {"type": "literal", "value": "Feminino", "xml:lang": "pt"},
                         "predicate": {"type": "uri", "value": "http://test/person/gender"},
                         "range": {"type": "bnode", "value": "nodeID://b72146"}
                        }
                    ]}
                }""")
            return fake_response

        schema.query_cardinalities = mock_query_cardinalities
        schema.query_predicates = mock_query_predicates

        response_predicates_and_cardinalities = schema.get_predicates_and_cardinalities(class_uri, class_schema, context)
        expected_predicates_and_cardinalities = {
            u'http://test/person/gender':
                {'comment': u'G\xeanero.',
                 'title': u'Sexo',
                 'enum': [u'http://test/person/Gender/Male', u'http://test/person/Gender/Female'],
                 'graph': u'http://test/person/',
                 'format': 'uri',
                 'maxItems': u'1',
                 'minItems': u'1',
                 'type': 'string',
                 'range': {'graph': u'http://test/person/',
                           '@id': u'http://test/person/Gender',
                           'title': u'G\xeanero da Pessoa'
                           }
                 }
        }
        self.assertEqual(response_predicates_and_cardinalities, expected_predicates_and_cardinalities)
        self.stop()


class AuxiliaryFunctionsTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        prefixes._MAP_SLUG_TO_PREFIX['test'] = 'http://test/person/'
        prefixes._MAP_PREFIX_TO_SLUG['http://test/person/'] = 'test'

    def tearDown(self):
        del prefixes._MAP_SLUG_TO_PREFIX['test']
        del prefixes._MAP_PREFIX_TO_SLUG['http://test/person/']

    def test_extract_min(self):
        binding = [
            {
                u'predicate': {u'type': u'uri',
                               u'value': u'http://test/person/gender'},
                u'range': {u'type': u'uri',
                           u'value': u'http://test/person/Gender'},
                u'min': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                         u'type': u'typed-literal', u'value': u'1'}
            }
        ]
        extracted = _extract_cardinalities(binding)
        expected = {u'http://test/person/gender': {u'http://test/person/Gender': {'minItems': u'1'}}}
        self.assertEqual(extracted, expected)

    def test_extract_max(self):
        binding = [
            {
                u'predicate': {u'type': u'uri',
                               u'value': u'http://test/person/gender'},
                u'range': {u'type': u'uri',
                           u'value': u'http://test/person/Gender'},
                u'max': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                         u'type': u'typed-literal', u'value': u'1'}
            }
        ]
        extracted = _extract_cardinalities(binding)
        expected = {u'http://test/person/gender': {u'http://test/person/Gender': {'maxItems': u'1'}}}
        self.assertEqual(extracted, expected)

    def test_extract_options(self):
        binding = [
            {u'predicate': {u'type': u'uri',
                            u'value': u'http://test/person/gender'},
             u'enumerated_value': {u'type': u'uri',
                                   u'value': u'http://test/person/Gender/Male'},
             u'range': {u'type': u'bnode', u'value': u'nodeID://b72146'},
             u'enumerated_value_label': {u'xml:lang': u'pt', u'type': u'literal',
                                         u'value': u'Masculino'}},
            {u'predicate': {u'type': u'uri',
                            u'value': u'http://test/person/gender'},
             u'enumerated_value': {u'type': u'uri',
                                   u'value': u'http://test/person/Gender/Female'},
             u'range': {u'type': u'bnode', u'value': u'nodeID://b72146'},
             u'enumerated_value_label': {u'xml:lang': u'pt', u'type': u'literal',
                                         u'value': u'Feminino'}}
        ]
        extracted = _extract_cardinalities(binding)
        expected = {u'http://test/person/gender': {
                    'enum': [u'http://test/person/Gender/Male', u'http://test/person/Gender/Female']}}
        self.assertEqual(extracted, expected)

    def test_build_predicate_dict_with_object_property(self):
        expected_predicate_dict = {'comment': u'G\xeanero.',
                                   'range': {'graph': 'test',
                                             '@id': 'test:Gender',
                                             'title': u'G\xeanero da Pessoa'},
                                   'graph': 'test',
                                   'maxItems': u'1',
                                   'format': 'uri',
                                   'minItems': u'1',
                                   'title': u'Sexo',
                                   'enum': [u'http://test/person/Gender/Male',
                                            u'http://test/person/Gender/Female'],
                                   'type': 'string'}
        # params
        name = u'http://test/person/gender'
        predicate = {u'predicate': {u'type': u'uri', u'value': u'http://test/person/gender'},
                     u'range': {u'type': u'uri', u'value': u'http://test/person/Gender'},
                     u'grafo_do_range': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'label_do_range': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'G\xeanero da Pessoa'},
                     u'title': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Sexo'},
                     u'predicate_graph': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'predicate_comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'G\xeanero.'},
                     u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}}
        cardinalities = {u'http://test/person/gender': {'enum': [u'http://test/person/Gender/Male',
                                                                  u'http://test/person/Gender/Female'],
                                                          u'http://test/person/Gender': {'minItems': u'1', 'maxItems': u'1'}}}
        context = prefixes.MemorizeContext()
        context.prefix_to_slug('http://test/person')
        # test call
        effective_predicate_dict = build_predicate_dict(name, predicate, cardinalities, context)
        self.assertEqual(expected_predicate_dict, effective_predicate_dict)

    def test_build_predicate_dict_with_datatype_property(self):
        expected_predicate_dict = {'comment': u'Nome completo da pessoa',
                                   'graph': 'test',
                                   'title': u'Nome',
                                   'type': 'string'}
        # params
        name = u'http://test/person/gender'
        predicate = {u'predicate': {u'type': u'uri', u'value': u'http://test/person/name'},
                     u'range': {u'type': u'uri', u'value': u'http://www.w3.org/2001/XMLSchema#string'},
                     u'title': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nome'},
                     u'grafo_do_range': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'label_do_range': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nome da Pessoa'},
                     u'predicate_graph': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'predicate_comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nome completo da pessoa'},
                     u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'}}
        cardinalities = {}
        context = prefixes.MemorizeContext()
        context.prefix_to_slug('http://test/person')
        # test call
        effective_predicate_dict = build_predicate_dict(name, predicate, cardinalities, context)
        self.assertEqual(expected_predicate_dict, effective_predicate_dict)
#        u'http://semantica.globo.com/person/fullName': {u'http://www.w3.org/2001/XMLSchema#string': {'maxItems': u'1'}},


class AuxiliaryFunctionsTestCase2(unittest.TestCase):

    def setUp(self):
        self.original_query_predicate_with_lang = schema._query_predicate_with_lang
        self.original_query_predicate_without_lang = schema._query_predicate_without_lang

    def tearDown(self):
        schema._query_predicate_with_lang = self.original_query_predicate_with_lang
        schema._query_predicate_without_lang = self.original_query_predicate_without_lang

    def test_query_predicates_successful_with_lang(self):
        response_text = '{"results": {"bindings": [1]}}'

        class ResponseWithBindings():
            body = response_text

        schema._query_predicate_with_lang = lambda class_uri, context: ResponseWithBindings()

        response = schema.query_predicates("class_uri", {})
        self.assertEqual(response.body, response_text)

    def test_query_predicates_successful_without_lang(self):
        response_text = '{"results": {"bindings": []}}'
        response_without_lang_text = '{"results": {"bindings": [1]}}'

        class MockResponse():
            def __init__(self, param):
                self.body = param

        schema._query_predicate_with_lang = lambda class_uri, context: MockResponse(response_text)
        schema._query_predicate_without_lang = lambda class_uri, context: MockResponse(response_without_lang_text)

        response = schema.query_predicates("class_uri", {})
        self.assertEqual(response.body, response_without_lang_text)
