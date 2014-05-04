import json
import StringIO
from mock import patch as patch_mock

from tornado import locale
from tornado.web import Application, HTTPError
from tornado.curl_httpclient import CurlError
from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.httpclient import HTTPResponse

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
            elif self.request.body == "400":
                _buffer = StringIO.StringIO()
                _buffer.write("Malformed query")
                response = HTTPResponse(self.request, 400, buffer=_buffer, effective_url="/a")
                raise ClientHTTPError(400, message="Bad request", response=response)
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
        expected_error_json = {"errors": ["HTTP error: 400\ntesting"]}
        self.assertEqual(response.code, 400)
        self.assertEqual(expected_error_json, json.loads(response.body))

    @patch_mock("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_400_client_error(self, log, settings):
        expected_error_message = ["HTTP error: 500\nAccess to backend service failed." +
                                  "  HTTP 400: Bad request.\nResponse:\nMalformed query"]
        response = self.fetch('/', method='PUT', body="400")
        self.assertEqual(response.code, 500)
        self.assertEqual(json.loads(response.body)["errors"], expected_error_message)

    @patch_mock("brainiak.handlers.logger")  # log is None and breaks test otherwise
    def test_500_error(self, log):
        response = self.fetch('/', method='POST', body="500")
        expected_error_json = "HTTP error: 500\nException:\nTraceback"
        response_error_json = json.loads(response.body)
        self.assertEqual(response.code, 500)
        self.assertIn(expected_error_json, response_error_json["errors"][0])

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

    @patch_mock("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_auth_access_with_invalid_user_returns_404(self, settings):
        response = self.fetch("/", method='GET', headers={'X-Brainiak-Client-Id': '1'})
        self.assertEqual(response.code, 404)
        expected_body = {"errors": [u"HTTP error: 404\nClient-Id provided at 'X-Brainiak-Client-Id' (1) is not known"]}
        computed_body = json.loads(response.body)
        self.assertEqual(computed_body, expected_body)

    def test_valid_client_id_from_another_client(self):
        eureka_client_id = 'other'
        response = self.fetch("/", method='GET', headers={'X-Brainiak-Client-Id': eureka_client_id})
        self.assertEqual(response.code, 200)


class TranslateTestCase(TornadoAsyncHTTPTestCase):

    class Handler(BrainiakRequestHandler):

        def get(self):
            locale.load_gettext_translations(directory="locale", domain="brainiak")
            user_locale = self.get_browser_locale()
            _ = user_locale.translate
            self.finalize(_("WORKING"))

    def get_app(self):
        return Application([('/', self.Handler)],
                           log_function=lambda x: None)

    @patch_mock("brainiak.handlers.logger")
    def test_request_portuguese(self, mock_logger):
        headers = {"Accept-Language": "pt_BR;q=0.8,en;q=0.2"}
        response = self.fetch('/', method='GET', headers=headers)
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body, "FUNCIONANDO")

    @patch_mock("brainiak.handlers.logger")
    def test_request_default(self, mock_logger):
        response = self.fetch('/', method='GET')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body, "WORKING")
