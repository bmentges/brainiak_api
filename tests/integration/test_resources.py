# coding: utf-8
import json
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncHTTPTestCase

from brainiak import greenlet_tornado
from brainiak import __version__, settings, server
from tests import TornadoAsyncHTTPTestCase


class TestInstanceResource(TornadoAsyncHTTPTestCase):

    def get_app(self):
        return server.Application()

    GENDER_MALE_JSON_INSTANCE = {
        "head": {
            "link": [],
            "vars": [
                "p",
                "o"]
        },
        "results": {
            "distinct": False,
            "ordered": True,
            "bindings": [{
                "p": {
                    "type": "uri",
                    "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
                },
                "o": {
                    "type": "uri",
                    "value": "http://semantica.globo.com/person/Gender"
                }
            }, {
                "p": {
                    "type": "uri",
                    "value": "http://www.w3.org/2000/01/rdf-schema#label"
                },
                "o": {
                    "type": "literal",
                    "xml:lang": "pt",
                    "value": "Masculino"
                }
            }]
        }
    }

    def test_get_instance_with_nonexistent_uri(self):
        response = self.fetch('/person/Gender/Alien')
        self.assertEquals(response.code, 204)

    def test_get_instance(self):
        response = self.fetch('/person/Gender/Male')
        self.assertEquals(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEquals(json_received, self.GENDER_MALE_JSON_INSTANCE)


class TestSchemaResource(TornadoAsyncHTTPTestCase):

    SAMPLE_SCHEMA_JSON = {
        u'schema': {
            u'$schema': u'http://json-schema.org/draft-03/schema#',
            u'@context': {u'@language': u'pt', u'person': u'http://semantica.globo.com/person/'},
            u'@id': u'person:Gender',
            u'links': [],
            u'properties': {},
            u'title': u"Gênero da Pessoa",
            u'comment': u"Gênero de uma pessoa.",
            u'type': u'object'
        }
    }

    maxDiff = None

    def test_schema_handler(self):
        response = self.fetch('/person/Gender/_schema')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received, self.SAMPLE_SCHEMA_JSON)

    def test_schema_handler_class_undefined(self):
        response = self.fetch('/animals/Ornithorhynchus/_schema')
        self.assertEqual(response.code, 204)
        self.assertFalse(response.body)


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


class TestVirtuosoStatusResource(TornadoAsyncHTTPTestCase):

    def setUp(self):
        self.original_settings_env = settings.ENVIRONMENT
        super(TestVirtuosoStatusResource, self).setUp()

    def tearDown(self):
        settings.ENVIRONMENT = self.original_settings_env

    def test_virtuoso_status_in_prod(self):
        settings.ENVIRONMENT = "prod"
        response = self.fetch('/status/virtuoso', method='GET')
        self.assertEqual(response.code, 404)
        self.stop()

    def test_virtuoso_status_in_non_prod(self):
        settings.ENVIRONMENT = "local"
        response = self.fetch('/status/virtuoso', method='GET')
        self.assertEqual(response.code, 200)
