# -*- coding: utf-8 -*-
import json
from urllib import quote_plus

import requests

from mock import patch

from brainiak.suggest.suggest import QUERY_PREDICATE_RANGES, \
    QUERY_SUBPROPERTIES
from brainiak.utils.sparql import filter_values
from brainiak import settings

from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class TestRangeSearch(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/animalia.n3"]
    graph_uri = "http://example.onto/"

    retries = 3
    sleep_between_retries = 1000

    maxDiff = None

    VALID_BODY_PARAMS = {'pattern': 'york', 'predicate': 'http://example.onto/birthPlace'}

    def setUp(self):
        super(TestRangeSearch, self).setUp()
        # ONLY VALID FOR VALID_BODY_PARAMS
        self.elastic_request_url = "http://" + settings.ELASTICSEARCH_ENDPOINT + "/example.onto/"
        self.elastic_request_url += quote_plus("http://example.onto/City") + "/"
        self.elastic_request_url += quote_plus("http://example.onto/York")
        entry = {
            "http://www.w3.org/2000/01/rdf-schema#label": "York"
        }

        requests.put(self.elastic_request_url + "?refresh=true", data=json.dumps(entry))

    def tearDown(self):
        super(TestRangeSearch, self).setUp()
        requests.delete(self.elastic_request_url)

    def test_request_with_invalid_predicate(self):
        INVALID_PARAMS = {'pattern': 'york', 'predicate': 'http://example.onto/invalidPredicate'}
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps(INVALID_PARAMS))
        self.assertEqual(response.code, 400)
        expected_error_msg = "HTTP error: 400\nEither the predicate http://example.onto/invalidPredicate does not exists or it does not have any rdfs:range defined in the triplestore"
        json_received = json.loads(response.body)
        self.assertIn(expected_error_msg, json_received['errors'])

    @patch("brainiak.suggest.suggest._graph_uri_to_index_name", return_value="example.onto")
    def test_successful_request(self, mocked_graph_uri_to_index_name):
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps(self.VALID_BODY_PARAMS))
        self.assertEqual(response.code, 200)
        #self.assertEqual(json_received, {})

    @patch("brainiak.suggest.suggest._graph_uri_to_index_name", return_value="example.onto")
    def test_zero_results(self, mocked_graph_uri_to_index_name):
        zero_results_parameters = {
            "predicate": "http://example.onto/birthPlace",
            "pattern": "non existent keywords"
        }
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps(zero_results_parameters))
        self.assertEqual(response.code, 404)

    def test_suggest_without_required_param_predicate(self):
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps({'pattern': 1}))
        self.assertEqual(response.code, 400)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['errors'][0], "HTTP error: 400\nRequired parameter (predicate) was not given.")

    def test_suggest_with_invalid_body_param(self):
        d = {'invalid': 3}
        d.update(self.VALID_BODY_PARAMS)
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps(d))
        self.assertEqual(response.code, 400)
        json_received = json.loads(response.body)
        self.assertIn("Argument invalid is not supported", json_received['errors'][0])

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
