# coding: utf-8
from mock import patch
from stomp.exception import NotConnectedException

from brainiak import __version__, event_bus, handlers, settings
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class TestHealthcheckResource(TornadoAsyncHTTPTestCase):

    def test_healthcheck(self):
        response = self.fetch('/healthcheck', method='GET')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body, "WORKING")


class TestVersionResource(TornadoAsyncHTTPTestCase):
    def test_healthcheck(self):
        response = self.fetch('/_version', method='GET')
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
        response = self.fetch('/_status/virtuoso', method='GET')
        self.assertEqual(response.code, 200)


class TestCacheStatusResource(TornadoAsyncHTTPTestCase):

    @patch("brainiak.handlers.cache.keys", return_value=["a key", "another key"])
    def test_cache_status_in_non_prod_with_cache(self, mock_keys):
        response = self.fetch('/_status/cache', method='GET')
        self.assertEqual(response.code, 200)
        expected = 'Redis connection authenticated [:j\xdf\x97\xf8:\xcfdS\xd4\xa6\xa4\xb1\x07\x0f7T] | SUCCEED | localhost:6379'
        self.assertIn(expected, response.body)
        self.assertIn("<br>Cached keys:<br>", response.body)
        self.assertIn("<br>a key<br>another key", response.body)

    @patch("brainiak.handlers.cache.keys", return_value=[])
    def test_cache_status_in_non_prod_without_cache(self, mock_keys):
        response = self.fetch('/_status/cache', method='GET')
        self.assertEqual(response.code, 200)
        expected = 'Redis connection authenticated [:j\xdf\x97\xf8:\xcfdS\xd4\xa6\xa4\xb1\x07\x0f7T] | SUCCEED | localhost:6379'
        self.assertIn(expected, response.body)
        self.assertIn("<br>There are no cached keys", response.body)


def raise_exception():
    raise NotConnectedException


class ActiveMQTestCase(TornadoAsyncHTTPTestCase):

    def setUp(self):
        self.original_not_connected = event_bus.middleware.not_connected
        TornadoAsyncHTTPTestCase.setUp(self)
        self.original_notify_bus = settings.NOTIFY_BUS
        settings.NOTIFY_BUS = True
        self.original_connect = event_bus.middleware.connect

    def tearDown(self):
        event_bus.middleware.not_connected = self.original_not_connected
        settings.NOTIFY_BUS = self.original_notify_bus
        event_bus.middleware.connect = self.original_connect

    @patch("brainiak.event_bus.logger")
    def test_activemq_status_on(self, log):
        msg = 'ActiveMQ connection not-authenticated | SUCCEED | localhost:61613'
        event_bus.middleware.not_connected = lambda: ""
        response = self.fetch('/_status/activemq', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, msg)

    @patch("brainiak.event_bus.logger")
    def test_activemq_status_off(self, log):
        msg = "Failed inside middleware"
        body = "ActiveMQ connection not-authenticated | FAILED | localhost:61613 | {0}".format(msg)
        event_bus.middleware.not_connected = lambda: msg
        event_bus.middleware.connect = lambda: raise_exception()
        response = self.fetch('/_status/activemq', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, body)


class LifecheckTestCase(TornadoAsyncHTTPTestCase):

    def setUp(self):
        TornadoAsyncHTTPTestCase.setUp(self)
        self.original_eb_status = handlers.event_bus.status
        self.original_ts_status = handlers.triplestore.status

    def tearDown(self):
        handlers.event_bus.status = self.original_eb_status
        handlers.triplestore.status = self.original_ts_status

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.event_bus.logger")
    def test_lifecheck_working(self, log, mock_lang):
        handlers.triplestore.status = lambda: "Virtuoso SUCCEED"
        handlers.event_bus.status = lambda: "ActiveMQ SUCCEED"
        response = self.fetch('/_status/', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, "WORKING")

    @patch("brainiak.event_bus.logger")
    def test_lifecheck_failed_due_to_virtuoso(self, log):
        handlers.triplestore.status = lambda: "Virtuoso FAILED"
        handlers.event_bus.status = lambda: "ActiveMQ SUCCEED"
        response = self.fetch('/_status/', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, "Virtuoso FAILED")

    @patch("brainiak.event_bus.logger")
    def test_lifecheck_failed_due_to_activemq(self, log):
        handlers.triplestore.status = lambda: "Virtuoso SUCCEED"
        handlers.event_bus.status = lambda: "ActiveMQ FAILED"
        response = self.fetch('/_status/', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, "ActiveMQ FAILED")

    @patch("brainiak.event_bus.logger")
    def test_lifecheck_failed_due_to_activemq(self, log):
        handlers.triplestore.status = lambda: "Virtuoso FAILED"
        handlers.event_bus.status = lambda: "ActiveMQ FAILED"
        response = self.fetch('/_status/', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, "Virtuoso FAILED\nActiveMQ FAILED")
