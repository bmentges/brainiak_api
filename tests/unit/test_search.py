from unittest import TestCase
from mock import patch

from brainiak.search.search import do_search_query, _build_items


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

    def test_build_items(self):
        expected_items = [
            {
                "@id": "http://example.onto/Brazil",
                "title": u"Brazil"
            }
        ]
        elasticsearch_result = {
            u'hits': {
                u'hits': [{
                    u'_index': u'semantica.glb',
                    u'_type': u'http://example.onto/Country',
                    u'_id': u'http://example.onto/Brazil',
                    u'_score': 1.0,
                    u'_source': {
                        u'http://www.w3.org/2000/01/rdf-schema#label': u'Brazil'
                    },
                }],
                u'total': 1,
                u'max_score': 1.0
            },
        }
        items = _build_items(elasticsearch_result)
        self.assertEqual(expected_items, items)
