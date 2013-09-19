# -*- coding: utf-8 -*-

import unittest
from jsonschema import Draft3Validator, SchemaError
from brainiak.root import json_schema as root_json_schema
from brainiak.context import json_schema as ctx_json_schema
from brainiak.collection import json_schema as collection_json_schema
from brainiak.suggest import json_schema as suggest_json_schema


class ResultHandlerTestCase(unittest.TestCase):

    def validate_draft3(self, schema):
        self.assertEqual(schema['$schema'], 'http://json-schema.org/draft-03/schema#')
        try:
            Draft3Validator.check_schema(schema)
        except SchemaError as ex:
            self.fail("Json-schema for root is not valid. Failed for {0:s}".format(ex))

    def test_valid_json_schema_for_root(self):
        schema = root_json_schema.schema()
        self.validate_draft3(schema)

    def test_valid_json_schema_for_context(self):
        schema = ctx_json_schema.schema('glb')
        self.validate_draft3(schema)

    def test_valid_json_schema_for_collection(self):
        schema = collection_json_schema.schema('glb', 'Materia', 'http://semantica.globo.com/base/')
        self.validate_draft3(schema)

    def test_valid_suggest_json_schema(self):
        schema = suggest_json_schema.schema()
        self.validate_draft3(schema)
