# -*- coding: utf-8 -*-
import json
from jsonschema import Draft4Validator, SchemaError
from mock import patch

from brainiak import settings
from brainiak.schema.get_class import get_cached_schema, SchemaNotFound
from tests.mocks import MockRequest
from tests.sparql import QueryTestCase
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class TestClassResource(TornadoAsyncHTTPTestCase):

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
        self.assertListEqual(received_rels, ['self', 'class', 'collection', 'delete', 'update'])
        # TODO: test the URLs of the links

    def test_schema_handler_with_default_uri_normalization(self):
        response = self.fetch('/person/Gender/_schema')
        self.assertEqual(response.code, 200)
        schema = json.loads(response.body)
        self.assertEqual(schema['id'], u'person:Gender')
        self.assertEqual(schema['$schema'], 'http://json-schema.org/draft-04/schema#')
        try:
            Draft4Validator.check_schema(schema)
        except SchemaError as ex:
            self.fail("Json-schema for class {0} is not valid. Failed for {1:s}".format('person:Gender', ex))

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
        self.assertEqual('http://www.w3.org/2001/XMLSchema#string', json_received['properties']['upper:description']['datatype'])
        self.assertEqual(json_received['id'], u'http://semantica.globo.com/person/Gender')

    def test_schema_handler_with_uri_normalization_expand_both(self):
        response = self.fetch('/person/Gender/_schema?expand_uri_keys=1&expand_uri_values=1')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['id'], u'http://semantica.globo.com/person/Gender')
        self.assertIn('http://semantica.globo.com/upper/isPartOf', json_received['properties'].keys())
        format_value = json_received['properties']['http://semantica.globo.com/upper/description']['datatype']
        self.assertEqual('http://www.w3.org/2001/XMLSchema#string', format_value)

    @patch("brainiak.handlers.logger")
    def test_schema_handler_with_invalid_params(self, log):
        response = self.fetch('/person/Gender/_schema?hello=world')
        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, '{"errors": ["HTTP error: 400\\nArgument hello is not supported. The supported querystring arguments are: expand_uri, expand_uri_keys, expand_uri_values, graph_uri, lang."]}')

    @patch("brainiak.handlers.logger")
    def test_schema_handler_class_undefined(self, log):
        response = self.fetch('/animals/Ornithorhynchus/_schema')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, '{}')

    @patch("brainiak.utils.cache.retrieve", return_value=None)
    @patch("brainiak.schema.get_class.get_schema", return_value={"cached": "false"})
    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_get_cached_schema_miss(self, settings_mock, get_schema_mock, retrieve_mock):
        uri = "http://example.onto/Place/_schema"
        query_params = {
            'class_uri': u'http://example.onto/Place',
            'do_item_count': '0',
            'expand_uri': '0',
            'expand_uri_keys': '0',
            'expand_uri_values': '0',
            'graph_uri': u'http://example.onto/',
            'lang': 'pt',
            'request': MockRequest(uri=uri)
        }
        schema = get_cached_schema(query_params)
        self.assertEqual(schema, {"cached": "false"})

    @patch("brainiak.utils.cache.retrieve", return_value={"body": {"cached": "true"}, "meta": {"cache": "HIT"}})
    @patch("brainiak.schema.get_class.get_schema", return_value={"cached": "false"})
    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_get_cached_schema_hit(self, settings_mock, get_schema_mock, retrieve_mock):
        uri = "http://example.onto/Place/_schema"
        query_params = {
            'class_uri': u'http://example.onto/Place',
            'do_item_count': '0',
            'expand_uri': '0',
            'expand_uri_keys': '0',
            'expand_uri_values': '0',
            'graph_uri': u'http://example.onto/',
            'lang': 'pt',
            'request': MockRequest(uri=uri)
        }
        schema = get_cached_schema(query_params)
        self.assertEqual(schema, {"cached": "true"})

    @patch("brainiak.schema.get_class.expand_all_uris_recursively", return_value={})
    @patch("brainiak.schema.get_class.get_schema", return_value={"cached": "false"})
    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_get_cached_schema_raise_schema_not_found_exception(self, settings_mock, get_schema_mock, expand_all_uris_recursively_mock):
        uri = "http://example.onto/Place/_schema"
        query_params = {
            'class_uri': u'http://example.onto/Place',
            'do_item_count': '0',
            'expand_uri': '0',
            'expand_uri_keys': '0',
            'expand_uri_values': '0',
            'graph_uri': u'http://example.onto/',
            'lang': 'pt',
            'request': MockRequest(uri=uri)
        }
        with self.assertRaises(SchemaNotFound) as exception:
            schema = get_cached_schema(query_params)
            self.assertEqual(
                "SchemaNotFound: The class definition for http://example.onto/Place was not found in graph http://example.onto/",
                str(exception.exception)
            )


class GetClassTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    fixtures_by_graph = {
        "http://example.onto/": ["tests/sample/animalia.n3"],
        "http://extra.onto/": ["tests/sample/animalia_extension.n3"],
    }
    maxDiff = None
    allow_triplestore_connection = True

    def test_property_redefined_in_subclass(self):
        response = self.fetch('/_/_/_schema?graph_uri=http://extra.onto/&class_uri=http://example.onto/Golden_Retriever')
        self.assertEqual(response.code, 200)
        computed = json.loads(response.body)["properties"]["http://example.onto/description"]
        expected = {
            u'format': u'',
            u'datatype': u'xsd:string',
            u'graph': u'http://example.onto/',
            u'required': True,
            u'range': [{u'type': u'string'}],
            u'title': u'Description of a place',
            u'type': u'string'
        }
        # expected = {
        #     u'datatype': u'xsd:string',
        #     u'graph': u'http://extra.onto/',
        #     u'required': True,
        #     u'title': u'Description of a place',
        #     u'type': u'string'
        # }
        self.assertEqual(computed, expected)
