import json
from mock import patch

from brainiak.handlers import RootJsonSchemaHandler
from tests.tornado_cases import TornadoAsyncHTTPTestCase


def raise_exception():
    raise Exception


class ListAllContextsTestCase(TornadoAsyncHTTPTestCase):

    def setUp(self):
        super(ListAllContextsTestCase, self).setUp()

    def tearDown(self):
        super(ListAllContextsTestCase, self).tearDown()

    def test_root_handler_allows_purge(self):
        self.assertIn("PURGE", RootJsonSchemaHandler.SUPPORTED_METHODS)

    @patch("brainiak.handlers.logger")
    def test_400(self, log):
        response = self.fetch("/_schema_list/?invalid_param=xubiru", method='GET')
        self.assertEqual(response.code, 400)
        body = json.loads(response.body)
        self.assertIn(u'Argument invalid_param is not supported. The supported ', body["errors"][0])

    @patch("brainiak.handlers.logger")
    @patch("brainiak.handlers.memoize", return_value={"body": {'items': []}, "meta": {"cache": "", "last_modified": ""}})
    def test_200_cached(self, mocked_memoize, log):
        response = self.fetch("/_schema_list/", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEquals(body["items"], [])

    def test_200(self):
        # disclaimer: this test assumes UPPER graph exists in Virtuoso and contains triples
        response = self.fetch("/_schema_list/", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body["$schema"], u'http://json-schema.org/draft-04/schema#')
        self.assertEqual(body["title"], u'Root Schema that lists all contexts')

    @patch("brainiak.utils.cache.retrieve", return_value={"body": {"status": "cached"}, "meta": {"last_modified": "Fri, 11 May 1984 20:00:00 -0300"}})
    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_200_with_cache(self, enable_cache, retrieve):
        response = self.fetch("/_schema_list/", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body, {'status': "cached"})
        self.assertTrue(response.headers['X-Cache'].startswith('HIT from localhost'))
