import unittest

from mock import patch
from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.web import HTTPError

from brainiak import triplestore
from brainiak import greenlet_tornado
from brainiak.utils import config_parser
from brainiak.utils.sparql import compress_keys_and_values
from tests.mocks import triplestore_config
from tests.sparql import QueryTestCase
from tests.tornado_cases import TornadoAsyncTestCase


SIMPLE_QUERY = "ASK {<SomeInstance> a <SomeClass>}"


class TriplestoreTestCase(TornadoAsyncTestCase, QueryTestCase):

    fixtures = ["tests/sample/dummy.ttl"]

    @greenlet_tornado.greenlet_test
    def test_query_ok(self):
        response = triplestore.query_sparql(SIMPLE_QUERY, triplestore_config)
        self.assertTrue(response['boolean'])

    @greenlet_tornado.greenlet_test
    def test_malformed_query(self):
        MALFORMED_QUERY = "SELECT A MALFORMED QUERY {?s ?p ?o}"
        with self.assertRaises(ClientHTTPError) as error:
            triplestore.query_sparql(MALFORMED_QUERY, triplestore_config)
        self.assertEqual(str(error.exception), 'HTTP 400: Bad Request')

    @greenlet_tornado.greenlet_test
    def test_query_to_authenticated_endpoint_inexistent_username(self):
        modified_dict = triplestore_config.copy()
        modified_dict["auth_username"] = 'inexistent'
        self.assertRaises(HTTPError, triplestore.query_sparql, SIMPLE_QUERY, modified_dict)

    @patch("brainiak.triplestore.greenlet_fetch", return_value=None)
    @patch("brainiak.triplestore.log.logger.info")
    @patch("brainiak.triplestore.time.time", return_value=0)
    def test_authenticated_access_to_not_authenticated_endpoint(self, time, info, greenlet_fetch):
        response = triplestore.query_sparql(SIMPLE_QUERY, triplestore_config)
        self.assertEqual(response, None)
        self.assertEqual(info.call_count, 1)
        log_msg = "POST - http://localhost:8890/sparql-auth - None - dba [tempo: 0] - QUERY - SELECT COUNT(*) WHERE {?s a owl:Class}"
        self.assertTrue(info.call_args, log_msg)
        with self.assertRaises(HTTPError) as error:
            triplestore.query_sparql(SIMPLE_QUERY, modified_dict)
        self.assertEqual(error.status_code, 401)

    @greenlet_tornado.greenlet_test
    def test_authenticated_access_to_not_authenticated_endpoint(self):
        response = triplestore.query_sparql(SIMPLE_QUERY, triplestore_config)
        self.assertTrue(response["boolean"])


class RunQueryTestCase(QueryTestCase):

    fixtures = ["tests/sample/dummy.ttl"]

    def test_sync_query_not_authenticated_works(self):
        triplestore_config = config_parser.parse_section()
        triplestore_config["url"] = "http://localhost:8890/sparql"
        response = triplestore.query_sparql(SIMPLE_QUERY, triplestore_config, async=False)
        self.assertTrue(response['boolean'])

    def test_sync_query_authenticated_works(self):
        triplestore_config = config_parser.parse_section()
        response = triplestore.query_sparql(SIMPLE_QUERY, triplestore_config, async=False)
        self.assertTrue(response["boolean"])

    def test_sync_query_authenticated_fails(self):
        triplestore_config = config_parser.parse_section()
        triplestore_config["auth_password"] = "wrong_password"
        self.assertRaises(HTTPError, triplestore.query_sparql, SIMPLE_QUERY, triplestore_config, async=False)
