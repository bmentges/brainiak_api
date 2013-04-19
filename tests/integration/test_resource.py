# coding: utf-8
import json
from urlparse import urlparse
from mock import patch
from brainiak import __version__, settings, server
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class TestInstanceResource(TornadoAsyncHTTPTestCase):

    def get_app(self):
        return server.Application()

    @patch("brainiak.handlers.log")
    def test_get_instance_with_nonexistent_uri(self, log):
        response = self.fetch('/person/Gender/Alien')
        self.assertEqual(response.code, 404)
        self.assertEqual(response.body, '{"error": "HTTP error: 404\\nInstance (http://semantica.globo.com/person/Gender/Alien) of class (http://semantica.globo.com/person/Gender) in graph (http://semantica.globo.com/person/) was not found."}')

    def test_get_instance(self):
        response = self.fetch('/person/Gender/Male')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertTrue(json_received['$schema'].endswith('_schema'))

    def test_instance_has_options(self):
        response = self.fetch('/person/Gender/Female', method='OPTIONS')
        self.assertEqual(response.code, 204)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], 'Content-Type')


class TestSchemaResource(TornadoAsyncHTTPTestCase):

    SAMPLE_SCHEMA_JSON = {
        u'$schema': u'http://json-schema.org/draft-03/schema#',
        u'@context': {u'@language': u'pt', u'person': u'http://semantica.globo.com/person/'},
        u'@id': u'person:Gender',
        u'links': [
            {u'href': u'http://localhost:10023/person/Gender/_schema?lang=pt', u'method': u'GET', u'rel': u'self'},
            {u'href': u'http://localhost:10023/person/Gender', u'method': u'GET', u'rel': u'instances'}],
        u'properties': {},
        u'title': u"Gênero da Pessoa",
        u'comment': u"Gênero de uma pessoa.",
        u'type': u'object'
    }

    maxDiff = None

    def test_collection_has_options(self):
        response = self.fetch('/person/Gender/_schema', method='OPTIONS')
        self.assertEqual(response.code, 204)
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], 'GET, OPTIONS')
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], 'Content-Type')

    def test_schema_has_options(self):
        response = self.fetch('/person/Gender/_schema', method='OPTIONS')
        self.assertEqual(response.code, 204)

    def test_schema_has_cors(self):
        response = self.fetch('/person/Gender/_schema', method='OPTIONS')
        response.headers['Access-Control-Allow-Methods']

    def test_schema_handler_with_lang(self):
        response = self.fetch('/person/Gender/_schema?lang=pt')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        # Adjust dynamic port from real to expected prior to comparison
        effective_port = str(urlparse(json_received[u'links'][0][u'href']).port)
        for entry in self.SAMPLE_SCHEMA_JSON[u'links']:
            entry[u'href'] = entry[u'href'].replace('10023', effective_port)

        json_received['links'] = sorted(json_received['links'])
        self.SAMPLE_SCHEMA_JSON['links'] = sorted(self.SAMPLE_SCHEMA_JSON['links'])
#        self.assertEqual(sorted(json_received['links']), sorted(self.SAMPLE_SCHEMA_JSON['links']))
        self.assertEqual(json_received['links'], self.SAMPLE_SCHEMA_JSON['links'])

    @patch("brainiak.handlers.log")
    def test_schema_handler_with_invalid_params(self, log):
        response = self.fetch('/person/Gender/_schema?hello=world')
        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, '{"error": "HTTP error: 400\\nArgument hello is not supported"}')

    # TODO: We should test with old models as well.
    # However, we need to isolate ontologies snippets from upper and from base
    # into .n3 files to be used as input for Brainiak

    # OLD_SCHEMA_JSON = {
    #     u'$schema': u'http://json-schema.org/draft-03/schema#',
    #     u'@context': {u'@language': u'pt',
    #                   u'rdf': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    #                   u'rdfs': u'http://www.w3.org/2000/01/rdf-schema#'},
    #     u'@id': u'http://semantica.globo.com/base/Acordo',
    #     u'links': [{u'href': u'/foaf/Agent', u'rel': u'foaf:maker'},
    #                {u'href': u'/foaf/Image', u'rel': u'foaf:depiction'},
    #                {u'href': u'/foaf/Document', u'rel': u'foaf:page'},
    #                {u'href': u'/foaf/Document', u'rel': u'foaf:homepage'},
    #                {u'href': u'/owl/Thing', u'rel': u'foaf:fundedBy'},
    #                {u'href': u'/owl/Thing', u'rel': u'foaf:theme'},
    #                {u'href': u'/owl/Thing', u'rel': u'foaf:logo'}],
    #     u'properties': {u'http://teste.com/thumbnail': {u'graph': u'http://teste.com/',
    #                                                     u'title': u'Icone',
    #                                                     u'type': u'any'},
    #                     u'rdfs:label': {u'graph': u'http://teste.com/',
    #                                     u'title': u'Nome Popular',
    #                                     u'type': u'any'}},
    #     u'title': u'Acordo',
    #     u'type': u'object'}
    #
    # def test_schema_handler_without_lang(self):
    #     response = self.fetch('/base/Acordo/_schema?graph_uri=http%3A//semantica.globo.com/&lang=undefined')
    #     self.assertEqual(response.code, 200)
    #     json_received = json.loads(response.body)
    #     self.assertEqual(json_received, self.OLD_SCHEMA_JSON)

    @patch("brainiak.handlers.log")
    def test_schema_handler_class_undefined(self, log):
        response = self.fetch('/animals/Ornithorhynchus/_schema')
        self.assertEqual(response.code, 404)
        self.assertEqual(response.body, '{"error": "HTTP error: 404\\nClass (http://semantica.globo.com/animals/Ornithorhynchus) in graph (http://semantica.globo.com/animals/) was not found."}')


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

    def setUp(self):
        self.original_settings_env = settings.ENVIRONMENT
        super(TestVirtuosoStatusResource, self).setUp()

    def tearDown(self):
        settings.ENVIRONMENT = self.original_settings_env

    @patch("brainiak.handlers.log")  # test fails otherwise because log.logger is None
    def test_virtuoso_status_in_prod(self, log):
        settings.ENVIRONMENT = "prod"
        response = self.fetch('/status/virtuoso', method='GET')
        self.assertEqual(response.code, 404)

    def test_virtuoso_status_in_non_prod(self):
        settings.ENVIRONMENT = "local"
        response = self.fetch('/status/virtuoso', method='GET')
        self.assertEqual(response.code, 200)
