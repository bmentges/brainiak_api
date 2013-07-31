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
        response = triplestore.run_query(SIMPLE_COUNT_CLASSES_QUERY, method="GET")
        self.assertEqual(response.code, 200)

    @patch("brainiak.triplestore.settings",
        SPARQL_ENDPOINT=EndpointConfig.URL,
        SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.BASIC)
    @greenlet_tornado.greenlet_test
    def test_query_ok(self, settings):
        response = triplestore.run_query(SIMPLE_COUNT_CLASSES_QUERY)
        self.assertEqual(response.code, 200)

    @greenlet_tornado.greenlet_test
    def test_malformed_query(self):
        MALFORMED_QUERY = "SELECT A MALFORMED QUERY {?s ?p ?o}"
        self.assertRaises(HTTPError, triplestore.run_query, MALFORMED_QUERY)

    # Authentication HAPPY paths
    @patch("brainiak.triplestore.settings",
           SPARQL_ENDPOINT=EndpointConfig.AUTHENTICATED_URL,
           SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.DIGEST,
           SPARQL_ENDPOINT_USER=EndpointConfig.USER,
           SPARQL_ENDPOINT_PASSWORD=EndpointConfig.PASSWORD)
    @greenlet_tornado.greenlet_test
    def test_authenticated_access_to_authenticated_endpoint(self, settings):
        response = triplestore.run_query(SIMPLE_COUNT_CLASSES_QUERY)
        self.assertEqual(response.code, 200)

    # Authentication UNHAPPY paths
    @patch("brainiak.triplestore.settings", SPARQL_ENDPOINT=EndpointConfig.AUTHENTICATED_URL)
    @greenlet_tornado.greenlet_test
    def test_not_authenticated_access_to_authenticated_endpoint(self, settings):
        del settings.SPARQL_ENDPOINT_AUTH_MODE
        del settings.SPARQL_ENDPOINT_USER
        del settings.SPARQL_ENDPOINT_PASSWORD
        try:
            triplestore.run_query(SIMPLE_COUNT_CLASSES_QUERY)
        except HTTPError as ex:
            self.assertEqual(ex.code, 401)
        else:
            self.fail("HTTPError not raised")

    @patch("brainiak.triplestore.greenlet_fetch", return_value=None)
    @patch("brainiak.triplestore.log.logger.info")
    @patch("brainiak.triplestore.time.time", return_value=0)
    @patch("brainiak.triplestore.settings",
           SPARQL_ENDPOINT=EndpointConfig.URL,
           SPARQL_ENDPOINT_AUTH_MODE=EndpointConfig.DIGEST,
           SPARQL_ENDPOINT_USER=EndpointConfig.USER,
           SPARQL_ENDPOINT_PASSWORD=EndpointConfig.PASSWORD)
    def test_authenticated_access_to_not_authenticated_endpoint(self, settings, time, info, greenlet_fetch):
        response = triplestore.run_query(SIMPLE_COUNT_CLASSES_QUERY)
        self.assertEqual(response, None)
        self.assertEqual(info.call_count, 1)
        log_msg = "POST - http://localhost:8890/sparql - None - api-semantica [tempo: 0] - QUERY - SELECT COUNT(*) WHERE {?s a owl:Class}"
        self.assertTrue(info.call_args, log_msg)
