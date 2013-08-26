from unittest import TestCase

from mock import patch

from brainiak.search_engine import _build_elasticsearch_request_url


class SearchEngineTestCase(TestCase):

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.dev.globoi.com")
    def test_build_elasticsearch_request_url_all_none(self):
        expected_url = "http://esearch.dev.globoi.com/semantica.*/_search"
        response = _build_elasticsearch_request_url(None)
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.dev.globoi.com")
    def test_build_elasticsearch_request_url(self):
        expected_url = "http://esearch.dev.globoi.com/semantica.glb/_search"
        response = _build_elasticsearch_request_url(["semantica.glb"])
        self.assertEquals(expected_url, response)
