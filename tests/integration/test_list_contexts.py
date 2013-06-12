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
        response = self.fetch("/?best_martial_arts=aikido", method='GET')
        self.assertEqual(response.code, 400)
        body = json.loads(response.body)
        self.assertEquals(body["error"], u'HTTP error: 400\nArgument best_martial_arts is not supported. The supported arguments are: per_page, sort_order, sort_by, sort_include_empty, page.')

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

        self.assertIn("item_count", body.keys())
        self.assertTrue(isinstance(body['item_count'], int))

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
        self.assertIn("item_count", body.keys())
        self.assertTrue(body['item_count'] > 2)


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
