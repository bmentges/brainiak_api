import json
from mock import patch

from brainiak.instance import create_resource
from tests import TornadoAsyncHTTPTestCase, MockRequest
from tests.sparql import QueryTestCase


JSON_CITY_GLOBOLAND = {
    "@context": {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "place": "http://semantica.globo.com/place/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "base": "http://semantica.globo.com/base/"
    },
    "upper:name": "Globoland",
    "upper:fullName": "Globoland (RJ)",
    "rdfs:comment": "City of Globo's organizations. Historically known as PROJAC.",
    "place:partOfState": "base:UF_RJ"
}


class InstanceResourceTestCase(TornadoAsyncHTTPTestCase):

    maxDiff = None

    @patch("brainiak.handlers.log")
    def test_create_instance_404_inexistant_class(self, log):
        payload = {}
        response = self.fetch('/xubiru/X',
            method='POST',
            body=json.dumps(payload))
        self.assertEqual(response.code, 404)
        body = json.loads(response.body)
        self.assertEqual(body["error"], u"HTTP error: 404\nClass X doesn't exist in context xubiru.")

    @patch("brainiak.handlers.log")
    def test_create_instance_200(self, log):
        payload = JSON_CITY_GLOBOLAND
        response = self.fetch('/place/City',
            method='POST',
            body=json.dumps(payload))
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, "ok")
