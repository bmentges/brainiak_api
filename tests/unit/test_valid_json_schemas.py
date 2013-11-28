# -*- coding: utf-8 -*-

import unittest
from jsonschema import Draft4Validator, SchemaError
from mock import patch
from brainiak.root import json_schema as root_json_schema
from brainiak.context import json_schema as ctx_json_schema
from brainiak.search import json_schema as search_json_schema
from brainiak.collection import json_schema as collection_json_schema
from brainiak.suggest import json_schema as suggest_json_schema
from brainiak.utils.params import ParamDict
from tests.mocks import MockHandler


class ResultHandlerTestCase(unittest.TestCase):

    def validate_draft4(self, schema):
        self.assertEqual(schema['$schema'], 'http://json-schema.org/draft-04/schema#')
        try:
            Draft4Validator.check_schema(schema)
        except SchemaError as ex:
            self.fail("Json-schema for root is not valid. Failed for {0:s}".format(ex))

    def test_valid_json_schema_for_root(self):
        schema = root_json_schema.schema()
        self.validate_draft4(schema)

    def test_valid_json_schema_for_context(self):
        handler = MockHandler()
        query_params = ParamDict(handler, context_name='glb')
        schema = ctx_json_schema.schema(query_params)
        self.validate_draft4(schema)

    def test_valid_json_schema_for_search(self):
        handler = MockHandler()
        query_params = ParamDict(handler, context_name='glb')
        schema = search_json_schema.schema(context_name='ctx', class_name='klass')
        self.validate_draft4(schema)

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=False)
    @patch("brainiak.collection.json_schema.get_cached_schema", return_value={'title': 'Materia'})
    def test_valid_json_schema_for_collection(self, mock_cached_schema, mock_settings):
        handler = MockHandler()
        query_params = ParamDict(handler, context_name='glb', class_name='Materia', class_prefix='http://semantica.globo.com/base/')
        schema = collection_json_schema.schema(query_params)
        self.validate_draft4(schema)

    def test_valid_suggest_json_schema(self):
        schema = suggest_json_schema.schema()
        self.validate_draft4(schema)
