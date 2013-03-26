from mock import patch
import json
from brainiak import server
from brainiak.instance import create_resource, edit_resource
from brainiak.utils.sparql import is_modify_response_successful

from tests import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class EditInstanceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    # The class variables below are handled by QueryTestCase
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

    def get_app(self):
        return server.Application()

    def setUp(self):
        super(EditInstanceTestCase, self).setUp()

    def tearDown(self):
        pass

    @patch("brainiak.handlers.log")
    @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    def test_edit_instance_400_no_body(self, log, settings):
        response = self.fetch('/test/Place/new_york?wrong_param=wrong_value', method='PUT')
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.log")
    @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    def test_edit_instance_400_wrong_params(self, log, settings):
        response = self.fetch('/test/Place/new_york?wrong_param=wrong_value', method='PUT', body=json.dumps({}))
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.log")
    @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    def test_edit_instance_404(self, log, settings):
        response = self.fetch('/test/Place/InexistentCity', method='PUT', body=json.dumps({}))
        self.assertEqual(response.code, 404)

    # @patch("brainiak.handlers.log")
    # @patch("brainiak.handlers.settings", URI_PREFIX="http://tatipedia.org/")
    # def test_edit_instance_200_adding_predicate(self, log, settings):
    #     actual_new_york = self.fetch('/test/Place/new_york', method='GET')
    #     self.assertEqual(actual_new_york.code, 200)
    #     actual_new_york_dict = json.loads(actual_new_york.body)
    #     self.assertIn("rdfs:label", actual_new_york_dict)
    #     self.assertNotIn("rdfs:comment", actual_new_york_dict)
    #     # Add an attribute
    #     actual_new_york_dict["rdfs:comment"] = "Some random comment"
    #
    #     modified_new_york = self.fetch('/test/place/new_york',
    #                                    method='PUT',
    #                                    body=json.dumps(actual_new_york_dict))
    #     self.assertEqual(modified_new_york.code, 200)
    #     modified_new_york_dict = json.loads(modified_new_york.body)
    #     self.assertIn("rdfs:label", modified_new_york_dict)
    #     self.assertIn("rdfs:comment", modified_new_york_dict)


class EditInstanceResourceTestCase(QueryTestCase):

    maxDiff = None
    allow_triplestore_connection = True
    graph_uri = 'http://test.edit.instance/'
    fixtures = []

    def test_query_modify(self):
        instance_data = {"triples": '<fulano> a <criatura>; <gosta-de> <ciclano>',
                         "prefix": "",
                         "graph_uri": self.graph_uri}
        query = create_resource.QUERY_INSERT_TRIPLES % instance_data
        self.query(query)

        existing_triple = self.query("SELECT ?s ?o from <%s> { ?s <gosta-de> ?o }" % self.graph_uri)
        self.assertEqual(existing_triple["results"]["bindings"][0]["s"]["value"], "fulano")
        self.assertEqual(existing_triple["results"]["bindings"][0]["o"]["value"], "ciclano")
        params = {"instance_uri": "fulano",
                  "graph_uri": self.graph_uri,
                  "triples": "<fulano> <gosta-de> <beltrano>"}
        modify_response = self.query(edit_resource.MODIFY_QUERY % params)

        self.assertTrue(is_modify_response_successful(modify_response, n_deleted=2, n_inserted=1))
