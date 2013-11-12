from mock import patch
import json
from brainiak import server
from brainiak.instance import create_instance, edit_instance
from brainiak.utils.sparql import is_modify_response_successful
from tests.mocks import mock_schema

from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class EditInstanceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    # The class variables below are handled by QueryTestCase
    allow_triplestore_connection = True
    graph_uri = "http://somegraph.org/"
    fixtures = ["tests/sample/instances.n3"]

    JSON_NEW_YORK_ADD_CONTINENT = {
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "place": "http://tatipedia.org/Place/",
            "tpedia": "http://tatipedia.org/",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        },
        "tpedia:partOfContinent": "place:America"
    }

    def setUp(self):
        super(EditInstanceTestCase, self).setUp()
        response = self.fetch('/place/Place/InexistentCity?class_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/', method='DELETE')

    def get_app(self):
        return server.Application()

    def setUp(self):
        super(EditInstanceTestCase, self).setUp()

    def tearDown(self):
        pass

    @patch("brainiak.handlers.logger")
    def test_edit_instance_500(self, log):
        actual_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='GET')
        self.assertEqual(actual_new_york.code, 200)
        actual_new_york_dict = json.loads(actual_new_york.body)

        config = {"side_effect": NotImplementedError}
        patcher = patch("brainiak.handlers.edit_instance", ** config)
        patcher.start()

        response = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='PUT',
            body=json.dumps(actual_new_york_dict))
        self.assertEqual(response.code, 500)
        patcher.stop()

    @patch("brainiak.handlers.logger")
    def test_edit_instance_400_no_body(self, log):
        response = self.fetch('/anything/Place/new_york', method='PUT')
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.logger")
    def test_edit_instance_400_wrong_params(self, log):
        response = self.fetch('/anything/Place/new_york?wrong_param=wrong_value', method='PUT', body=json.dumps({}))
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.logger")
    @patch("brainiak.instance.create_instance.get_cached_schema",
           return_value=mock_schema({"rdfs:label": "string",
                                     "rdfs:comment": "string",
                                     "http://tatipedia.org/speak": "string"}))
    def test_edit_instance_that_doesnt_exist_201(self, mock_schema, mock_log):  # Bus notification test is in a separated test file
        response = self.fetch('/place/Place/InexistentCity?class_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
                              method='PUT',
                              body=json.dumps({"rdfs:label": "Inexistent city"}))
        self.assertEqual(response.code, 201)
        location = response.headers['Location']
        self.assertTrue(location.startswith("http://localhost:"))
        self.assertTrue(location.endswith("/place/Place/InexistentCity?class_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/"))

    @patch("brainiak.handlers.logger")
    @patch("brainiak.instance.edit_instance.get_cached_schema", return_value=mock_schema({"rdfs:label": "string", "rdfs:comment": "string", "http://tatipedia.org/speak": "string"}))
    def test_edit_instance_200_adding_predicate(self, mock_schema, mock_log):
        actual_new_york = self.fetch('/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/', method='GET')
        self.assertEqual(actual_new_york.code, 200)
        actual_new_york_dict = json.loads(actual_new_york.body)
        self.assertIn("rdfs:label", actual_new_york_dict)
        self.assertNotIn("rdfs:comment", actual_new_york_dict)
        # Add an attribute
        actual_new_york_dict["rdfs:comment"] = "Some random comment"
        modified_new_york = self.fetch('/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
                                       method='PUT',
                                       body=json.dumps(actual_new_york_dict))
        self.assertEqual(modified_new_york.code, 200)
        self.assertEqual(modified_new_york.body, "")

    @patch("brainiak.handlers.logger")
    @patch("brainiak.instance.create_instance.get_cached_schema",
           return_value=mock_schema({"rdfs:label": "string",
                                     "rdfs:comment": "string",
                                     "http://tatipedia.org/speak": "string"}))
    def test_edit_instance_with_incorrect_values_raises_400(self, mock_schema, mock_log):  # Bus notification test is in a separated test file
        response = self.fetch('/place/Place/InexistentCity?class_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
                              method='PUT',
                              body=json.dumps({"rdfs:label": 1}))
        self.assertEqual(response.code, 400)
        computed_payload = json.loads(response.body)
        expected_payload = {
            "errors": [
                "Incorrect value for property (http://www.w3.org/2000/01/rdf-schema#label). A (xsd:string) was expected, but (1) was given."
            ]
        }
        self.assertEqual(computed_payload, expected_payload)

    @patch("brainiak.handlers.logger")
    @patch("brainiak.instance.edit_instance.get_cached_schema", return_value=mock_schema({"rdfs:label": "string", "rdfs:comment": "string", "http://tatipedia.org/speak": "string"}))
    def test_edit_instance_by_instance_uri_return_200_adding_predicate(self, mock_schema, mock_log):
        actual_new_york = self.fetch('/_/_/_/?instance_uri=http://tatipedia.org/new_york', method='GET')
        self.assertEqual(actual_new_york.code, 200)
        actual_new_york_dict = json.loads(actual_new_york.body)
        self.assertIn("rdfs:label", actual_new_york_dict)
        self.assertNotIn("rdfs:comment", actual_new_york_dict)
        # Add an attribute
        actual_new_york_dict["rdfs:comment"] = "Some random comment"
        modified_new_york = self.fetch('/_/_/_/?instance_uri=http://tatipedia.org/new_york',
                                       method='PUT',
                                       body=json.dumps(actual_new_york_dict))
        self.assertEqual(modified_new_york.code, 200)
        self.assertEqual(modified_new_york.body, "")


class EditInstanceResourceTestCase(QueryTestCase):

    maxDiff = None
    allow_triplestore_connection = True
    fixtures_by_graph = {
        'http://any.graph/': ['tests/sample/instances.n3'],
        'http://empty.graph/': [],
        'http://test.edit.instance/': []
    }

    def test_query_modify(self):
        instance_data = {"triples": '<fulano> a <criatura>; <gosta-de> <ciclano>',
                         "prefix": "",
                         "graph_uri": 'http://test.edit.instance/'}
        query = create_instance.QUERY_INSERT_TRIPLES % instance_data

        self.query(query, 'http://test.edit.instance/')

        existing_triple = self.query("SELECT ?s ?o from <http://test.edit.instance/> { ?s <gosta-de> ?o }")
        self.assertEqual(existing_triple["results"]["bindings"][0]["s"]["value"], "fulano")
        self.assertEqual(existing_triple["results"]["bindings"][0]["o"]["value"], "ciclano")
        params = {"instance_uri": "fulano",
                  "graph_uri": self.graph_uri,
                  "triples": "<fulano> <gosta-de> <beltrano>",
                  "prefix": ""}
        modify_response = self.query(edit_instance.MODIFY_QUERY % params, 'http://test.edit.instance/')

        self.assertTrue(is_modify_response_successful(modify_response, n_deleted=2, n_inserted=1))

    def test_query_exists_in_graph(self):
        params = {
            "instance_uri": "http://tatipedia.org/Platypus"
        }
        query = edit_instance.QUERY_INSTANCE_EXISTS_TEMPLATE % params
        computed = self.query(query, False)["boolean"]
        expected = True
        self.assertEqual(computed, expected)

    def test_query_isntance_doesnt_exist(self):
        params = {
            "instance_uri": "http://tatipedia.org/Xubylus"
        }
        query = edit_instance.QUERY_INSTANCE_EXISTS_TEMPLATE % params
        computed = self.query(query, False)["boolean"]
        expected = False
        self.assertEqual(computed, expected)
