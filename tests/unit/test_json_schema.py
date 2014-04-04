from mock import patch
from unittest import TestCase

from jsonschema import ValidationError
from tornado.web import HTTPError

from brainiak.utils.json_schema import validate_json_schema


class JSONSchemaTestCase(TestCase):

    JSON_SCHEMA_EXAMPLE = {
            "type": "object",
            "required": ["items"], 
            "properties": {
                "items": {"type": "array"}
            }
    }

    @patch("brainiak.utils.json_schema.validate")
    def test_valid_json_schema(self, mocked_validate):
        valid_json = {"items": []}
        validate_json_schema(valid_json,
            self.JSON_SCHEMA_EXAMPLE)

    @patch("brainiak.utils.json_schema.validate", side_effect=ValidationError("aa"))
    def test_invalid_json_schema(self, mocked_validate):
        valid_json = {"items": {}}  # not an array
        self.assertRaises(HTTPError,
                          validate_json_schema,
                          valid_json,
                          self.JSON_SCHEMA_EXAMPLE)
