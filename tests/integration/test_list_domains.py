import json

from tornado.web import HTTPError

from brainiak.domain.get import build_json, list_domains, QUERY_LIST_DOMAIN
from brainiak.utils import sparql
from tests import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


def raise_exception():
    raise Exception


class ListDomainsTestCase(TornadoAsyncHTTPTestCase):

    def setUp(self):
        self.original_filter_values = sparql.filter_values
        super(ListDomainsTestCase, self).setUp()

    def tearDown(self):
        sparql.filter_values = self.original_filter_values
        super(ListDomainsTestCase, self).tearDown()

    def test_400(self):
        sparql.filter_values = lambda a, b: []
        response = self.fetch("/?best_martial_arts=aikido", method='GET')
        self.assertEqual(response.code, 400)
        body = json.loads(response.body)
        self.assertEquals(body["error"], u'HTTP error: 400\nArgument best_martial_arts is not supported')

    def test_404(self):
        sparql.filter_values = lambda a, b: []
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 404)
        body = json.loads(response.body)
        self.assertEquals(body["error"], u'HTTP error: 404\nNo domains were found.')

    def test_500(self):
        sparql.filter_values = lambda a, b: raise_exception()
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 500)
        body = json.loads(response.body)
        self.assertIn("raise Exception\n\nException\n", body["error"])

    def test_200(self):
        # disclaimer: this test assumes OWL graph exists in Virtuoso and contains triples
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        owl = {u'resource_id': u'owl', u'@id': u'http://www.w3.org/2002/07/owl#', u'title': u'owl'}

        self.assertIn("links", body.keys())

        self.assertIn("items", body.keys())
        self.assertIn(owl, body['items'])

        self.assertIn("item_count", body.keys())
        self.assertTrue(isinstance(body['item_count'], int))

    def test_200_with_pagination(self):
        # disclaimer: this test assumes there are 2 or more non-empty registered graphs in Virtuoso
        response = self.fetch("/?page=1&per_page=2", method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertIn("links", body.keys())
        self.assertIn("items", body.keys())
        self.assertIn("item_count", body.keys())
        self.assertEqual(body['item_count'], 2)


class QueryTestCase(QueryTestCase):
    allow_triplestore_connection = True
    graph_uri = "http://whatever.com"
    fixtures = ["tests/sample/demo.n3"]

    def test_query_pre_defined_graphs(self):
        query = QUERY_LIST_DOMAIN
        response = self.query(query)
        registered_graphs = sparql.filter_values(response, "graph")
        self.assertIn('http://www.w3.org/2002/07/owl#', registered_graphs)

    def test_query_new_graph(self):
        query = QUERY_LIST_DOMAIN
        response = self.query(query)
        registered_graphs = sparql.filter_values(response, "graph")
        self.assertIn('http://whatever.com', registered_graphs)
