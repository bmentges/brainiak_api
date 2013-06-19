import json
from mock import patch

from brainiak.root.get import QUERY_LIST_CONTEXT
from brainiak.prefixes import ROOT_CONTEXT
from brainiak.utils import sparql
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

    @patch("brainiak.handlers.logger")
    def test_400(self, log):
        sparql.filter_values = lambda a, b: []
        response = self.fetch("/?best_aikido_move=ki_projection", method='GET')
        self.assertEqual(response.code, 400)
        body = json.loads(response.body)
        self.assertEquals(body["error"], u'HTTP error: 400\nArgument best_aikido_move is not supported. The supported arguments are: purge, sort_order, per_page, sort_by, page, do_item_count, sort_include_empty.')

    @patch("brainiak.handlers.logger")
    def test_404(self, log):
        sparql.filter_values = lambda a, b: []
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 404)
        body = json.loads(response.body)
        self.assertEquals(body["error"], u'HTTP error: 404\nNo contexts were found.')

    @patch("brainiak.handlers.logger")
    def test_500(self, log):
        sparql.filter_values = lambda a, b: raise_exception()
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 500)
        body = json.loads(response.body)
        self.assertIn("raise Exception\n\nException\n", body["error"])

    def test_200(self):
        # disclaimer: this test assumes UPPER graph exists in Virtuoso and contains triples
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        default_graph = {u'resource_id': u'upper', u'@id': u'http://semantica.globo.com/upper/', u'title': u'upper'}

        self.assertIn("links", body.keys())

        self.assertIn("items", body.keys())
        self.assertIn(default_graph, body['items'])

    def test_root_context(self):
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        default_graph = {u'resource_id': ROOT_CONTEXT, u'@id': u'http://semantica.globo.com/', u'title': ROOT_CONTEXT}
        self.assertIn("items", body.keys())
        self.assertIn(default_graph, body['items'])

    def test_200_with_pagination(self):
        # disclaimer: this test assumes there are > 2 non-empty registered graphs in Virtuoso
        response = self.fetch("/?page=1&per_page=2", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertIn("links", body.keys())
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
