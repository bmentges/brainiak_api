from mock import patch
from unittest import TestCase

from tornado.web import HTTPError

from brainiak.stored_query import execute


class StoredQueryExecuteTestCase(TestCase):

    def test_get_query_with_valid_params_in_request(self):
        expected = "SELECT ?s FROM <http://my_graph.com/> {?s a owl:Class}"
        stored_query = {
            "sparql_template": "SELECT ?s FROM <%(graph_uri)s> {?s a owl:Class}"
        }
        class QueryStringParams(object):
            arguments = {"graph_uri": "http://my_graph.com/"}

        response = execute.get_query(stored_query, QueryStringParams())
        self.assertEqual(expected, response)

    @patch("brainiak.stored_query.execute._", return_value="msg")
    def test_get_query_with_missing_param_in_request(self, mocked_i18n_message):
        stored_query = {
            "sparql_template": "SELECT ?s FROM <%(graph_uri)s> {?s a owl:Class}"
        }
        class QueryStringParams(object):
            arguments = {"a": "an_invalid_param"}

        self.assertRaises(HTTPError,
                          execute.get_query,
                          stored_query,
                          QueryStringParams())
