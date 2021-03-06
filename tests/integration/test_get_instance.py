import json
from mock import patch
import ujson
from brainiak import settings, server

from brainiak.instance import get_instance
from brainiak.settings import URI_PREFIX
from brainiak.utils.cache import connect
from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class TestInstanceResource(TornadoAsyncHTTPTestCase):

    def get_app(self):
        return server.Application()

    @patch("brainiak.handlers.logger")
    def test_get_instance_with_nonexistent_uri(self, log):
        response = self.fetch('/person/Gender/Alien')
        self.assertEqual(response.code, 404)

    def test_get_instance(self):
        response = self.fetch('/person/Gender/Male')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['@type'], 'person:Gender')
        self.assertEqual(json_received['@id'], "http://semantica.globo.com/person/Gender/Male")
        self.assertEqual(json_received['_resource_id'], "Male")
        self.assertEqual(json_received['_instance_prefix'], "http://semantica.globo.com/person/Gender/")

    def test_instance_has_options(self):
        response = self.fetch('/person/Gender/Female', method='OPTIONS')
        self.assertEqual(response.code, 204)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], settings.CORS_HEADERS)

    def test_instance_by_uri(self):
        response = self.fetch('/_/_/_/?instance_uri=http://semantica.globo.com/person/Gender/Female')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['@type'], 'person:Gender')
        self.assertEqual(json_received['@id'], "http://semantica.globo.com/person/Gender/Female")
        self.assertEqual(json_received['_resource_id'], "Female")
        self.assertEqual(json_received['_instance_prefix'], "http://semantica.globo.com/person/Gender/")


class InstanceResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

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

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_get_instance_200(self, mock_cache):
        response = self.fetch('/person/Gender/Female?lang=pt', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(u'/person/Gender/Female', body['@id'])
        self.assertEqual(body['@type'], u'person:Gender')
        self.assertEqual(body['upper:name'], u'Feminino')
        self.assertTrue(response.headers['X-Cache'].startswith('MISS from localhost'))

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_get_instance_200_now_cached(self, mock_cache):
        response = self.fetch('/person/Gender/Female?lang=pt', method='GET')
        first_to_cache = json.loads(response.body)
        response = self.fetch('/person/Gender/Female?lang=pt', method='GET')
        body = ujson.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(u'/person/Gender/Female', body['@id'])
        self.assertTrue(response.headers['X-Cache'].startswith('HIT'))

    def test_get_instance_200_with_expanded_uris(self):
        response = self.fetch('/person/Gender/Female?expand_uri=1', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)

        self.assertEqual(body[u'@type'], URI_PREFIX + u'person/Gender')
        self.assertEqual(body[URI_PREFIX + u'upper/name'], u'Feminino')

    def test_get_instance_200_with_expanded_both(self):
        response = self.fetch('/person/Gender/Female?expand_uri=1', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(body[u'@type'], URI_PREFIX + u'person/Gender')
        self.assertEqual(body[URI_PREFIX + u'upper/name'], u'Feminino')

    def test_get_instance_returns_schema_in_content_type(self):
        response = self.fetch('/person/Gender/Female', method='GET')
        self.assertEqual(response.code, 200)
        content_type = response.headers["Content-type"]
        self.assertTrue(content_type.startswith('application/json; profile=http://localhost:'))
        self.assertTrue(content_type.endswith('/person/Gender/_schema'))

    def test_get_instance_with_compressed_instance_prefix_200(self):
        instance_prefix = "http://test.com/other_prefix/"
        response = self.fetch('/person/Gender/Test?instance_prefix={0}&class_uri=http://test.com/person/Gender&graph_uri={1}&lang=en'.format(instance_prefix, self.graph_uri),
                              method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(instance_prefix + u'Test', body['@id'])
        self.assertEqual(body['@type'], u'http://test.com/person/Gender')
        self.assertEqual(body['_type_title'], u'Gender')


class InstancePropertiesTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    fixtures = ["tests/sample/gender.n3", "tests/sample/animalia.n3"]
    graph_uri = "http://test.com/"

    maxDiff = None

    def test_instance_query_doesnt_duplicate_equal_properties_from_different_graphs(self):
        response = self.fetch('/_/Yorkshire_Terrier/Nina?class_prefix=http://example.onto/&instance_prefix=http://example.onto/&graph_uri=http://test.com/', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body[u'http://example.onto/birthCity'], [u'http://example.onto/York'])

    def test_instance_has_property_that_is_array_but_contains_a_single_value(self):
        response = self.fetch('/_/Human/RodrigoSenra?class_prefix=http://example.onto/&instance_prefix=http://example.onto/&graph_uri=http://test.com/&expand_object_properties=1', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(
            body[u'http://example.onto/hasChild'],
            [{u'@id': u'http://example.onto/Naruto', u'title': u'Naruto Senra'}]
        )


class InstanceWithExpandedPropertiesTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    fixtures_by_graph = {
        "http://brmedia.com/": ["tests/sample/sports.n3"]
    }

    maxDiff = None

    def test_instance_query(self):
        params = {
            "lang": "en",
            "class_uri": "http://dbpedia.org/ontology/News",
            "graph_uri": "http://brmedia.com/",
            "instance_uri": "http://brmedia.com/news_cricket",
            "ruleset": "http://brmedia.com/ruleset",
            "object_label_variable": "?object_label",
            "object_label_optional_clause": "OPTIONAL { ?object rdfs:label ?object_label } ."
        }
        query = get_instance.QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % params
        computed = self.query(query, False)["results"]["bindings"]
        expected = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'object_label': {u'type': u'literal', u'value': u'News'},
                u'is_object_blank': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'0'
                }
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                u'object': {u'type': u'literal', u'value': u'Cricket becomes the most popular sport of Brazil'},
                u'is_object_blank': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'0'
                }
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://brmedia.com/related_to'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/Cricket'},
                u'object_label': {u'type': u'literal', u'value': u'Cricket'},
                u'is_object_blank': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'0'
                }
            }
        ]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_instance_query_by_instance_uri(self):
        params = {
            "lang": "en",
            "class_uri": "_/_",
            "graph_uri": "_",
            "instance_uri": "http://brmedia.com/news_cricket",
            "ruleset": "http://brmedia.com/ruleset",
            "object_label_variable": "?object_label",
            "object_label_optional_clause": "OPTIONAL { ?object rdfs:label ?object_label } ."
        }
        query = get_instance.QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE_BY_URI % params
        computed = self.query(query, False)["results"]["bindings"]
        expected = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'object_label': {u'type': u'literal', u'value': u'News'},
                u'class_uri': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'graph_uri': {u'type': u'uri', u'value': u'http://brmedia.com/'}
            },
            {

                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                u'object': {u'type': u'literal', u'value': u'Cricket becomes the most popular sport of Brazil'},
                u'class_uri': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'graph_uri': {u'type': u'uri', u'value': u'http://brmedia.com/'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://brmedia.com/related_to'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/Cricket'},
                u'object_label': {u'type': u'literal', u'value': u'Cricket'},
                u'class_uri': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'graph_uri': {u'type': u'uri', u'value': u'http://brmedia.com/'}
            }
        ]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_instance_query_expand_object_properties_is_not_defined(self):
        response = self.fetch('/dbpedia/News/news_cricket?instance_prefix=http://brmedia.com/&graph_uri=http://brmedia.com/', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body[u'http://brmedia.com/related_to'], [u'dbpedia:Cricket'])

    def test_instance_query_expand_object_properties_is_false(self):
        response = self.fetch('/dbpedia/News/news_cricket?instance_prefix=http://brmedia.com/&expand_object_properties=0&graph_uri=http://brmedia.com/', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body[u'http://brmedia.com/related_to'], [u'dbpedia:Cricket'])

    def test_instance_query_expand_object_properties_is_true(self):
        response = self.fetch('/dbpedia/News/news_cricket?instance_prefix=http://brmedia.com/&expand_object_properties=1&graph_uri=http://brmedia.com/', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body[u'http://brmedia.com/related_to'], [{u"@id": u"dbpedia:Cricket", u"title": u"Cricket"}])


class InstanceCauseSchemaToBeCachedTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    fixtures_by_graph = {"http://brmedia.com/": ["tests/sample/sports.n3"]}
    maxDiff = None
    redis_test_client = connect()

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_get_instance_generate_schema_cache_entry(self, mock_settings):
        expected_redis_key = "http://brmedia.com/@@http://dbpedia.org/ontology/News##class"
        # Clean cache
        self.redis_test_client.delete([expected_redis_key])

        class_response = self.fetch('/dbpedia/News/_schema?class_prefix=http://dbpedia.org/ontology/&graph_uri=http://brmedia.com/', method='GET')
        self.assertEqual(class_response.code, 200)
        cached_schema_by_direct_access_str = self.redis_test_client.get(expected_redis_key)
        cached_schema_by_direct_access = ujson.loads(cached_schema_by_direct_access_str)
        last_modified = cached_schema_by_direct_access['meta']['last_modified']

        # Clean cache
        self.redis_test_client.delete([expected_redis_key])

        instance_response = self.fetch('/dbpedia/News/news_cricket?instance_prefix=http://brmedia.com/&graph_uri=http://brmedia.com/', method='GET')
        self.assertEqual(instance_response.code, 200)
        cached_schema_caused_by_get_instance_str = self.redis_test_client.get(expected_redis_key)
        cached_schema_caused_by_get_instance = ujson.loads(cached_schema_caused_by_get_instance_str)

        self.assertEqual(cached_schema_caused_by_get_instance['body'], cached_schema_by_direct_access['body'])
        self.assertEqual(last_modified, cached_schema_by_direct_access['meta']['last_modified'])
