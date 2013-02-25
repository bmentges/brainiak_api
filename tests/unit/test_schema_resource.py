# -*- coding: utf-8 -*-

import json
import unittest
from tornado import gen

from tornado.testing import AsyncTestCase
from tornado.ioloop import IOLoop

from brainiak import schema_resource
from brainiak.schema_resource import _extract_cardinalities
from tests import TornadoAsyncTestCase


class MockResponse(object):
    def __init__(self, body):
        self.body = json.dumps(body)


class GetSchemaTestCase(TornadoAsyncTestCase):
    def setUp(self):
        self.io_loop = self.get_new_ioloop()
        self.original_query_class_schema = schema_resource.query_class_schema
        self.original_get_predicates_and_cardinalities = schema_resource.get_predicates_and_cardinalities

    def tearDown(self):
        if (not IOLoop.initialized() or self.io_loop is not IOLoop.instance()):
            self.io_loop.close(all_fds=True)
        super(AsyncTestCase, self).tearDown()
        schema_resource.query_class_schema = self.original_query_class_schema
        schema_resource.get_predicates_and_cardinalities = self.original_get_predicates_and_cardinalities

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

        schema_resource.query_class_schema = mock_query_class_schema

        def mock_get_predicates_and_cardinalities(class_uri, class_schema, remember, callback):
            callback(class_schema, None)

        schema_resource.get_predicates_and_cardinalities = mock_get_predicates_and_cardinalities

        response = yield gen.Task(schema_resource.get_schema, "test_context", "test_class")

        schema = response["schema"]
        self.assertIn("title", schema)
        self.assertIn("type", schema)
        self.assertIn("@id", schema)
        self.assertIn("properties", schema)
        # FIXME: enhance the structure of the response
        self.stop()


class AuxiliaryFunctionsTestCase(unittest.TestCase):

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
