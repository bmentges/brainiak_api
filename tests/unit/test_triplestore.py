# coding: utf-8
import json
import unittest

from mock import patch
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


class TriplestoreTestCase(unittest.TestCase):\

    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch("brainiak.triplestore.requests.request", return_value=MockResponse())
    def test_both_without_auth_and_with_auth_work(self, mock_request, mock_parse_section):
        received_msg = triplestore.status()
        msg1 = 'Virtuoso connection authenticated [USER:PASSWORD] | SUCCEED | url'
        msg2 = 'Virtuoso connection not-authenticated | SUCCEED | url'
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)

    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch("brainiak.triplestore.requests.request", side_effect=[MockResponse(401), MockResponse()])
    def test_without_auth_works_but_with_auth_doesnt(self, mock_parse_section, mock_request):
        received_msg = triplestore.status()
        msg1 = "Virtuoso connection authenticated [USER:PASSWORD] | FAILED | url | Status code: 401. Message: "
        msg2 = "Virtuoso connection not-authenticated | SUCCEED | url"
        expected_msg = "<br>".join([msg1, msg2])
        self.assertEqual(received_msg, expected_msg)

    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch("brainiak.triplestore.requests.request", side_effect=[MockResponse(), MockResponse(401)])
    def test_without_auth_doesnt_work_but_with_auth_works(self, mock_request, mock_parse_section):
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

    @patch("brainiak.triplestore.parse_section", return_value={"auth_username": "USER",
                                                               "auth_password": "PASSWORD",
                                                               "url": "url"})
    @patch('brainiak.triplestore.do_run_query', side_effect=HTTPError(401))
    def test_query_sparql_with_http_error_401(self, run_query, mock_parse_section):
        self.assertRaises(HTTPError, triplestore.query_sparql, "", {})

    @patch('brainiak.triplestore.do_run_query', side_effect=HTTPError(500))
    def test_query_sparql_with_http_error_500(self, run_query):
        self.assertRaises(HTTPError, triplestore.query_sparql, "", {})

    @patch('brainiak.triplestore.do_run_query', return_value=(MockResponse(), 0))
    def test_query_sparql_withouterror(self, run_query):
        config = {
            "app_name": "Brainiak",
            "url": "url",
            "auth_mode": "digest",
            "auth_username": "api-semantica",
            "auth_password": "api-semantica"
        }

        response = triplestore.query_sparql("", config)
        self.assertEqual(response, {})

    @patch('brainiak.triplestore.greenlet_fetch', return_value=MockResponse())
    @patch('brainiak.triplestore.log')
    def test_query_sparql_with_valid_credential(self, mocked_log, greenlet_fetch):
        response = triplestore.query_sparql("", triplestore_config)
        self.assertEqual(greenlet_fetch.call_count, 1)
        self.assertEqual(response, {})
