import json
from mock import patch

from tests import TornadoAsyncHTTPTestCase


class InstanceResourceTestCase(TornadoAsyncHTTPTestCase):

    maxDiff = None

    @patch("brainiak.handlers.log")
    def test_get_instance_400(self, log):
        response = self.fetch('/place/City/Tatilandia?eh=bigoletinha', method='GET')
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
        response = self.fetch('/place/City/Cidade_Uberaba_MG?instance_prefix=base', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(u'/place/City/_schema', body['$schema'])
        self.assertIn(u'/place/City/Cidade_Uberaba_MG?instance_prefix=base', body['@id'])
        self.assertEqual(body['@type'], u'place:City')
        #self.assertItemsEqual(body['rdf:type'], [u'place:City', u'base:Cidade'])
        #self.assertEqual(body['rdfs:label'], u'Uberaba')

    def test_get_instance_with_expanded_instance_prefix_200(self):
        response = self.fetch('/place/City/Cidade_Uberaba_MG?instance_prefix=http://semantica.globo.com/base/', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(u'/place/City/_schema', body['$schema'])
        self.assertIn(u'/place/City/Cidade_Uberaba_MG?instance_prefix=http://semantica.globo.com/base/', body['@id'])
        self.assertEqual(body['@type'], u'place:City')
        #self.assertItemsEqual(body['rdf:type'], [u'place:City', u'base:Cidade'])
        #self.assertEqual(body['rdfs:label'], u'Uberaba')
