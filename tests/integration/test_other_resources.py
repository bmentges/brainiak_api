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


class OptionsTestCase(TornadoAsyncHTTPTestCase):

    def test_collection_has_options(self):
        response = self.fetch('/person/Gender/', method='OPTIONS')
        self.assertEqual(response.code, 204)
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], 'GET, POST, OPTIONS')
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], 'Content-Type')


class TestVirtuosoStatusResource(TornadoAsyncHTTPTestCase):

    # def setUp(self):
    #     self.original_settings_env = settings.ENVIRONMENT
    #     super(TestVirtuosoStatusResource, self).setUp()

    # def tearDown(self):
    #     settings.ENVIRONMENT = self.original_settings_env

    # @patch("brainiak.handlers.log")  # test fails otherwise because log.logger is None
    # def test_virtuoso_status_in_prod(self, log):
    #     settings.ENVIRONMENT = "prod"
    #     response = self.fetch('/status/virtuoso', method='GET')
    #     self.assertEqual(response.code, 404)

    def test_virtuoso_status_in_non_prod(self):
        settings.ENVIRONMENT = "local"
        response = self.fetch('/status/virtuoso', method='GET')
        self.assertEqual(response.code, 200)


def raise_exception():
    raise NotConnectedException


class ActiveMQTestCase(TornadoAsyncHTTPTestCase):

    def setUp(self):
        self.original_abort = event_bus.event_bus_connection.abort
        TornadoAsyncHTTPTestCase.setUp(self)

    def tearDown(self):
        event_bus.event_bus_connection.abort = self.original_abort

    def test_activemq_status_on(self):
        event_bus.event_bus_connection.abort = lambda transaction: ""
        response = self.fetch('/status/activemq', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'ActiveMQ connection | SUCCEED | localhost:61613')

    def test_activemq_status_off(self):
        event_bus.event_bus_connection.abort = lambda transaction: raise_exception()
        response = self.fetch('/status/activemq', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, "ActiveMQ connection | FAILED | localhost:61613 | 'stomp.exception.NotConnectedException'")
