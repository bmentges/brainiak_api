# coding: utf-8
from mock import patch

import tornado

from brainiak import triplestore
from tests import TornadoAsyncTestCase


class TriplestoreInitTestCase(TornadoAsyncTestCase):

    @patch('brainiak.triplestore.settings', SPARQL_ENDPOINT_HOST="http://myhost", SPARQL_ENDPOINT_PORT=8080)
    def test_init_connection_endpoint_host_and_port_defined_in_settings(self, settings):
        del settings.SPARQL_ENDPOINT_FULL_URL

        expected = "http://myhost:8080/sparql"
        virtuoso_connection = triplestore.VirtuosoConnection()
        result = virtuoso_connection.endpoint_url
        self.assertEquals(expected, result)

    @patch('brainiak.triplestore.settings', SPARQL_ENDPOINT_FULL_URL="http://myhost:8080/sparql")
    def test_init_connection_endpoint_full_url_defined_in_settings(self, settings):
        expected = "http://myhost:8080/sparql"
        virtuoso_connection = triplestore.VirtuosoConnection()
        result = virtuoso_connection.endpoint_url
        self.assertEquals(expected, result)

    @patch('tornado.ioloop.IOLoop', am_i_a_mock=True)
    def test_init_connection_io_loop_as_a_param(self, io_loop):
        virtuoso_connection = triplestore.VirtuosoConnection(io_loop)
        self.assertTrue(virtuoso_connection.io_loop.am_i_a_mock)

    def test_init_connection_io_loop_default(self):
        virtuoso_connection = triplestore.VirtuosoConnection()
        self.assertTrue(isinstance(virtuoso_connection.io_loop, tornado.ioloop.IOLoop))


class TriplestoreSetCredentialsTestCase(TornadoAsyncTestCase):

    @patch('brainiak.triplestore.settings')
    def test_set_credentials_no_auth_settings_at_all(self, settings):
        del settings.SPARQL_ENDPOINT_USER
        del settings.SPARQL_ENDPOINT_PASSWORD
        del settings.SPARQL_ENDPOINT_AUTH_MODE

        virtuoso_connection = triplestore.VirtuosoConnection()
        credentials = (virtuoso_connection.user, virtuoso_connection.password, virtuoso_connection.auth_mode)
        self.assertTrue(all([x is None for x in credentials]))

    @patch('brainiak.triplestore.settings')
    def test_set_credentials_no_password(self, settings):
        del settings.SPARQL_ENDPOINT_PASSWORD

        virtuoso_connection = triplestore.VirtuosoConnection()
        credentials = (virtuoso_connection.user, virtuoso_connection.password, virtuoso_connection.auth_mode)
        self.assertTrue(all([x is None for x in credentials]))
