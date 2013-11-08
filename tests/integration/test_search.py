import json
from unittest import TestCase
from urllib import quote_plus

import requests

from brainiak import settings


class SearchIntegrationTestCase(TestCase):

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

    def test_successful_search(self):
        pass

    def test_search_not_found(self):
        pass
