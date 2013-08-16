# -*- coding: utf-8 -*-
import json

from brainiak.range_search.range_search import QUERY_PREDICATE_RANGES, \
    QUERY_SUBPROPERTIES
from brainiak.utils.sparql import filter_values

from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class TestRangeSearch(TornadoAsyncHTTPTestCase):

    def test_without_required_params(self):
        response = self.fetch('/_range_search',
                              method='POST',
                              body=json.dumps({'pattern': '', 'predicate':'base:cita_a_entidade'}))
        self.assertEqual(response.code, 400)
        #json_received = json.loads(response.body)
        #self.assertEqual(json_received, {})

    def test_range_search_without_required_param_predicate(self):
        response = self.fetch('/_range_search?pattern=12',
                              method='POST',
                              body=json.dumps({'pattern':1}))
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
        expected_graphs = ["http://example.onto/", "http://example.onto/"]

        query_params = {
            "predicate": "http://example.onto/birthPlace",
            "lang_filter_range_label": ""
        }
        query_response = self.query(QUERY_PREDICATE_RANGES % query_params)
        response_classes = filter_values(query_response, "range")
        response_labels = filter_values(query_response, "range_label")
        response_graphs = filter_values(query_response, "range_graph")

        self.assertEqual(expected_classes, response_classes)
        self.assertEqual(expected_labels, response_labels)
        self.assertEqual(expected_graphs, response_graphs)

    def test_query_subproperties(self):
        expected = ["http://example.onto/birthCity"]
        query_response = self.query(QUERY_SUBPROPERTIES % "http://example.onto/birthPlace")
        response = filter_values(query_response, "property")
        self.assertEqual(expected, response)
