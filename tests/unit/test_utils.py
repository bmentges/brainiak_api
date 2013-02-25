import unittest
from mock import patch

from tornado.curl_httpclient import CurlAsyncHTTPClient

from brainiak import utils


class UtilsTestCase(unittest.TestCase):

    def test_async_client_is_curl_async_http_client(self):
        expected = CurlAsyncHTTPClient()
        result = utils.get_tornado_async_client()
        self.assertEquals(CurlAsyncHTTPClient, type(result))

    @patch('tornado.ioloop.IOLoop', am_i_a_mock=True)
    def test_async_client_with_ioloop(self, io_loop):
        client = utils.get_tornado_async_client(io_loop)
        self.assertTrue(client.io_loop.am_i_a_mock)
