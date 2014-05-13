# coding: utf-8
import json
import unittest

from mock import patch
import simplejson
from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.web import HTTPError

from brainiak import triplestore
from tests.mocks import triplestore_config


class MockResponse(object):

    def __init__(self, status_code=200, body="{}"):
        self.status_code = status_code
        self.body = body
        self.text = body

    def json(self):
        return json.loads(self.body)


class TriplestoreTestCase(unittest.TestCase):

    TRIPLESTORE_CONFIG = {
        "app_name": "Brainiak",
        "url": "url",
        "auth_mode": "digest",
        "auth_username": "api-semantica",
        "auth_password": "api-semantica"
    }

    EXAMPLE_QUERY = u"SELECT * {?s a ?o}"
    EXAMPLE_QUERY_URL_ENCODED = "query=SELECT+%2A+%7B%3Fs+a+%3Fo%7D&format=application%2Fsparql-results%2Bjson"

    @patch("brainiak.triplestore.log.logger")
    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch("brainiak.triplestore.requests.request", return_value=MockResponse())
    def test_both_without_auth_and_with_auth_work(self, mock_request, mock_parse_section, log):
        received_msg = triplestore.status()
        msg1 = 'Virtuoso connection authenticated [USER:PASSWORD] | SUCCEED | url'
        msg2 = 'Virtuoso connection not-authenticated | SUCCEED | url'
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)

    @patch("brainiak.triplestore.log.logger")
    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch("brainiak.triplestore.requests.request", side_effect=[MockResponse(401), MockResponse()])
    def test_without_auth_works_but_with_auth_doesnt(self, mock_parse_section, mock_request, mock_log):
        received_msg = triplestore.status()
        msg1 = "Virtuoso connection authenticated [USER:PASSWORD] | FAILED | url | Status code: 401. Message: "
        msg2 = "Virtuoso connection not-authenticated | SUCCEED | url"
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)

    @patch("brainiak.triplestore.log.logger")
    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch("brainiak.triplestore.requests.request", side_effect=[MockResponse(), MockResponse(401)])
    def test_without_auth_doesnt_work_but_with_auth_works(self, mock_request, mock_parse_section, mock_log):
        received_msg = triplestore.status()
        msg1 = "Virtuoso connection authenticated [USER:PASSWORD] | SUCCEED | url"
        msg2 = "Virtuoso connection not-authenticated | FAILED | url | Status code: 401. Message: "
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)

    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch("brainiak.triplestore.requests.request", return_value=MockResponse(401))
    def test_both_without_auth_and_with_auth_dont_work(self, mock_request, mock_parse_section):
        received_msg = triplestore.status()
        msg1 = "Virtuoso connection authenticated [USER:PASSWORD] | FAILED | url | Status code: 401. Message: "
        msg2 = "Virtuoso connection not-authenticated | FAILED | url | Status code: 401. Message: "
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)

    def test_process_triplestore_response_async_true(self):
        expected = {"a": "json string"}
        class TornadoHTTPResponse:
            body = '{"a": "json string"}'
        tornado_response = TornadoHTTPResponse()
        response = triplestore._process_json_triplestore_response(tornado_response)
        self.assertEqual(expected, response)

    def test_process_triplestore_response_async_false(self):
        expected = {"a": "json string"}
        class RequestsHTTPResponse:
            def json(self):
                return {"a": "json string"}
        tornado_response = RequestsHTTPResponse()
        response = triplestore._process_json_triplestore_response(tornado_response,
                                                                  async=False)
        self.assertEqual(response, expected)

    def test_process_triplestore_response_async_false_invalid_json(self):
        class RequestsHTTPResponse:
            def json(self):
                raise simplejson.JSONDecodeError("", "", 10)
            text = ""
        tornado_response = RequestsHTTPResponse()
        self.assertRaises(ClientHTTPError,
                          triplestore._process_json_triplestore_response,
                          tornado_response,
                          async=False)

    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch('brainiak.triplestore.greenlet_fetch', side_effect=ClientHTTPError(401, message=""))
    def test_query_sparql_with_http_error_401(self, run_query, mock_parse_section):
        request_params = {"url": "http://aa"}
        self.assertRaises(HTTPError, triplestore.do_run_query, request_params, async=True)

    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch('brainiak.triplestore.greenlet_fetch', side_effect=ClientHTTPError(500, message=""))
    def test_query_sparql_with_http_error_500(self, run_query, mock_parse_section):
        request_params = {"url": "http://aa"}
        self.assertRaises(ClientHTTPError, triplestore.do_run_query, request_params, async=True)

    def test_build_request_params_for_async_query(self):
        expected_request_for_tornado = {
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "method": triplestore.DEFAULT_HTTP_METHOD,
            "body": self.EXAMPLE_QUERY_URL_ENCODED
        }
        expected_request_for_tornado.update(self.TRIPLESTORE_CONFIG)

        response = triplestore._build_request_params(self.EXAMPLE_QUERY,
                                                     self.TRIPLESTORE_CONFIG,
                                                     async=True)
        self.assertEqual(response, expected_request_for_tornado)

    @patch('brainiak.triplestore.log.logger')
    @patch('brainiak.triplestore.do_run_query', return_value=(MockResponse(), 0))
    def test_query_sparql_without_error(self, run_query, mock_log):
        response = triplestore.query_sparql("", self.TRIPLESTORE_CONFIG)
        self.assertEqual(response, {})

    @patch('brainiak.triplestore.greenlet_fetch', return_value=MockResponse())
    @patch('brainiak.triplestore.log')
    def test_query_sparql_with_valid_credential(self, mocked_log, greenlet_fetch):
        response = triplestore.query_sparql("", triplestore_config)
        self.assertEqual(greenlet_fetch.call_count, 1)
        self.assertEqual(response, {})
