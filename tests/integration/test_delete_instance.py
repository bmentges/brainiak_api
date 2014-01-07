from tornado.web import HTTPError
from mock import patch

from brainiak.instance.delete_instance import query_delete, query_dependants, \
    delete_instance
from brainiak import triplestore, server

from tests.mocks import Params
from tests.sparql import QueryTestCase
from tests.tornado_cases import TornadoAsyncHTTPTestCase


EXPECTED_DEPENDANTS_JSON = {
    u'head': {u'link': [], u'vars': [u'dependant']},
    u'results': {u'bindings': [
        {u'dependant': {u'type': u'uri', u'value': 'http://tatipedia.org/Platypus'}},
        {u'dependant': {u'type': u'uri', u'value': 'http://tatipedia.org/Teinolophos'}}],
        u'distinct': False,
        u'ordered': True}
}

EXPECTED_DELETE_JSON = {
    u"head": {u"link": [], u"vars": [u"callret-0"]},
    u"results": {u"distinct": False, "ordered": True, "bindings": [
    {"callret-0": {"type": "literal", "value": "Delete from <http://somegraph.org/>, 4 (or less) triples -- done"}}
    ]}}


class DeleteNonExistentTestCase(TornadoAsyncHTTPTestCase):

    @patch("brainiak.handlers.logger")
    def test_handler_404(self, log):
        response = self.fetch('/person/Person/NonExistentURI', method="DELETE")
        self.assertEqual(response.code, 404)


class DeleteQueriesTestCase(QueryTestCase, TornadoAsyncHTTPTestCase):

    allow_triplestore_connection = True
    graph_uri = "http://somegraph.org/"
    fixtures = ["tests/sample/instances.n3"]

    def get_app(self):
        return server.Application()

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        triplestore.query_sparql = lambda query, params: self.query(query)
        super(DeleteQueriesTestCase, self).setUp()

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    def test_dependants_query(self):
        params = Params({
            "graph_uri": self.graph_uri,
            "instance_uri": "http://tatipedia.org/Australia"
        })

        response_bindings = query_dependants(params)
        expected_binding = EXPECTED_DEPENDANTS_JSON

        self.assertEqual(len(response_bindings), len(expected_binding))
        for item in expected_binding:
            self.assertIn(item, response_bindings)

    def test_delete_query(self):
        params = Params({
            "graph_uri": self.graph_uri,
            "instance_uri": "http://tatipedia.org/Platypus"
        })
        response = query_delete(params)

        expected = EXPECTED_DELETE_JSON

        self.assertEqual(len(response), len(expected))
        self.assertEqual(response, expected)

    def test_delete_instance_with_dependendants(self):
        params = Params({
            "graph_uri": self.graph_uri,
            "instance_uri": "http://tatipedia.org/Australia"
        })
        self.assertRaises(HTTPError, delete_instance, params)

    def test_delete_instance_successful(self):
        params = Params({
            "graph_uri": self.graph_uri,
            "instance_uri": "http://tatipedia.org/Platypus"
        })
        self.assertTrue(delete_instance(params))

    def test_delete_instance_unsuccessful(self):
        params = Params({
            "graph_uri": self.graph_uri,
            "instance_uri": "http://tatipedia.org/NonExistentURI"
        })
        self.assertFalse(delete_instance(params))

    @patch("brainiak.handlers.cache.delete")
    @patch("brainiak.handlers.logger")
    @patch("brainiak.handlers.notify_bus")
    def test_handler_204(self, logger, mocked_notify_bus, mock_delete):
        response = self.fetch(
                    '/anygraph/Species/Platypus?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
                    method="DELETE")
        mock_delete.assert_called_with(u"_@@_@@http://tatipedia.org/Platypus##instance")
        self.assertEqual(response.code, 204)

    @patch("brainiak.handlers.logger")
    def test_handler_409(self, log):
        response = self.fetch('/anygraph/Place/Australia?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/', method="DELETE")
        self.assertEqual(response.code, 409)
