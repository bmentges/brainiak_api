# coding: utf-8
from mock import patch
from stomp.exception import NotConnectedException

from brainiak import __version__, event_bus, settings
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class TestHealthcheckResource(TornadoAsyncHTTPTestCase):

    def test_healthcheck(self):
        response = self.fetch('/healthcheck', method='GET')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body, "WORKING")


class TestVersionResource(TornadoAsyncHTTPTestCase):
    def test_healthcheck(self):
        response = self.fetch('/version', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, __version__)
        version_pieces = __version__.split("|")
        self.assertEqual(len(version_pieces), 2)


class OptionsTestCase(TornadoAsyncHTTPTestCase):

    def test_collection_has_options(self):
        response = self.fetch('/person/Gender/', method='OPTIONS')
        self.assertEqual(response.code, 204)
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], 'GET, POST, OPTIONS')
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], settings.CORS_HEADERS)


class TestVirtuosoStatusResource(TornadoAsyncHTTPTestCase):

    def test_virtuoso_status_in_non_prod(self):
        settings.ENVIRONMENT = "local"
        response = self.fetch('/status/virtuoso', method='GET')
        self.assertEqual(response.code, 200)


def raise_exception():
    raise NotConnectedException


class ActiveMQTestCase(TornadoAsyncHTTPTestCase):

    def setUp(self):
        self.original_not_connected = event_bus.middleware.not_connected
        TornadoAsyncHTTPTestCase.setUp(self)
        self.original_notify_bus = settings.NOTIFY_BUS
        settings.NOTIFY_BUS = True

    def tearDown(self):
        event_bus.middleware.not_connected = self.original_not_connected
        settings.NOTIFY_BUS = self.original_notify_bus

    @patch("brainiak.event_bus.logger")
    def test_activemq_status_on(self, log):
        msg = 'ActiveMQ connection not-authenticated | SUCCEED | localhost:61613'
        event_bus.middleware.not_connected = lambda: ""
        response = self.fetch('/status/activemq', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, msg)

    @patch("brainiak.event_bus.logger")
    def test_activemq_status_off(self, log):
        msg = "Failed inside middleware"
        body = "ActiveMQ connection not-authenticated | FAILED | localhost:61613 | {0}".format(msg)
        event_bus.middleware.not_connected = lambda: msg
        response = self.fetch('/status/activemq', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, body)
