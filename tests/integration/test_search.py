import json
from urllib import quote_plus
from mock import patch

from tests.tornado_cases import TornadoAsyncHTTPTestCase
import requests

from brainiak import settings


class SearchIntegrationTestCase(TornadoAsyncHTTPTestCase):

    def setUp(self):
        super(SearchIntegrationTestCase, self).setUp()
        self.elastic_request_url = "http://" + settings.ELASTICSEARCH_ENDPOINT + "/semantica.example.onto/"
        self.elastic_request_url += quote_plus("http://example.onto/City") + "/"
        self.elastic_request_url += quote_plus("http://example.onto/York")
        entry = {
            "http://www.w3.org/2000/01/rdf-schema#label": "York",
            "http://example.onto/nickname": "City of York",
            "http://example.onto/description": "York is a walled city, situated at the confluence of the Rivers Ouse and Foss in North Yorkshire, England."
        }

        requests.put(self.elastic_request_url + "?refresh=true", data=json.dumps(entry))

    def tearDown(self):
        super(SearchIntegrationTestCase, self).setUp()
        requests.delete(self.elastic_request_url)

    @patch("brainiak.search.search.uri_to_slug", return_value="example.onto")
    def test_successful_search(self, mock_uri_to_slug):
        expected_answer_dict = {
            u'@context': {u'@language': u'pt'},
            u'_class_name': u'City',
            u'_class_prefix': u'http://example.onto/',
            u'_class_uri': u'http://example.onto/City',
            u'_context_name': u'example.onto',
            u'_graph_uri': u'http://example.onto/',
            u'_first_args': u'pattern=york&graph_uri=http://example.onto/&page=1&class_uri=http://example.onto/City',
            u'_next_args': u'pattern=york&graph_uri=http://example.onto/&page=2&class_uri=http://example.onto/City',
            u'items': [
                {u'@id': u'http://example.onto/York', u'title': u'York'}
            ],
            u'pattern': u'york'
        }
        response = self.fetch('/_search?pattern=york' +
                              '&graph_uri=http://example.onto/' +
                              '&class_uri=http://example.onto/City')
        self.assertEqual(response.code, 200)
        response_dict = json.loads(response.body)
        del response_dict["_base_url"]  # This varies from request to request locally because tornado bind a random port
        self.assertEqual(sorted(response_dict), sorted(expected_answer_dict))

    @patch("brainiak.search.search.uri_to_slug", return_value="example.onto")
    def test_successful_fuzzy_search(self, mock_uri_to_slug):
        expected_answer_dict = {
            u'@context': {u'@language': u'pt'},
            u'_class_name': u'City',
            u'_class_prefix': u'http://example.onto/',
            u'_class_uri': u'http://example.onto/City',
            u'_context_name': u'example.onto',
            u'_graph_uri': u'http://example.onto/',
            u'_first_args': u'pattern=yo&graph_uri=http://example.onto/&page=1&class_uri=http://example.onto/City',
            u'_next_args': u'pattern=yo&graph_uri=http://example.onto/&page=2&class_uri=http://example.onto/City',
            u'items': [
                {u'@id': u'http://example.onto/York', u'title': u'York'}
            ],
            u'pattern': u'yo'
        }
        response = self.fetch('/_search?pattern=yo' +
                              '&graph_uri=http://example.onto/' +
                              '&class_uri=http://example.onto/City')
        self.assertEqual(response.code, 200)
        response_dict = json.loads(response.body)
        del response_dict["_base_url"]  # This varies from request to request locally because tornado bind a random port
        self.assertEqual(sorted(response_dict), sorted(expected_answer_dict))

    @patch("brainiak.search.search.uri_to_slug", return_value="example.onto")
    def test_search_not_found(self, mock_uri_to_slug):
        expected_items = {}
        response = self.fetch('/_search?pattern=non_existent_pattern' +
                              '&graph_uri=http://example.onto/' +
                              '&class_uri=http://example.onto/City')
        response_dict = json.loads(response.body)
        self.assertEqual(response.code, 200)
        response_items = response_dict["items"]
        self.assertEqual(expected_items, response_items)

    def test_search_with_missing_parameters(self):
        response = self.fetch('/_search')
        self.assertEqual(response.code, 400)
        error_message = response.body
        self.assertEqual(error_message, '{"errors": ["HTTP error: 400\\nRequired parameter (pattern) was not given."]}')
