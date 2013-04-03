import json

from tornado.web import HTTPError

from brainiak.domain.get import build_domains, build_json, list_domains
from brainiak.utils import sparql
from tests import TornadoAsyncHTTPTestCase


def raise_exception():
    raise Exception


class ListDomainsTestCase(TornadoAsyncHTTPTestCase):

    def setUp(self):
        self.original_filter_values = sparql.filter_values
        super(ListDomainsTestCase, self).setUp()

    def tearDown(self):
        sparql.filter_values = self.original_filter_values
        super(ListDomainsTestCase, self).tearDown()

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
        response = self.fetch("/", method='GET')
        self.assertEqual(response.code, 200)
