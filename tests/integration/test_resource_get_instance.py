import json
from mock import patch

from brainiak.instance import get_resource
from tests import TornadoAsyncHTTPTestCase, MockRequest
from tests.sparql import QueryTestCase


class InstanceResourceTestCase(TornadoAsyncHTTPTestCase):

    maxDiff = None

    @patch("brainiak.handlers.log")
    def test_filter_with_invalid_query_string(self, log):
        response = self.fetch('/person/Gender/Anysexual', method='GET')
        self.assertEqual(response.code, 404)

    def test_filter_without_predicate_and_object(self):
        response = self.fetch('/person/Gender/Female', method='GET')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIn(u'person/Gender/_schema', body['$schema'])
        self.assertIn(u'/person/Gender/Female', body['@id'])
        self.assertEqual(body['@type'], u'person:Gender')
        self.assertEqual(body['rdf:type'], u'person:Gender')
        self.assertEqual(body['rdfs:label'], u'Female')
