import json
from mock import patch
from brainiak.prefixes import ROOT_CONTEXT

from brainiak.root.get_root import QUERY_LIST_CONTEXT
from brainiak.utils import sparql
from brainiak.handlers import RootHandler
from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


def raise_exception():
    raise Exception


class ListAllContextsTestCase(TornadoAsyncHTTPTestCase):

    def setUp(self):
        self.original_filter_values = sparql.filter_values
        super(ListAllContextsTestCase, self).setUp()

    def tearDown(self):
        sparql.filter_values = self.original_filter_values
        super(ListAllContextsTestCase, self).tearDown()

    def test_root_handler_allows_purge(self):
        self.assertIn("PURGE", RootHandler.SUPPORTED_METHODS)

    @patch("brainiak.handlers.logger")
    def test_400(self, log):
        sparql.filter_values = lambda a, b: []
        response = self.fetch("/?best_aikido_move=ki_projection", method='GET')
        self.assertEqual(response.code, 400)
        body = json.loads(response.body)
        self.assertIn(u'Argument best_aikido_move is not supported. The supported ', body["errors"][0])

    @patch("brainiak.handlers.logger")
    def test_404(self, log):
        sparql.filter_values = lambda a, b: []
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 404)
        body = json.loads(response.body)
        self.assertEquals(body["errors"], [u'HTTP error: 404\nNo contexts were found.'])

    @patch("brainiak.handlers.logger")
    def test_500(self, log):
        sparql.filter_values = lambda a, b: raise_exception()
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 500)
        body = json.loads(response.body)
        self.assertIn("raise Exception\n\nException\n", body["errors"][0])

    def test_200(self):
        # disclaimer: this test assumes UPPER graph exists in Virtuoso and contains triples
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)

        keys = body.keys()
        self.assertEqual(len(keys), 4)
        self.assertIn("items", keys)
        self.assertIn('_base_url', keys)
        self.assertIn('_first_args', keys)
        self.assertIn('_next_args', keys)

        upper_graph = {u'resource_id': u'upper', u'@id': u'http://semantica.globo.com/upper/', u'title': u'upper'}
        self.assertIn(upper_graph, body['items'])

    def test_200_with_pagination(self):
        # disclaimer: this test assumes there are > 2 non-empty registered graphs in Virtuoso
        response = self.fetch("/?page=1&per_page=2&do_item_count=1", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertIn("items", body.keys())

    @patch("brainiak.utils.cache.retrieve", return_value={"body": {"status": "cached"}, "meta": {"last_modified": "Fri, 11 May 1984 20:00:00 -0300"}})
    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_200_with_cache(self, enable_cache, retrieve):
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body, {'status': "cached"})
        self.assertEqual(response.headers['Last-Modified'], 'Fri, 11 May 1984 20:00:00 -0300')
        self.assertTrue(response.headers['X-Cache'].startswith('HIT from localhost'))

    @patch("brainiak.utils.cache.retrieve", return_value={"cache": False})
    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=False)
    def test_200_without_cache(self, enable_cache, retrieve):
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertIn("items", body.keys())
        self.assertTrue(response.headers.get('Last-Modified'))
        self.assertTrue(response.headers['X-Cache'].startswith('MISS from localhost'))

    @patch("brainiak.utils.cache.retrieve", return_value={"cache": "dismissed"})
    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_200_with_cache_but_with_purge(self, enable_cache, retrieve):
        response = self.fetch("/?purge=1", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertIn("items", body.keys())
        self.assertTrue(response.headers.get('Last-Modified'))
        self.assertTrue(response.headers['X-Cache'].startswith('MISS from localhost'))

    @patch("brainiak.handlers.settings", ENABLE_CACHE=False)
    def test_purge_returns_405_when_cache_is_disabled(self, enable_cache):
        response = self.fetch("/", method='PURGE')
        self.assertEqual(response.code, 405)
        received = json.loads(response.body)
        expected = {u'errors': [u"HTTP error: 405\nCache is disabled (Brainaik's settings.ENABLE_CACHE is set to False)"]}
        self.assertEqual(received, expected)

    @patch("brainiak.utils.cache.delete")
    @patch("brainiak.utils.cache.purge")
    @patch("brainiak.handlers.settings", ENABLE_CACHE=True)
    def test_purge_returns_200_when_cache_is_enabled(self, enable_cache, delete_all, delete):
        response = self.fetch("/", method='PURGE')
        self.assertEqual(response.code, 200)
        delete.assert_called_once_with("/")
        self.assertFalse(response.body)

    @patch("brainiak.utils.cache.delete")
    @patch("brainiak.utils.cache.purge")
    @patch("brainiak.handlers.settings", ENABLE_CACHE=True)
    def test_purge_returns_200_recursive(self, enable_cache, delete_all, delete):
        response = self.fetch("/", method='PURGE', headers={'X-Cache-Recursive': '1'})
        self.assertEqual(response.code, 200)
        self.assertFalse(response.body)
        delete_all.assert_called_once_with("/")


class QueryTestCase(QueryTestCase):
    allow_triplestore_connection = True
    graph_uri = "http://whatever.com"
    fixtures = ["tests/sample/instances.n3"]

    def test_query_pre_defined_graphs(self):
        query = QUERY_LIST_CONTEXT
        response = self.query(query)
        registered_graphs = sparql.filter_values(response, "graph")
        self.assertIn('http://semantica.globo.com/upper/', registered_graphs)

    def test_query_new_graph(self):
        query = QUERY_LIST_CONTEXT
        response = self.query(query)
        registered_graphs = sparql.filter_values(response, "graph")
        self.assertIn('http://whatever.com', registered_graphs)
