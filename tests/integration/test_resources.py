from tornado.testing import AsyncHTTPTestCase

from brainiak import __version__
from brainiak import server, settings
from tests import TestHandlerBase


class TestHealthcheckResource(TestHandlerBase):

    def test_healthcheck(self):
        response = self.fetch('/healthcheck', method='GET')
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body, "WORKING")


class TestVersionResource(TestHandlerBase):

    def test_healthcheck(self):
        response = self.fetch('/version', method='GET')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, __version__)


class TestVirtuosoStatusResource(TestHandlerBase):

    def setUp(self):
        self.original_settings_env = settings.ENVIRONMENT
        super(TestVirtuosoStatusResource, self).setUp()

    def tearDown(self):
        settings.ENVIRONMENT = self.original_settings_env

    def test_virtuoso_status_in_prod(self):
        settings.ENVIRONMENT = "prod"
        response = self.fetch('/status/virtuoso', method='GET')
        self.assertEqual(response.code, 410)

    def test_virtuoso_status_in_non_prod(self):
        settings.ENVIRONMENT = "local"
        response = self.fetch('/status/virtuoso', method='GET')
        self.assertEqual(response.code, 200)
