import unittest

from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.web import HTTPError


from brainiak import triplestore
from brainiak import greenlet_tornado
from brainiak.utils.sparql import compress_keys_and_values
from tests.mocks import triplestore_config
from tests.tornado_cases import TornadoAsyncTestCase


SIMPLE_COUNT_CLASSES_QUERY = "SELECT COUNT(*) WHERE {?s a owl:Class}"


class TriplestoreTestCase(TornadoAsyncTestCase):

    @greenlet_tornado.greenlet_test
    def test_query_ok(self):
        response = triplestore.query_sparql(SIMPLE_COUNT_CLASSES_QUERY, triplestore_config)
        compress_keys_and_values(response)

    @greenlet_tornado.greenlet_test
    def test_malformed_query(self):
        MALFORMED_QUERY = "SELECT A MALFORMED QUERY {?s ?p ?o}"
        try:
            triplestore.query_sparql(MALFORMED_QUERY, triplestore_config)
        except ClientHTTPError as e:
            self.assertEqual(e.code, 400)
        else:
            self.fail("ClientHTTPError should have been raised")


    @greenlet_tornado.greenlet_test
    def test_query_to_authenticated_endpoint_inexistent_username(self):
        modified_dict = triplestore_config.copy()
        modified_dict["auth_username"] = 'inexistent'
        try:
            triplestore.query_sparql(SIMPLE_COUNT_CLASSES_QUERY, modified_dict)
        except HTTPError as e:
            self.assertEqual(e.status_code, 401)
        else:
            self.fail("ClientHTTPError should have been raised")


    @greenlet_tornado.greenlet_test
    def test_authenticated_access_to_not_authenticated_endpoint(self):
        response = triplestore.query_sparql(SIMPLE_COUNT_CLASSES_QUERY, triplestore_config)
        try:
            int(response["results"]["bindings"][0]["callret-0"]["value"])
        except Exception as e:
            self.fail(u"Exception: {0}".format(e))


class RunQueryTestCase(unittest.TestCase):

    def test_sync_query_not_authenticated_works(self):
        endpoint = "http://localhost:8890/sparql"
        query = "ASK {?s a ?o}"
        response = triplestore.sync_query(endpoint, query)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['boolean'])

    def test_sync_query_authenticated_works(self):
        endpoint = "http://localhost:8890/sparql-auth"
        query = "ASK {?s a ?o}"
        auth = ("api-semantica", "api-semantica")
        response = triplestore.sync_query(endpoint, query, auth=auth)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['boolean'])

    def test_sync_query_authenticated_fails(self):
        endpoint = "http://localhost:8890/sparql-auth"
        query = "ASK {?s a ?o}"
        response = triplestore.sync_query(endpoint, query)
        self.assertEqual(response.status_code, 401)
