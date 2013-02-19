# coding: utf-8
from mock import patch

import tornado
from tornado.testing import AsyncTestCase
from tornado.ioloop import IOLoop

from brainiak import triplestore



class TriplestoreTestCase(AsyncTestCase):

    def setUp(self):
        self.io_loop = self.get_new_ioloop()

    def tearDown(self):
        if (not IOLoop.initialized() or self.io_loop is not IOLoop.instance()):
            self.io_loop.close(all_fds=True)
        super(AsyncTestCase, self).tearDown()

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
