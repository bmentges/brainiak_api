import json
from mock import patch

from tests import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class InstanceResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/gender.n3"]
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
        self.assertIn(u'person/Gender/_schema', body['$schema'])
        self.assertIn(u'/person/Gender/Female', body['@id'])
        self.assertEqual(body['@type'], u'person:Gender')
        self.assertEqual(body['rdf:type'], u'person:Gender')
        self.assertItemsEqual(body['rdfs:label'], [u'Female', u'Feminino'])

    def test_get_instance_with_compressed_instance_prefix_200(self):
        response = self.fetch('/person/Gender/Test?instance_prefix=http://test.com/other_prefix/&class_uri=http://test.com/person/Gender', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(u'/person/Gender/_schema', body['$schema'])
        self.assertIn(u'/person/Gender/Test?instance_prefix=http://test.com/other_prefix/', body['@id'])
        self.assertEqual(body['@type'], u'person:Gender')
        self.assertEqual(body['rdf:type'], u'http://test.com/person/Gender')
        self.assertEqual(body['rdfs:label'], u'Teste')
