import json
from mock import patch

from brainiak.instance.get_resource import QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE
from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


# FIXME: this test is totally broken - it is acessing http://semantica.globo.com/person/Gender
class InstanceResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/gender.n3", "tests/sample/animalia.n3"]
    graph_uri = "http://test.com/"

    maxDiff = None

    @patch("brainiak.handlers.log")
    def test_get_instance_400(self, log):
        response = self.fetch('/person/Gender/Female?eh=bigoletinha', method='GET')
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.log")
    def test_get_instance_404(self, log):
        response = self.fetch('/person/Gender/Anysexual', method='GET')
        self.assertEqual(response.code, 404)

    def test_get_instance_200(self):
        response = self.fetch('/person/Gender/Female', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(u'/person/Gender/Female', body['@id'])
        self.assertEqual(body['@type'], u'person:Gender')
        self.assertEqual(body['rdf:type'], u'person:Gender')
        self.assertEqual(body['upper:name'], u'Feminino')

    def test_get_instance_with_compressed_instance_prefix_200(self):
        instance_prefix = "http://test.com/other_prefix/"
        response = self.fetch('/person/Gender/Test?instance_prefix={0}&class_uri=http://test.com/person/Gender&lang=en'.format(instance_prefix),
                              method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(instance_prefix + u'Test', body['@id'])
        self.assertEqual(body['@type'], u'person:Gender')
        self.assertEqual(body['rdf:type'], u'http://test.com/person/Gender')
        self.assertEqual(body['rdfs:label'], u'Teste')


class InstanceQueryTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures_by_graph = {
        "http://test.com/": ["tests/sample/animalia.n3"],
        "http://test2.com/": ["tests/sample/animalia.n3"]
    }

    maxDiff = None

    def test_instance_query(self):
        params = {
            "lang": "en",
            "class_uri": "http://example.onto/Yorkshire_Terrier",
            "instance_uri": "http://example.onto/Nina",
            "ruleset": "http://test.com/ruleset"
        }
        query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % params
        computed = self.query(query, False)["results"]["bindings"]
        non_blank_expected = [
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'object': {u'type': u'uri', u'value': u'http://example.onto/Yorkshire_Terrier'},
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'object': {u'type': u'uri', u'value': u'http://example.onto/Canidae'},
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'object': {u'type': u'uri', u'value': u'http://example.onto/Mammalia'},
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'object': {u'type': u'uri', u'value': u'http://example.onto/Animal'},
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'object': {u'type': u'uri', u'value': u'http://example.onto/Species'},
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'object': {u'type': u'uri', u'value': u'http://example.onto/York'},
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/birthCity'},
                u'super_property': {u'type': u'uri', u'value': u'http://example.onto/birthPlace'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'object': {u'type': u'uri', u'value': u'http://example.onto/York'},
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/birthPlace'}
            }
        ]
        for item in non_blank_expected:
            self.assertIn(item, computed)

    def test_instance_query_doesnt_duplicate_equal_properties_from_different_graphs(self):
        response = self.fetch('/anything/Yorkshire_Terrier/Nina?class_prefix=http://example.onto/&instance_prefix=http://example.onto/', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body[u'http://example.onto/birthCity'], u'http://example.onto/York')
