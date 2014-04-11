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

    @patch("brainiak.stored_query.execute.compress_keys_and_values",
           return_value=[])
    @patch("brainiak.stored_query.execute.query_sparql")
    @patch("brainiak.stored_query.execute.get_query",
           return_value="SELECT ?s FROM <http://my_graph.com/> {?s a owl:Class}")
    def test_execute_query_with_no_results(self,
                                          mock_get_query,
                                          mock_query_sparql,
                                          mock_compress):
        query_id = "query_id"
        stored_query = {
            "sparql_template": "SELECT ?s FROM <%(graph_uri)s> {?s a owl:Class}"
        }

        class QueryStringParams(object):
            arguments = {"graph_uri": "http://my_graph.com/"}
            triplestore_config = {
                "app_name": "my_app",
                "query_id": "id",
                "url": "url",
                "query": "query"
            }

        expected_query = stored_query["sparql_template"] % {
            "graph_uri": QueryStringParams().arguments["graph_uri"],
        }
        expected_response = {
            "items": [],
            "warning": "The query returned no results. SPARQL endpoint [{0}]\n  Query: {1}".format("url", expected_query)
        }

        response = execute.execute_query(query_id, stored_query, QueryStringParams())
        self.assertEqual(expected_response, response)
