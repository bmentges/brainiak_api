from tests import TornadoAsyncTestCase
from brainiak import triplestore
from mock import patch


SIMPLE_COUNT_CLASSES_QUERY = "SELECT COUNT(*) WHERE {?s a owl:Class}"


class TriplestoreTestCase(TornadoAsyncTestCase):

    def is_response_ok(self, response, *args, **kw):
        self.assertEquals(response.code, 200)
        self.stop()
#
#    def is_malformed_query(self, response, *args, **kw):
#        self.assertEquals(response.code, 400)
#        self.stop()
#
#    def is_unauthorized(self, response, *args, **kw):
#        self.assertEquals(response.code, 401)
#        self.stop()
#
#    def test_query_ok(self):
#        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
#        virtuoso_connection.query(self.is_response_ok, SIMPLE_COUNT_CLASSES_QUERY)
#        self.wait()
#
#    def test_query_ok_with_get_method(self):
#        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
#        virtuoso_connection.query(self.is_response_ok, SIMPLE_COUNT_CLASSES_QUERY, method="GET")
#        self.wait()
#
#    def test_malformed_query(self):
#        MALFORMED_QUERY = "SELECT A MALFORMED QUERY {?s ?p ?o}"
#        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
#        virtuoso_connection.query(self.is_malformed_query, MALFORMED_QUERY)
#        self.wait()

    # HAPPY paths
    @patch("brainiak.triplestore.settings",
           SPARQL_ENDPOINT_FULL_URL="http://localhost:8890/sparql-auth",
           SPARQL_ENDPOINT_AUTH_MODE="digest",
           SPARQL_ENDPOINT_USER="api-semantica",
           SPARQL_ENDPOINT_PASSWORD="api-semantica")
    def test_authenticated_access_to_authenticated_endpoint(self, settings):
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.is_response_ok, SIMPLE_COUNT_CLASSES_QUERY)
        self.wait()

    def test_not_authenticated_acess_to_not_authenticated_endpoint(self):
        pass  # test_query_ok (above)

#    # UNHAPPY paths
#    @patch("brainiak.triplestore.settings", SPARQL_ENDPOINT_FULL_URL="http://localhost:8890/sparql-auth")
#    def test_not_authenticated_access_to_authenticated_endpoint(self, settings):
#        del settings.SPARQL_ENDPOINT_AUTH_MODE
#        del settings.SPARQL_ENDPOINT_USER
#        del settings.SPARQL_ENDPOINT_PASSWORD
#        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
#        virtuoso_connection.query(self.is_unauthorized, SIMPLE_COUNT_CLASSES_QUERY)
#        self.wait()
#
#    def test_authenticated_access_to_not_authenticated_endpoint(self):
#        self.fail("not implemented")
