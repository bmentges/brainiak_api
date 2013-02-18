# coding: utf-8

import unittest
from mock import patch
from brainiak import triplestore


class TriplestoreWithFullUrlTestCase(unittest.TestCase):

    @patch('brainiak.triplestore.settings', SPARQL_ENDPOINT_HOST="http://myhost", SPARQL_ENDPOINT_PORT=8080)
    def test_endpoint_host_and_port_defined_in_settings(self, settings):
        del settings.SPARQL_ENDPOINT_FULL_URL

        expected = "http://myhost:8080/sparql"
        virtuoso_connection = triplestore.VirtuosoConnection()
        result = virtuoso_connection.endpoint_url
        self.assertEquals(expected, result)

    @patch('brainiak.triplestore.settings', SPARQL_ENDPOINT_FULL_URL="http://myhost:8080/sparql")
    def test_endpoint_full_url_defined_in_settings(self, settings):
        expected = "http://myhost:8080/sparql"
        virtuoso_connection = triplestore.VirtuosoConnection()
        result = virtuoso_connection.endpoint_url
        self.assertEquals(expected, result)
