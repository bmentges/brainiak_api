import unittest
from mock import patch
from tornado.web import HTTPError
from brainiak.instance.create_instance import create_instance
from brainiak.utils.params import ParamDict
from tests.mocks import MockHandler, mock_schema


class TestCaseInstanceCreateResource(unittest.TestCase):

    @patch("brainiak.instance.create_instance.query_create_instances")
    @patch("brainiak.instance.create_instance.is_insert_response_successful", return_value=False)
    @patch("brainiak.instance.create_instance.get_cached_schema", return_value=mock_schema({"rdfs:label": "string"}))
    @patch("brainiak.utils.sparql.validate_value_uniqueness")
    def test_instance_not_inserted(self, mock_value_uniqueness, mock_get_cached_schema,
                                   mocked_response_successful, mocked_query_create_instances):
        handler = MockHandler()
        params = ParamDict(handler, class_uri="class", graph_uri="graph")
        instance_data = {"http://www.w3.org/2000/01/rdf-schema#label": "teste"}
        self.assertRaises(HTTPError, create_instance, params, instance_data, "http://uri-teste")
