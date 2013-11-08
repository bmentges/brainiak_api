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
        response = self.fetch('/_search?pattern=yo' +
                   '&graph_uri=http://example.onto/' +
                   '&class_uri=http://example.onto/City')

    def test_search_not_found(self):
        pass
