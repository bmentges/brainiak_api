from tornado.web import HTTPError
from mock import patch

from brainiak.instance.delete_resource import query_delete, query_dependants, \
    delete_instance
from brainiak import triplestore, server

from tests.sparql import QueryTestCase
from tests import TornadoAsyncHTTPTestCase


EXPECTED_DEPENDANTS_JSON = {
    u'head': {u'link': [], u'vars': [u'dependant']},
    u'results': {u'bindings': [
        {u'dependant': {u'type': u'uri', u'value': 'http://tatipedia.org/test/Platypus'}},
        {u'dependant': {u'type': u'uri', u'value': 'http://tatipedia.org/test/Teinolophos'}}],
        u'distinct': False,
        u'ordered': True}
}

EXPECTED_DELETE_JSON = {
    u"head": {u"link": [], u"vars": [u"callret-0"]},
    u"results": {u"distinct": False, "ordered": True, "bindings": [
    {"callret-0": {"type": "literal", "value": "Delete from <http://tatipedia.org/test>, 4 (or less) triples -- done"}}
    ]}}


class DeleteQueriesTestCase(QueryTestCase, TornadoAsyncHTTPTestCase):

    allow_triplestore_connection = True
    graph_uri = "http://tatipedia.org/test"
    fixtures = ["tests/sample/instances.n3"]

    def get_app(self):
        return server.Application()

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        triplestore.query_sparql = lambda query: self.query(query)
        super(DeleteQueriesTestCase, self).setUp()

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    def test_dependants_query(self):
        response_bindings = query_dependants("http://tatipedia.org/test/Place/Australia")
        expected_binding = EXPECTED_DEPENDANTS_JSON

        self.assertEqual(len(response_bindings), len(expected_binding))
        for item in expected_binding:
            self.assertIn(item, response_bindings)

    def test_delete_query(self):
        response = query_delete(self.graph_uri, "http://tatipedia.org/test/Species/Platypus")
        expected = EXPECTED_DELETE_JSON

        self.assertEqual(len(response), len(expected))
        self.assertEqual(response, expected)

    def test_delete_instance_with_dependendants(self):
        query_params = {
            "graph_uri": "http://tatipedia.org/test",
            "instance_uri": "http://tatipedia.org/test/Place/Australia"
        }
        self.assertRaises(HTTPError, delete_instance, query_params)

    def test_delete_instance_successful(self):
        query_params = {
            "graph_uri": "http://tatipedia.org/test",
            "instance_uri": "http://tatipedia.org/test/Species/Platypus"
        }
        self.assertTrue(delete_instance(query_params))

    def test_delete_instance_unsuccessful(self):
        query_params = {
            "graph_uri": "http://tatipedia.org/test",
            "instance_uri": "http://tatipedia.org/test/NonExistentURI"
        }
        self.assertFalse(delete_instance(query_params))

    @patch("brainiak.handlers.log")
    @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    def test_handler_204(self, log, settings):
        response = self.fetch('/test/Species/Platypus', method="DELETE")
        self.assertEqual(response.code, 204)

    @patch("brainiak.handlers.log")
    @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    def test_handler_404(self, log, settings):
        response = self.fetch('/test/Species/NonExistentURI', method="DELETE")
        self.assertEqual(response.code, 404)

    @patch("brainiak.handlers.log")
    @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    def test_handler_409(self, log, settings):
        response = self.fetch('/test/Place/Australia', method="DELETE")
        self.assertEqual(response.code, 409)
