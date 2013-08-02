import json
from mock import patch as patch_mock

from tornado.web import Application, HTTPError
from tornado.curl_httpclient import CurlError
from tornado.httpclient import HTTPError as ClientHTTPError

from brainiak.handlers import BrainiakRequestHandler

from tests.tornado_cases import TornadoAsyncHTTPTestCase


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

        def put(self, unauthorized=False):
            if self.request.body == "unauthorized":
                raise ClientHTTPError(401, "http error: unauthorized, back off")
            elif self.request.body == "500":
                raise HTTPError(500, "Internal Virtuoso Error")
            else:
                raise CurlError(500, "Virtuoso Down on port 8890")

        def delete(self):
            self.finalize(None)

    def get_app(self):
        return Application([('/', self.Handler)],
                           log_function=lambda x: None)

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_request_summary(self, log):
        response = self.fetch('/', method='GET')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body, "TEST")

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_400_error(self, log):
        response = self.fetch('/', method='POST', body="400")
        expected_error_json = {"error": "HTTP error: 400\ntesting"}
        self.assertEqual(response.code, 400)
        self.assertEqual(expected_error_json, json.loads(response.body))

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_500_error(self, log):
        response = self.fetch('/', method='POST', body="500")
        expected_error_json = {"error": "HTTP error: 500\nException:\nTraceback"}
        response_error_json = json.loads(response.body)
        self.assertEqual(response.code, 500)
        self.assertIn(expected_error_json["error"], response_error_json["error"])

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_500_curl_error(self, log):
        response = self.fetch('/', method='PUT')
        self.assertEqual(response.code, 500)

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_500_client_error(self, log):
        response = self.fetch('/', method='PUT', body="unauthorized")
        self.assertEqual(response.code, 500)

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_500_http_error_500(self, log):
        response = self.fetch('/', method='PUT', body="500")
        self.assertEqual(response.code, 500)

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_delete_finalize_None(self, log):
        response = self.fetch('/', method='DELETE')
        self.assertEqual(response.code, 404)


class TestUnmatchedHandler(TornadoAsyncHTTPTestCase):

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_get(self, log):
        response = self.fetch('/a/b/c/d/e', method='GET')
        self.assertEqual(response.code, 404)

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_put(self, log):
        response = self.fetch('/a/b/c/d/e', method='PUT', body='')
        self.assertEqual(response.code, 404)

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_post(self, log):
        response = self.fetch('/a/b/c/d/e', method='POST', body='')
        self.assertEqual(response.code, 404)

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_patch(self, log):
        response = self.fetch('/a/b/c/d/e', method='PATCH', body='')
        self.assertEqual(response.code, 404)

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_delete(self, log):
        response = self.fetch('/a/b/c/d/e', method='DELETE')
        self.assertEqual(response.code, 404)


class AuthenticatedAccessTestCase(TornadoAsyncHTTPTestCase):

    def test_auth_access_with_invalid_user_returns_404(self):
        response = self.fetch("/", method='GET', headers={'X-Brainiak-Client-Id': '1'})
        self.assertEqual(response.code, 404)
        expected_body = {"error": u"HTTP error: 404\nClient-Id provided at 'X-Brainiak-Client-Id' (1) is not known"}
        computed_body = json.loads(response.body)
        self.assertEqual(computed_body, expected_body)

    def test_valid_client_id_from_eureka_client(self):
        eureka_client_id = 'YXA67LOpsLMnEeKa8nvYJ9aXRQ'
        response = self.fetch("/", method='GET', headers={'X-Brainiak-Client-Id': eureka_client_id})
        self.assertEqual(response.code, 200)
