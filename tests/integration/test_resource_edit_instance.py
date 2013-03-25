from mock import patch
import json

from brainiak import triplestore, server
from tests import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class InstanceResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    graph_uri = "http://tatipedia.org/test"
    fixtures = ["tests/sample/instances.n3"]

    JSON_NEW_YORK_ADD_CONTINENT = {
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "place": "http://tatipedia.org/test/Place/",
            "tpedia": "http://tatipedia.org/test/",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        },
        "tpedia:partOfContinent": "place:America"
    }

    maxDiff = None

    def get_app(self):
        return server.Application()

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        triplestore.query_sparql = lambda query: self.query(query)
        super(InstanceResourceTestCase, self).setUp()

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    @patch("brainiak.handlers.log")
    @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    def test_edit_instance_400(self, log, settings):
        response = self.fetch('/test/place/new_york?wrong_param=wrong_value', method='PATCH')
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.log")
    @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    def test_edit_instance_404(self, log, settings):
        response = self.fetch('/test/place/InexistentCity', method='PATCH')
        self.assertEqual(response.code, 404)

    @patch("brainiak.handlers.log")
    @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    def test_edit_instance_200_adding_predicate(self, log, settings):
        actual_new_york = self.fetch('/test/place/new_york', method='GET')
        self.assertEqual(actual_new_york.code, 200)
        actual_new_york_dict = json.loads(actual_new_york.body)
        self.assertIn("rdfs:label", actual_new_york_dict)
        self.assertIn("rdfs:comment", actual_new_york_dict)

        modified_new_york = self.fetch('/test/place/new_york', method='PATCH')
        self.assertEqual(modified_new_york.code, 200)
        modified_new_york_dict = json.loads(modified_new_york.body)
        self.assertIn("rdfs:label", modified_new_york_dict)
        self.assertIn("rdfs:comment", modified_new_york_dict)
        self.assertIn("place:partOfContinent", modified_new_york_dict)
        self.assertEqual(modified_new_york_dict["place:partOfContinent"],
                         self.JSON_new_york_ADD_CONTINENT["place:partOfContinent"])
