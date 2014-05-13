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


from brainiak.utils import config_parser

class RunQueryTestCase(unittest.TestCase):

    def test_sync_query_not_authenticated_works(self):
        query = "ASK {?s a ?o}"
        triplestore_config = config_parser.parse_section()
        triplestore_config["url"] = "http://localhost:8890/sparql"
        response = triplestore.query_sparql(query, triplestore_config, async=False)
        self.assertEqual(response["boolean"], True)

    def test_sync_query_authenticated_works(self):
        query = "ASK {?s a ?o}"
        triplestore_config = config_parser.parse_section()
        response = triplestore.query_sparql(query, triplestore_config, async=False)
        self.assertEqual(response["boolean"], True)

    def test_sync_query_authenticated_fails(self):
        query = "ASK {?s a ?o}"
        triplestore_config = config_parser.parse_section()
        triplestore_config["auth_password"] = "wrong_password"
        self.assertRaises(HTTPError, triplestore.query_sparql, query, triplestore_config, async=False)
