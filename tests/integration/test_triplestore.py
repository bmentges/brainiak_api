from mock import patch

from tornado.httpclient import HTTPError

from brainiak import triplestore
from brainiak import greenlet_tornado
from tests.tornado_cases import TornadoAsyncTestCase

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
    @patch("brainiak.triplestore.settings",
        SPARQL_ENDPOINT=EndpointConfig.URL,
        SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.BASIC)
    @greenlet_tornado.greenlet_test
    def test_query_ok_with_get_method(self, settings):
        virtuoso_connection = triplestore.VirtuosoConnection()
        response = virtuoso_connection.query(SIMPLE_COUNT_CLASSES_QUERY, method="GET")
        self.assertEqual(response.code, 200)

    @patch("brainiak.triplestore.settings",
        SPARQL_ENDPOINT=EndpointConfig.URL,
        SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.BASIC)
    @greenlet_tornado.greenlet_test
    def test_query_ok(self, settings):
        virtuoso_connection = triplestore.VirtuosoConnection()
        response = virtuoso_connection.query(SIMPLE_COUNT_CLASSES_QUERY)
        self.assertEqual(response.code, 200)

    @patch("brainiak.triplestore.settings",
        SPARQL_ENDPOINT=EndpointConfig.URL,
        SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.BASIC)
    @greenlet_tornado.greenlet_test
    def test_malformed_query(self, settings):
        MALFORMED_QUERY = "SELECT A MALFORMED QUERY {?s ?p ?o}"
        virtuoso_connection = triplestore.VirtuosoConnection()
        try:
            virtuoso_connection.query(MALFORMED_QUERY)
        except HTTPError as ex:
            self.assertEqual(ex.code, 400)
        else:
            self.fail("HTTPError not raised")

    # Authentication HAPPY paths
    @patch("brainiak.triplestore.settings",
           SPARQL_ENDPOINT=EndpointConfig.AUTHENTICATED_URL,
           SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.DIGEST,
           SPARQL_ENDPOINT_USER=EndpointConfig.USER,
           SPARQL_ENDPOINT_PASSWORD=EndpointConfig.PASSWORD)
    @greenlet_tornado.greenlet_test
    def test_authenticated_access_to_authenticated_endpoint(self, settings):
        virtuoso_connection = triplestore.VirtuosoConnection()
        response = virtuoso_connection.query(SIMPLE_COUNT_CLASSES_QUERY)
        self.assertEqual(response.code, 200)

    # Authentication UNHAPPY paths
    @patch("brainiak.triplestore.settings", SPARQL_ENDPOINT=EndpointConfig.AUTHENTICATED_URL)
    @greenlet_tornado.greenlet_test
    def test_not_authenticated_access_to_authenticated_endpoint(self, settings):
        del settings.SPARQL_ENDPOINT_AUTH_MODE
        del settings.SPARQL_ENDPOINT_USER
        del settings.SPARQL_ENDPOINT_PASSWORD
        virtuoso_connection = triplestore.VirtuosoConnection()
        try:
            virtuoso_connection.query(SIMPLE_COUNT_CLASSES_QUERY)
        except HTTPError as ex:
            self.assertEqual(ex.code, 401)
        else:
            self.fail("HTTPError not raised")

    @patch("brainiak.triplestore.settings",
           SPARQL_ENDPOINT=EndpointConfig.URL,
           SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.DIGEST,
           SPARQL_ENDPOINT_USER=EndpointConfig.USER,
           SPARQL_ENDPOINT_PASSWORD=EndpointConfig.PASSWORD)
    @greenlet_tornado.greenlet_test
    def test_authenticated_access_to_not_authenticated_endpoint(self, settings):
        virtuoso_connection = triplestore.VirtuosoConnection()
        response = virtuoso_connection.query(SIMPLE_COUNT_CLASSES_QUERY)
        self.assertEqual(response.code, 200)
