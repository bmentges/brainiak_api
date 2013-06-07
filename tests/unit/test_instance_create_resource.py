import unittest
from mock import patch

from tornado.web import HTTPError

from brainiak.instance.create_resource import create_instance


class TestCaseInstanceCreateResource(unittest.TestCase):

    @patch("brainiak.instance.create_resource.query_create_instances")
    @patch("brainiak.instance.create_resource.is_insert_response_successful", return_value=False)
    def test_instance_not_inserted(self, mocked_response_successful, mocked_query_create_instances):
        query_params = {"class_uri": "class", "graph_uri": "graph"}
        instance_data = {"rdfs:label": "teste"}
        self.assertRaises(HTTPError, create_instance, query_params, instance_data, "http://uri-teste")
