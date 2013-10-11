import json
from mock import patch
from brainiak import settings, server

from brainiak.instance.get_instance import QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE
from brainiak.settings import URI_PREFIX
from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class TestInstanceResource(TornadoAsyncHTTPTestCase):

    def get_app(self):
        return server.Application()

    @patch("brainiak.handlers.logger")
    def test_get_instance_with_nonexistent_uri(self, log):
        response = self.fetch('/person/Gender/Alien')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, '{}')

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


class InstanceResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/gender.n3", "tests/sample/animalia.n3"]
    graph_uri = "http://test.com/"

    maxDiff = None

    @patch("brainiak.handlers.logger")
    def test_get_instance_400(self, log):
        response = self.fetch('/person/Gender/Female?eh=bigoletinha', method='GET')
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.logger")
    def test_get_instance_404(self, log):
        response = self.fetch('/person/Gender/Anysexual', method='GET')
        self.assertEqual(response.code, 404)

    def test_get_instance_200(self):
        response = self.fetch('/person/Gender/Female?lang=pt', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(u'/person/Gender/Female', body['@id'])
        self.assertEqual(body['@type'], u'person:Gender')
        self.assertEqual(body['rdf:type'], u'person:Gender')
        self.assertEqual(body['upper:name'], u'Feminino')

    def test_get_instance_200_with_expanded_uris(self):
        response = self.fetch('/person/Gender/Female?expand_uri=1', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)

        self.assertEqual(body[u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'], URI_PREFIX + u'person/Gender')
        self.assertEqual(body[URI_PREFIX + u'upper/name'], u'Feminino')

    def test_get_instance_200_with_expanded_both(self):
        response = self.fetch('/person/Gender/Female?expand_uri=1', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(body[u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'], URI_PREFIX + u'person/Gender')
        self.assertEqual(body[URI_PREFIX + u'upper/name'], u'Feminino')
        self.assertEqual(body['@type'], URI_PREFIX + u'person/Gender')

    def test_get_instance_returns_schema_in_content_type(self):
        response = self.fetch('/person/Gender/Female', method='GET')
        self.assertEqual(response.code, 200)
        content_type = response.headers["Content-type"]
        self.assertTrue(content_type.startswith('application/json; profile=http://localhost:'))
        self.assertTrue(content_type.endswith('/person/Gender/_schema'))

    def test_get_instance_with_compressed_instance_prefix_200(self):
        instance_prefix = "http://test.com/other_prefix/"
        response = self.fetch('/person/Gender/Test?instance_prefix={0}&class_uri=http://test.com/person/Gender&lang=en'.format(instance_prefix),
                              method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(instance_prefix + u'Test', body['@id'])
        self.assertEqual(body['@type'], u'http://test.com/person/Gender')
        self.assertEqual(body['rdf:type'], u'http://test.com/person/Gender')
        self.assertEqual(body['rdfs:label'], u'Teste')


class InstanceResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/gender.n3", "tests/sample/animalia.n3"]
    graph_uri = "http://test.com/"

    maxDiff = None

    def test_instance_query_doesnt_duplicate_equal_properties_from_different_graphs(self):
        response = self.fetch('/_/Yorkshire_Terrier/Nina?class_prefix=http://example.onto/&instance_prefix=http://example.onto/', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body[u'http://example.onto/birthCity'], u'http://example.onto/York')


class InstanceWithExpandedPropertiesTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures_by_graph = {
        "http://brmedia.com/": ["tests/sample/sports.n3"]
    }

    maxDiff = None

    def test_instance_query(self):
        params = {
            "lang": "en",
            "class_uri": "http://dbpedia.org/ontology/News",
            "instance_uri": "http://brmedia.com/news_cricket",
            "ruleset": "http://brmedia.com/ruleset",
            "object_label_variable": "?object_label",
            "object_label_optional_clause": "OPTIONAL { ?object rdfs:label ?object_label } ."
        }
        query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % params
        computed = self.query(query, False)["results"]["bindings"]
        expected = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                u'object': {u'type': u'literal', u'value': u'Cricket becomes the most popular sport of Brazil'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'object_label': {u'type': u'literal', u'value': u'News'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://brmedia.com/related_to'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/Cricket'},
                u'object_label': {u'type': u'literal', u'value': u'Cricket'}
            }
        ]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_instance_query_expand_object_properties_is_not_defined(self):
        response = self.fetch('/dbpedia/News/news_cricket?instance_prefix=http://brmedia.com/', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body[u'http://brmedia.com/related_to'], u'dbpedia:Cricket')

    def test_instance_query_expand_object_properties_is_false(self):
        response = self.fetch('/dbpedia/News/news_cricket?instance_prefix=http://brmedia.com/&expand_object_properties=0', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body[u'http://brmedia.com/related_to'], u'dbpedia:Cricket')

    def test_instance_query_expand_object_properties_is_true(self):
        response = self.fetch('/dbpedia/News/news_cricket?instance_prefix=http://brmedia.com/&expand_object_properties=1', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body[u'http://brmedia.com/related_to'], {"@id": "dbpedia:Cricket", "title": "Cricket"})
