from unittest import TestCase
from mock import patch

from brainiak.search.search import do_search_query


class SearchUnitTestCase(TestCase):

    @patch("brainiak.search.search.uri_to_slug", return_value="example.onto")
    @patch("brainiak.search.search.run_search")
    def test_do_search_query(self, mock_run_search, mock_uri_to_slug):
        search_fields = ["http://www.w3.org/2000/01/rdf-schema#label"]
        query_params = {
            "graph_uri": "http://example.onto/",
            "class_uri": "http://example.onto/City",
            "pattern": "Yo",  # dawg
        }
        expected_query = {
            "filter": {
                "type": {
                    "value": "http://example.onto/City"
                }
            },
            "query": {
                "query_string": {
                    "fields": ["http://www.w3.org/2000/01/rdf-schema#label"],
                    "query": "*Yo*"
                }
            },
            "from": 0,
            "size": 10,
        }

        do_search_query(query_params, search_fields)
        mock_run_search.assert_called_with(expected_query, indexes=["semantica.example.onto"])
