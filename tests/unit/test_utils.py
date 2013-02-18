import unittest
from brainiak import utils
from tornado.curl_httpclient import CurlAsyncHTTPClient


class UtilsTestCase(unittest.TestCase):

    def test_async_client(self):
        expected = CurlAsyncHTTPClient()
        result = utils.get_tornado_async_client()
        self.assertEquals(expected, result)
