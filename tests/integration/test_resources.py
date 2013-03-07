# coding: utf-8
import json


from brainiak import __version__
from brainiak import settings
from tests import TestHandlerBase


class TestInstanceResource(TestHandlerBase):

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
        self.http_client.fetch(self.get_url('/person/Gender/Alien'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)

    def test_get_instance(self):
        self.http_client.fetch(self.get_url('/person/Gender/Male'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received, self.GENDER_MALE_JSON_INSTANCE)


class TestSchemaResource(TestHandlerBase):

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
        self.http_client.fetch(self.get_url('/person/Gender/_schema'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received, self.SAMPLE_SCHEMA_JSON)

    def test_schema_handler_class_undefined(self):
        self.http_client.fetch(self.get_url('/animals/Ornithorhynchus/_schema'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        self.assertFalse(response.body)


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
        self.assertEqual(response.code, 404)

    def test_virtuoso_status_in_non_prod(self):
        settings.ENVIRONMENT = "local"
        response = self.fetch('/status/virtuoso', method='GET')
        self.assertEqual(response.code, 200)
