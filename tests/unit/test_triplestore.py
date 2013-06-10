# coding: utf-8
import unittest
from mock import patch

from tornado.httpclient import HTTPError

from brainiak import triplestore
import SPARQLWrapper


class TriplestoreInitTestCase(unittest.TestCase):

    @patch('brainiak.triplestore.settings', SPARQL_ENDPOINT_HOST="http://myhost", SPARQL_ENDPOINT_PORT=8080)
    def tests_init_connection_endpoint_host_and_port_defined_in_settings(self, settings):
        del settings.SPARQL_ENDPOINT

        expected = "http://myhost:8080/sparql"
        virtuoso_connection = triplestore.VirtuosoConnection()
        result = virtuoso_connection.endpoint_url
        self.assertEqual(expected, result)

    @patch('brainiak.triplestore.settings', SPARQL_ENDPOINT="http://myhost:8080/sparql")
    def test_init_connection_endpoint_full_url_defined_in_settings(self, settings):
        expected = "http://myhost:8080/sparql"
        virtuoso_connection = triplestore.VirtuosoConnection()
        result = virtuoso_connection.endpoint_url
        self.assertEqual(expected, result)


class TriplestoreSetCredentialsTestCase(unittest.TestCase):

    @patch('brainiak.triplestore.settings')
    def test_set_credentials_no_auth_settings_at_all(self, settings):
        del settings.SPARQL_ENDPOINT_USER
        del settings.SPARQL_ENDPOINT_PASSWORD
        del settings.SPARQL_ENDPOINT_AUTH_MODE

        virtuoso_connection = triplestore.VirtuosoConnection()
        credentials = (virtuoso_connection.user, virtuoso_connection.password, virtuoso_connection.auth_mode)
        self.assertTrue(all([x is None for x in credentials]))

    @patch('brainiak.triplestore.settings')
    def test_set_credentials_no_password(self, settings):
        del settings.SPARQL_ENDPOINT_PASSWORD

        virtuoso_connection = triplestore.VirtuosoConnection()
        credentials = (virtuoso_connection.user, virtuoso_connection.password, virtuoso_connection.auth_mode)
        self.assertTrue(all([x is None for x in credentials]))


class MockSPARQLWrapper():

    iteration = 0
    exception_iterations = []

    def __init__(self, *args, **kw):
        pass

    def query(self):
        self.iteration += 1
        if (self.iteration - 1) in self.exception_iterations:
            e = Exception()
            e.msg = "ERROR %d" % (self.iteration - 1)
            raise e

    def addDefaultGraph(self, graph):
        pass

    def setQuery(self, query):
        pass

    def setCredentials(self, username, password, mode=None, realm=None):
        pass


class TestCaseStatus(unittest.TestCase):

    def setUp(self):
        self.original_sparql_wrapper = SPARQLWrapper.SPARQLWrapper
        SPARQLWrapper.SPARQLWrapper = MockSPARQLWrapper

    def tearDown(self):
        SPARQLWrapper.SPARQLWrapper = self.original_sparql_wrapper

    def test_both_without_auth_and_with_auth_work(self):
        SPARQLWrapper.SPARQLWrapper.iteration = 0
        SPARQLWrapper.SPARQLWrapper.exception_iterations = []

        received_msg = triplestore.status("USER", "PASSWORD")
        msg1 = 'Virtuoso connection not-authenticated | SUCCEED | http://localhost:8890/sparql-auth'
        msg2 = 'Virtuoso connection authenticated [USER:1\x9fM&\xe3\xc56\xb5\xdd\x87\x1b\xb2\xc5.1x] | SUCCEED | http://localhost:8890/sparql-auth'
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)

    def test_without_auth_works_but_with_auth_doesnt(self):
        SPARQLWrapper.SPARQLWrapper.iteration = 0
        SPARQLWrapper.SPARQLWrapper.exception_iterations = [1]
        received_msg = triplestore.status("USER", "PASSWORD")
        msg1 = "Virtuoso connection not-authenticated | SUCCEED | http://localhost:8890/sparql-auth"
        msg2 = "Virtuoso connection authenticated [USER:1\x9fM&\xe3\xc56\xb5\xdd\x87\x1b\xb2\xc5.1x] | FAILED | http://localhost:8890/sparql-auth | ERROR 1"
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)

    def test_without_auth_doesnt_work_but_with_auth_works(self):
        SPARQLWrapper.SPARQLWrapper.iteration = 0
        SPARQLWrapper.SPARQLWrapper.exception_iterations = [0]
        received_msg = triplestore.status("USER", "PASSWORD")
        msg1 = "Virtuoso connection not-authenticated | FAILED | http://localhost:8890/sparql-auth | ERROR 0"
        msg2 = "Virtuoso connection authenticated [USER:1\x9fM&\xe3\xc56\xb5\xdd\x87\x1b\xb2\xc5.1x] | SUCCEED | http://localhost:8890/sparql-auth"
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)

    def test_both_without_auth_and_with_auth_dont_work(self):
        SPARQLWrapper.SPARQLWrapper.iteration = 0
        SPARQLWrapper.SPARQLWrapper.exception_iterations = [0, 1]
        received_msg = triplestore.status("USER", "PASSWORD")
        msg1 = "Virtuoso connection not-authenticated | FAILED | http://localhost:8890/sparql-auth | ERROR 0"
        msg2 = "Virtuoso connection authenticated [USER:1\x9fM&\xe3\xc56\xb5\xdd\x87\x1b\xb2\xc5.1x] | FAILED | http://localhost:8890/sparql-auth | ERROR 1"
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)


class TriplestoreExceptionTestCase(unittest.TestCase):

    @patch("brainiak.triplestore.VirtuosoConnection.query", side_effect=HTTPError(401))
    def test_query_returns_401(self, mocked_query):
        try:
            triplestore.query_sparql("aa")
        except HTTPError as e:
            self.assertEquals(e.message, 'HTTP 401: Check triplestore user and password.')
        else:
            self.fail()
