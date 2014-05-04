from brainiak.utils.sparql import QUERY_VALUE_EXISTS, is_result_true
from tests.sparql import QueryTestCase


class ValidateUniquenessTestCase(QueryTestCase):

    graph_uri = "http://example_alternative.onto/"
    fixtures_by_graph = {
        graph_uri: ["tests/sample/animalia.n3"]
    }
    maxDiff = None

    def test_query(self):
        query_params = {
            "graph_uri": self.graph_uri,
            "class_uri": "http://example.onto/City",
            "instance_uri": "http://example.onto/York",
            "predicate_uri": "http://example.onto/nickname",
            "object_value": '"City of York"'
        }
        query = QUERY_VALUE_EXISTS % query_params
        query_result = self.query(query)
        self.assertTrue(is_result_true(query_result))

    def test_query_answer_false(self):
        query_params = {
            "graph_uri": self.graph_uri,
            "class_uri": "http://example.onto/City",
            "instance_uri": "http://example.onto/York",
            "predicate_uri": "http://example.onto/nickname",
            "object_value": '"Unexistent value"'
        }
        query = QUERY_VALUE_EXISTS % query_params
        query_result = self.query(query)
        self.assertFalse(is_result_true(query_result))
