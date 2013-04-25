import json
from mock import patch

from brainiak.instance.get_resource import QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE
from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


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
        self.assertEqual(body['rdfs:label'], u'Feminino')

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


class InstanceQueryTestCase(QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/animalia.n3"]
    graph_uri = "http://test.com/"

    maxDiff = None

    def test_instance_query(self):
        params = {
            "lang": "en",
            "class_uri": "http://example.onto/Yorkshire_Terrier",
            "instance_uri": "http://example.onto/Nina",
            "ruleset": "http://test.com/ruleset"
        }
        query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % params
        computed = self.query(query)["results"]["bindings"]
        non_blank_expected = [
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'o': {u'type': u'uri', u'value': u'http://example.onto/Yorkshire_Terrier'},
                u'p': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'o': {u'type': u'uri', u'value': u'http://example.onto/Canidae'},
                u'p': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'o': {u'type': u'uri', u'value': u'http://example.onto/Mammalia'},
                u'p': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'o': {u'type': u'uri', u'value': u'http://example.onto/Animal'},
                u'p': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'o': {u'type': u'uri', u'value': u'http://example.onto/Species'},
                u'p': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'o': {u'type': u'uri', u'value': u'http://example.onto/York'},
                u'p': {u'type': u'uri', u'value': u'http://example.onto/birthCity'},
                u'super_property': {u'type': u'uri', u'value': u'http://example.onto/birthPlace'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Nina Fox'},
                u'o': {u'type': u'uri', u'value': u'http://example.onto/York'},
                u'p': {u'type': u'uri', u'value': u'http://example.onto/birthPlace'}
            }
        ]
        for item in non_blank_expected:
            self.assertIn(item, computed)
