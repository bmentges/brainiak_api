# -*- coding: utf-8 -*-

import json
import unittest
from tornado import gen
import mock

from brainiak.resource import schema
from brainiak import prefixes
from brainiak.resource.schema import _extract_cardinalities, build_predicate_dict
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

    @gen.engine
    def test_query_get_schema(self):
        expected_response = {
            "schema": {
                'class': 'http://test.domain.com/test_context/test_class',
                'comment': False,
                'label': False,
                'predicates': None
            }
        }

        # Mocks
        def mock_query_class_schema(class_uri, remember, callback):
            class_schema = {"results": {"bindings": [{"dummy_key": "dummy_value"}]}}
            tornado_response = MockResponse(class_schema)
            callback(tornado_response, remember)

        schema.query_class_schema = mock_query_class_schema

        def mock_get_predicates_and_cardinalities(class_uri, class_schema, remember, callback):
            callback(class_schema, None)

        schema.get_predicates_and_cardinalities = mock_get_predicates_and_cardinalities

        response = yield gen.Task(schema.get_schema, "test_context", "test_class")

        schema_response = response["schema"]
        self.assertIn("title", schema_response)
        self.assertIn("type", schema_response)
        self.assertIn("@id", schema_response)
        self.assertIn("properties", schema_response)
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

    @gen.engine
    def test_get_predicates_and_cardinalities(self):
        context = prefixes.MemorizeContext()
        class_uri = "http://test/person/gender"
        class_schema = None

        # Mocks
        def mock_query_predicates(class_uri, context, callback):
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
            callback(fake_response, context)

        def mock_query_cardinalities(class_uri, class_schema, final_callback, context, callback):
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
                        {"enumerated_value": {"type": "uri", "value": "http://test/data/Gender/Male"},
                         "enumerated_value_label": {"type": "literal", "value": "Masculino", "xml:lang": "pt"},
                         "predicate": {"type": "uri", "value": "http://test/person/gender"},
                         "range": {"type": "bnode", "value": "nodeID://b72146"}
                        },
                        {"enumerated_value": {"type": "uri", "value": "http://test/data/Gender/Female"},
                         "enumerated_value_label": {"type": "literal", "value": "Feminino", "xml:lang": "pt"},
                         "predicate": {"type": "uri", "value": "http://test/person/gender"},
                         "range": {"type": "bnode", "value": "nodeID://b72146"}
                        }
                    ]}
                }""")
            callback(fake_response, class_schema, final_callback, context)

        schema.query_cardinalities = mock_query_cardinalities
        schema.query_predicates = mock_query_predicates

        response = yield gen.Task(schema.get_predicates_and_cardinalities,
                                  class_uri, class_schema, context)
        response_class_schema, response_predicates_and_cardinalities = response.args
        expected_predicates_and_cardinalities = {
            u'http://test/person/gender':
                {'comment': u'G\xeanero.',
                 'title': u'Sexo',
                 'enum': [u'http://test/data/Gender/Male', u'http://test/data/Gender/Female'],
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
        self.assertEquals(response_class_schema, class_schema)
        self.assertEquals(response_predicates_and_cardinalities, expected_predicates_and_cardinalities)


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
        self.assertEquals(extracted, expected)

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
        self.assertEquals(extracted, expected)

    def test_extract_options(self):
        binding = [
            {u'predicate': {u'type': u'uri',
                            u'value': u'http://test/person/gender'},
             u'enumerated_value': {u'type': u'uri',
                                   u'value': u'http://test/data/Gender/Male'},
             u'range': {u'type': u'bnode', u'value': u'nodeID://b72146'},
             u'enumerated_value_label': {u'xml:lang': u'pt', u'type': u'literal',
                                         u'value': u'Masculino'}},
            {u'predicate': {u'type': u'uri',
                            u'value': u'http://test/person/gender'},
             u'enumerated_value': {u'type': u'uri',
                                   u'value': u'http://test/data/Gender/Female'},
             u'range': {u'type': u'bnode', u'value': u'nodeID://b72146'},
             u'enumerated_value_label': {u'xml:lang': u'pt', u'type': u'literal',
                                         u'value': u'Feminino'}}
        ]
        extracted = _extract_cardinalities(binding)
        expected = {u'http://test/person/gender': {
                    'enum': [u'http://test/data/Gender/Male', u'http://test/data/Gender/Female']}}
        self.assertEquals(extracted, expected)

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
                                   'enum': [u'http://test/data/Gender/Male',
                                            u'http://test/data/Gender/Female'],
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
        cardinalities = {u'http://test/person/gender': {'enum': [u'http://test/data/Gender/Male',
                                                                  u'http://test/data/Gender/Female'],
                                                          u'http://test/person/Gender': {'minItems': u'1', 'maxItems': u'1'}}}
        context = prefixes.MemorizeContext()
        context.prefix_to_slug('http://test/person')
        # test call
        effective_predicate_dict = build_predicate_dict(name, predicate, cardinalities, context)
        self.assertEquals(expected_predicate_dict, effective_predicate_dict)

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
        self.assertEquals(expected_predicate_dict, effective_predicate_dict)
#        u'http://semantica.globo.com/person/fullName': {u'http://www.w3.org/2001/XMLSchema#string': {'maxItems': u'1'}},


class AuxiliaryFunctionsTestCase2(unittest.TestCase):

    def setUp(self):
        self.original_query_predicate_with_lang = schema._query_predicate_with_lang
        self.original_query_predicate_without_lang = schema._query_predicate_without_lang

    def tearDown(self):
        schema._query_predicate_with_lang = self.original_query_predicate_with_lang
        schema._query_predicate_without_lang = self.original_query_predicate_without_lang

    def test_query_predicates_successful_with_lang(self):

        callback_stack = []

        def first_callback(tornado_response, context):
            callback_stack.append(1)

        class ResponseWithBindings():
            body = '{"results": {"bindings": [1]}}'

        class ResponseMock():
            args = [ResponseWithBindings(), {}]

        schema._query_predicate_with_lang = lambda class_uri, context, callback: callback(ResponseMock())

        schema.query_predicates("class_uri", {}, first_callback)
        self.assertEquals(callback_stack, [1])

    def test_query_predicates_successful_without_lang(self):

        callback_stack = []

        def first_callback(tornado_response, context=None):
            callback_stack.append(1)

        class ResponseWithoutBindings():
            body = '{"results": {"bindings": []}}'

        class ResponseToQueryWithLang():
            args = [ResponseWithoutBindings(), {}]

        class ResponseToQueryWithoutLang():
            def __init__(self):
                callback_stack.append(2)
                self.args = [ResponseWithoutBindings(), {}]

        schema._query_predicate_with_lang = lambda class_uri, context, callback: callback(ResponseToQueryWithLang())
        schema._query_predicate_without_lang = lambda class_uri, context, callback: callback(ResponseToQueryWithoutLang())

        schema.query_predicates("class_uri", {}, first_callback)
        self.assertEquals(callback_stack, [2, 1])
