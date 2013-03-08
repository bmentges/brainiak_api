from mock import patch

from brainiak import triplestore, server
from brainiak.greenlet_tornado import greenlet_test
from tests import TornadoAsyncTestCase, HTTPError
import greenlet

SIMPLE_COUNT_CLASSES_QUERY = "SELECT COUNT(*) WHERE {?s a owl:Class}"


# TODO Put that in a configs file
class EndpointConfig:

    URL = "http://localhost:8890/sparql"
    AUTHENTICATED_URL = "http://localhost:8890/sparql-auth"
    USER = "api-semantica"
    PASSWORD = "api-semantica"
    DIGEST = "digest"
    BASIC = "basic"


class TriplestoreTestCase(TornadoAsyncTestCase):

    application = lambda: None
    application._wsgi = None

    def is_response_ok(self, response, *args, **kw):
        self.assertEquals(response.code, 200)
        self.stop()

    def is_malformed_query(self, response, *args, **kw):
        self.assertEquals(response.code, 400)
        self.stop()

    def is_unauthorized(self, response, *args, **kw):
        self.assertEquals(response.code, 401)
        self.stop()

    @greenlet_test
    @patch("brainiak.triplestore.settings",
           SPARQL_ENDPOINT=EndpointConfig.URL,
           )
    def test_query_ok_with_get_method(self, settings):
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        response = virtuoso_connection.query(SIMPLE_COUNT_CLASSES_QUERY, method="GET")
        self.assertEquals(response.code, 200)

    @greenlet_test
    @patch("brainiak.triplestore.settings", SPARQL_ENDPOINT=EndpointConfig.URL)
    def test_query_ok(self, settings):
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        response = virtuoso_connection.query(SIMPLE_COUNT_CLASSES_QUERY)
        self.assertEquals(response.code, 200)


    @greenlet_test
    @patch("brainiak.triplestore.settings", SPARQL_ENDPOINT=EndpointConfig.URL)
    def test_malformed_query(self, settings):
        MALFORMED_QUERY = "SELECT A MALFORMED QUERY {?s ?p ?o}"
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        try:
            virtuoso_connection.query(MALFORMED_QUERY)
        except HTTPError as ex:
            self.assertEquals(ex.code, 400)
        else:
            self.fail("HTTPError not raised")

    # Authentication HAPPY paths
    @patch("brainiak.triplestore.settings",
           SPARQL_ENDPOINT=EndpointConfig.AUTHENTICATED_URL,
           SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.DIGEST,
           SPARQL_ENDPOINT_USER=EndpointConfig.USER,
           SPARQL_ENDPOINT_PASSWORD=EndpointConfig.PASSWORD)
    def test_authenticated_access_to_authenticated_endpoint(self, settings):
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.is_response_ok, SIMPLE_COUNT_CLASSES_QUERY)
        self.wait()

    def test_not_authenticated_acess_to_not_authenticated_endpoint(self):
        pass  # test_query_ok (above)

    # Authentication UNHAPPY paths
    @patch("brainiak.triplestore.settings", SPARQL_ENDPOINT=EndpointConfig.AUTHENTICATED_URL)
    def test_not_authenticated_access_to_authenticated_endpoint(self, settings):
        del settings.SPARQL_ENDPOINT_AUTH_MODE
        del settings.SPARQL_ENDPOINT_USER
        del settings.SPARQL_ENDPOINT_PASSWORD
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.is_unauthorized, SIMPLE_COUNT_CLASSES_QUERY)
        self.wait()

    @patch("brainiak.triplestore.settings",
           SPARQL_ENDPOINT=EndpointConfig.URL,
           SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.DIGEST,
           SPARQL_ENDPOINT_USER=EndpointConfig.USER,
           SPARQL_ENDPOINT_PASSWORD=EndpointConfig.PASSWORD)
    def test_authenticated_access_to_not_authenticated_endpoint(self, settings):
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.is_response_ok, SIMPLE_COUNT_CLASSES_QUERY)
        self.wait()
