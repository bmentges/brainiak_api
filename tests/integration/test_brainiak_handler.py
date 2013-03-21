import json
from mock import patch as patch_mock

from tornado.web import Application, HTTPError

from brainiak.handlers import BrainiakRequestHandler
from tests import TornadoAsyncHTTPTestCase


class TestBrainiakRequestHandler(TornadoAsyncHTTPTestCase):

    class Handler(BrainiakRequestHandler):

        def get(self):
            self.finish("TEST")
            expected_summary = "GET localhost:10007 (127.0.0.1)"
            assert self._request_summary() == expected_summary

        def post(self):
            if self.request.body == "500":
                raise NotImplementedError("exception message")
            elif self.request.body == "400":
                raise HTTPError(400, log_message="testing")

    def get_app(self):
        return Application([('/', self.Handler)],
                           log_function=lambda x: None)

    @patch_mock("brainiak.handlers.log")  # log is None and breaks test otherwise
    def test_request_summary(self, log):
        response = self.fetch('/', method='GET')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body, "TEST")

    @patch_mock("brainiak.handlers.log")  # log is None and breaks test otherwise
    def test_400_error(self, log):
        response = self.fetch('/', method='POST', body="400")
        expected_error_json = {"error": "HTTP error: 400\ntesting"}
        self.assertEqual(response.code, 400)
        self.assertEqual(expected_error_json, json.loads(response.body))

    @patch_mock("brainiak.handlers.log")  # log is None and breaks test otherwise
    def test_500_error(self, log):
        response = self.fetch('/', method='POST', body="500")
        expected_error_json = {"error": "HTTP error: 500\nException:\nTraceback"}
        response_error_json = json.loads(response.body)
        self.assertEqual(response.code, 500)
        self.assertIn(expected_error_json["error"], response_error_json["error"])


class TestUnmatchedHandler(TornadoAsyncHTTPTestCase):

    @patch_mock("brainiak.handlers.log")  # log is None and breaks test otherwise
    def test_get(self, log):
        response = self.fetch('/a/b/c/d/e', method='GET')
        self.assertEqual(response.code, 404)

    @patch_mock("brainiak.handlers.log")  # log is None and breaks test otherwise
    def test_get(self, log):
        response = self.fetch('/a/b/c/d/e', method='PUT')
        self.assertEqual(response.code, 404)

    @patch_mock("brainiak.handlers.log")  # log is None and breaks test otherwise
    def test_get(self, log):
        response = self.fetch('/a/b/c/d/e', method='POST')
        self.assertEqual(response.code, 404)

    @patch_mock("brainiak.handlers.log")  # log is None and breaks test otherwise
    def test_get(self, log):
        response = self.fetch('/a/b/c/d/e', method='DELETE')
        self.assertEqual(response.code, 404)
