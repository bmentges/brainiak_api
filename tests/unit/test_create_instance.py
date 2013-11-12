import json
import unittest

from mock import patch
from tornado.web import HTTPError

from brainiak.instance.create_instance import create_instance
from brainiak.utils.params import ParamDict
from tests.mocks import MockHandler, mock_schema


class TestCaseInstanceCreateResource(unittest.TestCase):

    @patch("brainiak.utils.sparql.property_must_map_a_unique_value", return_value=True)
    @patch("brainiak.instance.create_instance.query_create_instances")
    @patch("brainiak.instance.create_instance.is_insert_response_successful", return_value=False)
    @patch("brainiak.instance.create_instance.get_cached_schema", return_value=mock_schema({"rdfs:label": "string"}, id="http://somedomain/class"))
    @patch("brainiak.utils.sparql.is_value_unique", return_value=False)
    def test_instance_not_inserted(self, mock_value_uniqueness, mock_get_cached_schema,
                                   mocked_response_successful, mocked_query_create_instances,
                                   mocked_property_must_map_a_unique_value):
        handler = MockHandler()
        params = ParamDict(handler, class_uri="http://somedomain/class", graph_uri="http://somedomain/graph")
        instance_data = {"http://www.w3.org/2000/01/rdf-schema#label": "teste"}
        with self.assertRaises(HTTPError) as e:
            create_instance(params, instance_data, "http://uri-teste")
            expected = ["The property (http://www.w3.org/2000/01/rdf-schema#label) defined in the schema (http://somedomain/class) must map a unique value. The value provided (teste) is already used by another instance."]
            self.assertEqual(json.loads(str(e.exception)), expected)
