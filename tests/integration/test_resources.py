# coding: utf-8
import json

from brainiak import __version__, settings, server
from tests import TornadoAsyncHTTPTestCase


class TestInstanceResource(TornadoAsyncHTTPTestCase):

    def get_app(self):
        return server.Application()

    def test_get_instance_with_nonexistent_uri(self):
        response = self.fetch('/person/Gender/Alien')
        self.assertEqual(response.code, 404)

    def test_get_instance(self):
        response = self.fetch('/person/Gender/Male')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertTrue(json_received['$schema'].endswith('_schema'))


class TestSchemaResource(TornadoAsyncHTTPTestCase):

    SAMPLE_SCHEMA_JSON = {
            u'$schema': u'http://json-schema.org/draft-03/schema#',
            u'@context': {u'@language': u'pt', u'person': u'http://semantica.globo.com/person/'},
            u'@id': u'person:Gender',
            u'links': [],
            u'properties': {},
            u'title': u"Gênero da Pessoa",
            u'comment': u"Gênero de uma pessoa.",
            u'type': u'object'
    }

    OLD_SCHEMA_JSON = {
        u'$schema': u'http://json-schema.org/draft-03/schema#',
        u'@context': {u'@language': u'pt',
                   u'rdf': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                   u'rdfs': u'http://www.w3.org/2000/01/rdf-schema#'},
        u'@id': u'http://semantica.globo.com/base/Acordo',
        u'links': [],
        u'properties': {u'http://teste.com/thumbnail': {u'graph': u'http://teste.com/',
                                                     u'title': u'Icone',
                                                     u'type': u'any'},
                     u'rdfs:label': {u'graph': u'http://teste.com/',
                                     u'title': u'Nome Popular',
                                     u'type': u'any'}},
        u'title': u'Acordo',
        u'type': u'object'}

    maxDiff = None

    def test_schema_handler_with_lang(self):
        response = self.fetch('/person/Gender/_schema?lang=pt')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received, self.SAMPLE_SCHEMA_JSON)

    def test_schema_handler_with_invalid_params(self):
        response = self.fetch('/person/Gender/_schema?hello=world')
        self.assertEqual(response.code, 400)
        self.assertFalse(response.body)

    def test_schema_handler_without_lang(self):
        response = self.fetch('/base/Acordo/_schema?graph_uri=http%3A//semantica.globo.com/')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received, self.OLD_SCHEMA_JSON)

    def test_schema_handler_class_undefined(self):
        response = self.fetch('/animals/Ornithorhynchus/_schema')
        self.assertEqual(response.code, 404)
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
