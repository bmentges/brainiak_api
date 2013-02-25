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


# class AuxiliaryFunctionsTestCase(unittest.TestCase):
#
#     def test_extract_cardinalities(self):
#         cardinalities_from_virtuoso = [
#             {
#                 u'max': {
#                     u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
#                     u'type': u'typed-literal',
#                     u'value': u'1'
#                 },
#                 u'predicate': {
#                     u'type': u'uri',
#                     u'value': u'http://semantica.globo.com/place/partOfState'
#                 },
#                 u'range': {
#                     u'type': u'uri',
#                     u'value': u'http://semantica.globo.com/place/State'
#                 },
#                 u'min': {
#                     u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
#                     u'type': u'typed-literal',
#                     u'value': u'0'
#                 }
#             },
#             {
#                 u'predicate': {
#                     u'type': u'uri',
#                     u'value': u'http://semantica.globo.com/upper/name'},
#                 u'range': {
#                     u'type': u'uri',
#                     u'value': u'http://www.w3.org/2001/XMLSchema#string'},
#                 u'min': {
#                     u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
#                     u'type': u'typed-literal',
#                     u'value': u'1'}}]
#         extracted = _extract_cardinalities(cardinalities_from_virtuoso)
#         expected = None
#         self.assertEquals(extracted, expected)
