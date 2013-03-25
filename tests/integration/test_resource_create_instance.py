import json
import uuid

from mock import patch

from brainiak.instance import create_resource
from brainiak.instance.delete_resource import QUERY_DELETE_INSTANCE
from brainiak.schema import resource as schema_resource
from tests import TornadoAsyncHTTPTestCase, MockRequest
from tests.sparql import QueryTestCase


JSON_CITY_GLOBOLAND = {
    "@context": {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "place": "http://semantica.globo.com/place/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "base": "http://semantica.globo.com/base/",
        "upper": "http://semantica.globo.com/upper/"
    },
    "upper:name": "Globoland",
    "upper:fullName": "Globoland (RJ)",
    "rdfs:comment": "City of Globo's companies. Historically known as PROJAC.",
    "place:partOfState": "base:UF_RJ",
    "place:latitude": "-22.958314",
    "place:longitude": "-43.407133"
}


class CollectionResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    allow_triplestore_connection = True
    graph_uri = 'http://semantica.globo.com/sample-place/'
    fixtures = []

    def setUp(self):
        self.original_uuid = uuid.uuid4
        self.original_schema_resource_get_schema = schema_resource.get_schema
        uuid.uuid4 = lambda: "unique-id"
        super(CollectionResourceTestCase, self).setUp()

    def tearDown(self):

        query_string = QUERY_DELETE_INSTANCE % {
            "graph_uri": 'http://semantica.globo.com/place/',
            "instance_uri": 'http://semantica.globo.com/place/City/unique-id'
        }
        self.query(query_string)
        uuid.uuid4 = self.original_uuid
        schema_resource.get_schema = self.original_schema_resource_get_schema
        super(CollectionResourceTestCase, self).tearDown()

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
    def test_create_instance_201(self, log):
        schema_resource.get_schema = lambda params: True
        payload = JSON_CITY_GLOBOLAND
        response = self.fetch('/sample-place/City',
            method='POST',
            body=json.dumps(payload))
        self.assertEqual(response.code, 201)
        self.assertEqual(response.headers['Location'], 'http://semantica.globo.com/sample-place/City/unique-id')
        self.assertEqual(response.body, "ok")
