from mock import patch

from tornado.httpclient import HTTPError

from brainiak import triplestore
from brainiak import greenlet_tornado
from tests.tornado_cases import TornadoAsyncTestCase

SIMPLE_COUNT_CLASSES_QUERY = "SELECT COUNT(*) WHERE {?s a owl:Class}"

endpoint_dict = {
    'url': 'http://localhost:8890/sparql-auth',
    'auth_mode': 'digest',
    'auth_username': 'api-semantica',
    'auth_password': 'api-semantica'
}


class TriplestoreTestCase(TornadoAsyncTestCase):

    @greenlet_tornado.greenlet_test
    def test_query_ok(self):
        response = triplestore.run_query(SIMPLE_COUNT_CLASSES_QUERY, endpoint_dict=endpoint_dict)
        self.assertEqual(response.code, 200)

    @greenlet_tornado.greenlet_test
    def test_malformed_query(self):
        MALFORMED_QUERY = "SELECT A MALFORMED QUERY {?s ?p ?o}"
        self.assertRaises(HTTPError, triplestore.run_query, MALFORMED_QUERY, endpoint_dict=endpoint_dict)

    @greenlet_tornado.greenlet_test
    def test_not_authenticated_access_to_authenticated_endpoint(self):
        modified_dict = dict(endpoint_dict.items())
        modified_dict["auth_username"] = 'inexistent'
        self.assertRaises(HTTPError, triplestore.run_query, SIMPLE_COUNT_CLASSES_QUERY, endpoint_dict=modified_dict)

    @patch("brainiak.triplestore.greenlet_fetch", return_value=None)
    @patch("brainiak.triplestore.log.logger.info")
    @patch("brainiak.triplestore.time.time", return_value=0)
    def test_authenticated_access_to_not_authenticated_endpoint(self, time, info, greenlet_fetch):
        response = triplestore.run_query(SIMPLE_COUNT_CLASSES_QUERY, endpoint_dict=endpoint_dict)
        self.assertEqual(response, None)
        self.assertEqual(info.call_count, 1)
        log_msg = "POST - http://localhost:8890/sparql-auth - None - api-semantica [tempo: 0] - QUERY - SELECT COUNT(*) WHERE {?s a owl:Class}"
        self.assertTrue(info.call_args, log_msg)
