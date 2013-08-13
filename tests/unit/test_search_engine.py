from unittest import TestCase

from mock import patch

from brainiak.search_engine import _build_elasticsearch_request_url


class SearchEngineTestCase(TestCase):

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "http://esearch.dev.globoi.com")
    def test_build_elasticsearch_request_url_all_none(self):
        expected_url = "http://esearch.dev.globoi.com/semantica.*/_search"
        response = _build_elasticsearch_request_url(None, None)
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "http://esearch.dev.globoi.com")
    def test_build_elasticsearch_request_url_indexes_none(self):
        expected_url = "http://esearch.dev.globoi.com/semantica.*/class_uri_encoded/_search"
        response = _build_elasticsearch_request_url(None, ["class_uri_encoded"])
        self.assertEquals(expected_url, response)


    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "http://esearch.dev.globoi.com")
    def test_build_elasticsearch_request_url_types_none(self):
        expected_url = "http://esearch.dev.globoi.com/semantica.glb/_search"
        response = _build_elasticsearch_request_url(["semantica.glb"], None)
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "http://esearch.dev.globoi.com")
    def test_build_elasticsearch_request_url(self):
        expected_url = "http://esearch.dev.globoi.com/semantica.glb/class_uri_encoded/_search"
        response = _build_elasticsearch_request_url(["semantica.glb"], ["class_uri_encoded"])
        self.assertEquals(expected_url, response)
