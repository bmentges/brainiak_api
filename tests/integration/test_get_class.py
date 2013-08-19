# -*- coding: utf-8 -*-
import json
from mock import patch

from brainiak import settings
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class TestClassResource(TornadoAsyncHTTPTestCase):

    SAMPLE_SCHEMA_JSON = {
        u'$schema': u'http://json-schema.org/draft-03/schema#',
        u'@context': {u'@language': u'pt', u'person': u'http://semantica.globo.com/person/'},
        u'id': u'person:Gender',
        u'links': [
            {u'href': u'http://localhost:10023/person/Gender/{_resource_id}?lang=pt', u'method': u'GET', u'rel': u'self'},
            {u'href': u'http://localhost:10023/person/Gender/_schema?lang=pt', u'method': u'GET', u'rel': u'class'},
            {u'href': u'http://localhost:10023/person/Gender/{@resource_id}?lang=pt', u'method': u'DELETE', u'rel': u'delete'},
            {u'href': u'http://localhost:10023/person/Gender/{@resource_id}?lang=pt', u'method': u'PUT', u'rel': u'replace', u'schema': {u'$ref': u'http://localhost:10023/person/Gender/_schema'}},
            {u'href': u'http://localhost:10023/person/Gender?class_prefix=http%3A%2F%2Fsemantica.globo.com%2Fperson%2F', u'method': u'GET', u'rel': u'collection'}],
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
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], settings.CORS_HEADERS)

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
        received_rels = [link['rel'] for link in json_received['links']]
        self.assertListEqual(received_rels, ['self', 'class', 'collection', 'delete', 'replace'])
        # TODO: test the URLs of the links

    def test_schema_handler_with_default_uri_normalization(self):
        response = self.fetch('/person/Gender/_schema')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['id'], u'person:Gender')

    def test_schema_handler_with_uri_normalization_shorten(self):
        response = self.fetch('/person/Gender/_schema?expand_uri=0')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['id'], u'person:Gender')

    def test_schema_handler_with_uri_normalization_expand(self):
        response = self.fetch('/person/Gender/_schema?expand_uri=1')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['id'], u'http://semantica.globo.com/person/Gender')

    def test_schema_handler_with_uri_normalization_expand_just_keys(self):
        response = self.fetch('/person/Gender/_schema?expand_uri_keys=1')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertIn('http://semantica.globo.com/upper/isPartOf', json_received['properties'].keys())
        self.assertEqual(json_received['id'], u'person:Gender')

    def test_schema_handler_with_uri_normalization_expand_just_values(self):
        response = self.fetch('/person/Gender/_schema?expand_uri_values=1')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual('http://www.w3.org/2001/XMLSchema#string', json_received['properties']['upper:description']['format'])
        self.assertEqual(json_received['id'], u'http://semantica.globo.com/person/Gender')

    def test_schema_handler_with_uri_normalization_expand_both(self):
        response = self.fetch('/person/Gender/_schema?expand_uri_keys=1&expand_uri_values=1')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['id'], u'http://semantica.globo.com/person/Gender')
        self.assertIn('http://semantica.globo.com/upper/isPartOf', json_received['properties'].keys())
        format_value = json_received['properties']['http://semantica.globo.com/upper/description']['format']
        self.assertEqual('http://www.w3.org/2001/XMLSchema#string', format_value)

    @patch("brainiak.handlers.logger")
    def test_schema_handler_with_invalid_params(self, log):
        response = self.fetch('/person/Gender/_schema?hello=world')
        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, '{"error": "HTTP error: 400\\nArgument hello is not supported. The supported querystring arguments are: expand_uri, expand_uri_keys, expand_uri_values, graph_uri, lang."}')

    @patch("brainiak.handlers.logger")
    def test_schema_handler_class_undefined(self, log):
        response = self.fetch('/animals/Ornithorhynchus/_schema')
        self.assertEqual(response.code, 404)
        self.assertEqual(response.body, '{"error": "HTTP error: 404\\nClass (animalsOrnithorhynchus) in graph (animals) was not found."}')
