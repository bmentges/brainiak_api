# -*- coding: utf-8 -*-
import json

from brainiak.range_search.range_search import QUERY_PREDICATE_RANGES
from brainiak.utils.sparql import filter_values

from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase

class TestRangeSearch(TornadoAsyncHTTPTestCase):

    def test_range_search_with_required_params(self):
        response = self.fetch('/_range_search?pattern=12&predicate=Override')
        self.assertEqual(response.code, 404)
        #json_received = json.loads(response.body)
        #self.assertEqual(json_received, {})

    def test_range_search_without_required_param_predicate(self):
        response = self.fetch('/_range_search?pattern=12')
        self.assertEqual(response.code, 400)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['error'], "HTTP error: 400\nRequired parameter (predicate) was not given, received just: pattern")

    # def test_range_search_without_required_param_predicate(self):
    #     self.assertRaises(HTTPError, self.fetch, '/_range_search?pattern=12')


class TestQueryPredicatesRange(QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/animalia.n3"]
    graph_uri = "http://example.onto/"

    maxDiff = None

    def test_query_predicate_superclass_range(self):
        expected_classes = ["http://example.onto/Place", "http://example.onto/City"]
        expected_labels = ["Place", "City"]

        query_params = {
            "predicate": "http://example.onto/birthPlace",
            "lang_filter_label_range": ""
        }
        query_response = self.query(QUERY_PREDICATE_RANGES % query_params)
        response_classes = filter_values(query_response, "range")
        response_labels = filter_values(query_response, "label_range")

        self.assertEqual(expected_classes, response_classes)
        self.assertEqual(expected_labels, response_labels)
