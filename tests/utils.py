import unittest
import urlparse


class URLTestCase(unittest.TestCase):

    def assertQueryStringArgsEqual(self, querystring1, querystring2):

        if isinstance(querystring1, str) or isinstance(querystring1, unicode):
            querystring1 = urlparse.parse_qs(querystring1)

        if isinstance(querystring2, str) or isinstance(querystring2, unicode):
            querystring2 = urlparse.parse_qs(querystring2)

        self.assertDictEqual(querystring1, querystring2)
