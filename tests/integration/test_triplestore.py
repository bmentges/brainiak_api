import unittest

from mock import patch
from tornado.httpclient import HTTPError

from brainiak import triplestore
from brainiak import greenlet_tornado
from tests.tornado_cases import TornadoAsyncTestCase
from tests.mocks import triplestore_config
from tests.sparql import QueryTestCase


SIMPLE_QUERY = "ASK {<SomeInstance> a <SomeClass>}" 


class TriplestoreTestCase(TornadoAsyncTestCase, QueryTestCase):

    fixtures = ["tests/sample/dummy.ttl"]

    @greenlet_tornado.greenlet_test
    def test_query_ok(self):
        response = triplestore.run_query(SIMPLE_QUERY, triplestore_config)
        self.assertEqual(response.code, 200)

    @greenlet_tornado.greenlet_test
    def test_malformed_query(self):
        MALFORMED_QUERY = "SELECT A MALFORMED QUERY {?s ?p ?o}"
        self.assertRaises(HTTPError, triplestore.run_query, MALFORMED_QUERY, triplestore_config)

    @greenlet_tornado.greenlet_test
    def test_not_authenticated_access_to_authenticated_endpoint(self):
        modified_dict = triplestore_config.copy()
        modified_dict["auth_username"] = 'inexistent'
        self.assertRaises(HTTPError, triplestore.run_query, SIMPLE_QUERY, modified_dict)

    @patch("brainiak.triplestore.greenlet_fetch", return_value=None)
    @patch("brainiak.triplestore.log.logger.info")
    @patch("brainiak.triplestore.time.time", return_value=0)
    def test_authenticated_access_to_not_authenticated_endpoint(self, time, info, greenlet_fetch):
        response = triplestore.run_query(SIMPLE_QUERY, triplestore_config)
        self.assertEqual(response, None)
        self.assertEqual(info.call_count, 1)
        log_msg = "POST - http://localhost:8890/sparql-auth - None - dba [tempo: 0] - QUERY - SELECT COUNT(*) WHERE {?s a owl:Class}"
        self.assertTrue(info.call_args, log_msg)


class RunQueryTestCase(QueryTestCase):

    fixtures = ["tests/sample/dummy.ttl"]

    def test_sync_query_not_authenticated_works(self):
        endpoint = "http://localhost:8890/sparql"
        response = triplestore.sync_query(endpoint, SIMPLE_QUERY)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['boolean'])

    def test_sync_query_authenticated_works(self):
        endpoint = "http://localhost:8890/sparql-auth"
        auth = ("dba", "dba")
        response = triplestore.sync_query(endpoint, SIMPLE_QUERY, auth=auth)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['boolean'])

    def test_sync_query_authenticated_fails(self):
        endpoint = "http://localhost:8890/sparql-auth"
        response = triplestore.sync_query(endpoint, SIMPLE_QUERY)
        self.assertEqual(response.status_code, 401)
