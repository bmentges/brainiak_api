import json

from mock import patch
from tornado.web import HTTPError


from brainiak.instance.delete_instance import query_delete, query_dependants, \
    delete_instance, QUERY_DEPENDANTS_TEMPLATE, QUERY_DELETE_INSTANCE
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

    graph_uri = "http://somegraph.org/"
    fixtures = ["tests/sample/instances.n3"]

    def get_app(self):
        return server.Application()

    def test_dependants_query(self):
        params = Params({
            "graph_uri": self.graph_uri,
            "instance_uri": "http://tatipedia.org/Australia"
        })

        query = QUERY_DEPENDANTS_TEMPLATE % params
        response_bindings = self.query(query)
        expected_binding = EXPECTED_DEPENDANTS_JSON

        self.assertEqual(len(response_bindings), len(expected_binding))
        for item in expected_binding:
            self.assertIn(item, response_bindings)

    def test_delete_query(self):
        params = Params({
            "graph_uri": self.graph_uri,
            "instance_uri": "http://tatipedia.org/Platypus"
        })
        query = QUERY_DELETE_INSTANCE % params
        response = self.query(query)

        expected = EXPECTED_DELETE_JSON

        self.assertEqual(len(response), len(expected))
        self.assertEqual(response, expected)

    @patch("brainiak.handlers.cache.purge_an_instance")
    @patch("brainiak.handlers.logger")
    @patch("brainiak.handlers.notify_bus")
    def test_handler_204(self, logger, mocked_notify_bus, mock_purge):
        response = self.fetch(
                    '/anygraph/Species/Platypus?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
                    method="DELETE")
        mock_purge.assert_called_with(u'http://tatipedia.org/Platypus')
        self.assertEqual(response.code, 204)

    @patch("brainiak.handlers.logger")
    def test_handler_409(self, log):
        response = self.fetch('/anygraph/Place/Australia?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/', method="DELETE")
        self.assertEqual(response.code, 409)
        expected_body = {u'errors': [u'HTTP error: 409\nN\xe3o foi poss\xedvel excluir inst\xe2ncias devido \xe0s depend\xeancias: http://tatipedia.org/Platypus, http://tatipedia.org/Teinolophos']}
        computed_body = json.loads(response.body)
        self.assertEqual(computed_body, expected_body)
