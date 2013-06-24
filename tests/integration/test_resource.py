# coding: utf-8
import json
from urlparse import urlparse

from mock import patch

from brainiak import __version__, server, settings
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class TestInstanceResource(TornadoAsyncHTTPTestCase):

    def get_app(self):
        return server.Application()

    @patch("brainiak.handlers.logger")
    def test_get_instance_with_nonexistent_uri(self, log):
        response = self.fetch('/person/Gender/Alien')
        self.assertEqual(response.code, 404)
        self.assertEqual(response.body, '{"error": "HTTP error: 404\\nInstance (http://semantica.globo.com/person/Gender/Alien) of class (http://semantica.globo.com/person/Gender) in graph (http://semantica.globo.com/person/) was not found."}')

    def test_get_instance(self):
        response = self.fetch('/person/Gender/Male')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['@type'], 'person:Gender')
        self.assertEqual(json_received['@id'], "http://semantica.globo.com/person/Gender/Male")

    def test_instance_has_options(self):
        response = self.fetch('/person/Gender/Female', method='OPTIONS')
        self.assertEqual(response.code, 204)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], settings.CORS_HEADERS)


class TestSchemaResource(TornadoAsyncHTTPTestCase):

    SAMPLE_SCHEMA_JSON = {
        u'$schema': u'http://json-schema.org/draft-03/schema#',
        u'@context': {u'@language': u'pt', u'person': u'http://semantica.globo.com/person/'},
        u'@id': u'person:Gender',
        u'links': [
            {u'href': u'http://localhost:10023/person/Gender/_class?lang=pt', u'method': u'GET', u'rel': u'self'},
            {u'href': u'http://localhost:10023/person/Gender?class_prefix=http%3A%2F%2Fsemantica.globo.com%2Fperson%2F', u'method': u'GET', u'rel': u'collection'}],
        u'properties': {},
        u'title': u"Gênero da Pessoa",
        u'comment': u"Gênero de uma pessoa.",
        u'type': u'object'
    }

    maxDiff = None

    def test_collection_has_options(self):
        response = self.fetch('/person/Gender/_class', method='OPTIONS')
        self.assertEqual(response.code, 204)
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], 'GET, OPTIONS')
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], settings.CORS_HEADERS)

    def test_schema_has_options(self):
        response = self.fetch('/person/Gender/_class', method='OPTIONS')
        self.assertEqual(response.code, 204)

    def test_schema_has_cors(self):
        response = self.fetch('/person/Gender/_class', method='OPTIONS')
        response.headers['Access-Control-Allow-Methods']

    def test_schema_handler_with_lang(self):
        response = self.fetch('/person/Gender/_class?lang=pt')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        # Adjust dynamic port from real to expected prior to comparison
        effective_port = str(urlparse(json_received[u'links'][0][u'href']).port)
        for entry in self.SAMPLE_SCHEMA_JSON[u'links']:
            entry[u'href'] = entry[u'href'].replace('10023', effective_port)
        #json_received['links'] = sorted(json_received['links'])
        #self.SAMPLE_SCHEMA_JSON['links'] = sorted(self.SAMPLE_SCHEMA_JSON['links'])
        self.assertEqual(json_received['links'], self.SAMPLE_SCHEMA_JSON['links'])

    @patch("brainiak.handlers.logger")
    def test_schema_handler_with_invalid_params(self, log):
        response = self.fetch('/person/Gender/_class?hello=world')
        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, '{"error": "HTTP error: 400\\nArgument hello is not supported. The supported arguments are: graph_uri."}')

    @patch("brainiak.handlers.logger")
    def test_schema_handler_class_undefined(self, log):
        response = self.fetch('/animals/Ornithorhynchus/_class')
        self.assertEqual(response.code, 404)
        self.assertEqual(response.body, '{"error": "HTTP error: 404\\nClass (animalsOrnithorhynchus) in graph (animals) was not found."}')


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


class OptionsTestCase(TornadoAsyncHTTPTestCase):

    def test_collection_has_options(self):
        response = self.fetch('/person/Gender/', method='OPTIONS')
        self.assertEqual(response.code, 204)
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], 'GET, POST, OPTIONS')
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], settings.CORS_HEADERS)
