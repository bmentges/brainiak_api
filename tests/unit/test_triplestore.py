# coding: utf-8
import unittest
from mock import patch

from tornado.httpclient import HTTPError, HTTPResponse

from brainiak import triplestore
import SPARQLWrapper


class MockException(Exception):
    def __str__(self):
        return "Mocked exception"


class MockResponse(object):
    body = "{}"


class MockSPARQLWrapper():

    iteration = 0
    exception_iterations = []

    def __init__(self, *args, **kw):
        pass

    def query(self):
        self.iteration += 1
        if (self.iteration - 1) in self.exception_iterations:
            # note that msg is used due to SPARQLWrapper.SPARQLExceptions.py
            # implementation of error messages
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

    @patch('brainiak.triplestore.SPARQLWrapper.SPARQLWrapper.query', side_effect=MockException())
    def test_status_default_exception_msg(self, mock_query):
        received_msg = triplestore.status("USER", "PASSWORD")
        self.assertTrue(received_msg.endswith("Mocked exception"))

    @patch('brainiak.triplestore.settings', SPARQL_ENDPOINT=None, SPARQL_ENDPOINT_HOST='HOST', SPARQL_ENDPOINT_PORT='PORT')
    def test_endpoint_url_without_endpoint(self, settings):
        response = triplestore.endpoint_url()
        self.assertEqual(response, "HOST:PORT")

    @patch('brainiak.triplestore.settings', SPARQL_ENDPOINT='ENDPOINT', SPARQL_ENDPOINT_HOST='HOST', SPARQL_ENDPOINT_PORT='PORT')
    def test_endpoint_url_with_endpoint(self, settings):
        response = triplestore.endpoint_url()
        self.assertEqual(response, "ENDPOINT")

    @patch('brainiak.triplestore.run_query', side_effect=HTTPError(code=401))
    def test_query_sparql_with_http_error_401(self, run_query):
        self.assertRaises(HTTPError, triplestore.query_sparql, "")

    @patch('brainiak.triplestore.run_query', side_effect=HTTPError(code=500))
    def test_query_sparql_with_http_error_500(self, run_query):
        self.assertRaises(HTTPError, triplestore.query_sparql, "")

    @patch('brainiak.triplestore.run_query', side_effect=HTTPError(code=500))
    def test_query_sparql_with_http_error_500(self, run_query):
        self.assertRaises(HTTPError, triplestore.query_sparql, "")

    @patch('brainiak.triplestore.run_query', return_value=MockResponse())
    def test_query_sparql_withouterror(self, run_query):
        response = triplestore.query_sparql("")
        self.assertEqual(response, {})
