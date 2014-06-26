import json
from mock import patch
from brainiak.instance import create_instance
from brainiak.instance.get_instance import QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE
from brainiak.schema import get_class as schema_resource
from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class CreateInstanceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None

    # the variables below have special meaning for QueryTestCase
    graph_uri = 'http://example.onto/'
    fixtures = ["tests/sample/animalia.n3"]

    def setUp(self):
        self.original_schema_resource_get_schema = schema_resource.get_schema
        super(CreateInstanceTestCase, self).setUp()

    def tearDown(self):
        schema_resource.get_schema = self.original_schema_resource_get_schema
        super(CreateInstanceTestCase, self).tearDown()

    def checkInstanceExistance(self, class_uri, instance_uri):
        query_string = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % {
            "class_uri": class_uri,
            "instance_uri": instance_uri,
            "lang": "pt",
            "ruleset": "%sruleset" % self.graph_uri,
            "object_label_variable": "",
            "object_label_optional_clause": ""
        }
        response = self.query(query_string)
        return response['results']['bindings'] != []

    def assertInstanceExist(self, class_uri, instance_uri):
        return self.checkInstanceExistance(class_uri, instance_uri)

    def assertInstanceDoesNotExist(self, class_uri, instance_uri):
        return not self.checkInstanceExistance(class_uri, instance_uri)

    @patch("brainiak.handlers.logger")
    def test_create_instance_500_internal_error(self, log):
        def raise_exception():
            raise Exception()
        schema_resource.get_schema = lambda params: raise_exception()
        response = self.fetch('/person/Person/',
                              method='POST',
                              body=json.dumps({}))
        self.assertEqual(response.code, 500)
        body = json.loads(response.body)
        self.assertIn("HTTP error: 500\nException:\n", body["errors"][0])

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.handlers.logger")
    def test_create_instance_400_invalid_json(self, log, settings):
        response = self.fetch('/place/City/',
                              method='POST',
                              body="invalid input")
        self.assertEqual(response.code, 400)
        body = json.loads(response.body)
        self.assertEquals(body["errors"], ['HTTP error: 400\nNo JSON object could be decoded'])

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.handlers.logger")
    def test_create_instance_404_inexistant_class(self, log, settings):
        payload = {}
        response = self.fetch('/xubiru/X/',
                              method='POST',
                              body=json.dumps(payload))
        self.assertEqual(response.code, 404)
        body = json.loads(response.body)
        self.assertEqual(body["errors"], [u"HTTP error: 404\nClass xubiru/X doesn't exist in context xubiru."])

    @patch("brainiak.handlers.logger")
    @patch("brainiak.handlers.notify_bus")
    @patch("brainiak.handlers.schema_resource.get_schema", return_value=True)
    @patch("brainiak.instance.create_instance.create_instance_uri", return_value="http://example.onto/City/123")
    @patch("brainiak.instance.get_instance.settings", DEFAULT_RULESET_URI="{0}ruleset".format(graph_uri))
    @patch("brainiak.instance.get_instance.triplestore")
    @patch("brainiak.handlers.settings", NOTIFY_BUS=True)
    @patch("brainiak.instance.get_instance.get_class.get_cached_schema",
           return_value={
               "properties": {
                   "http://www.w3.org/2000/01/rdf-schema#label": {"type": "string"},
                   "http://example.onto/name": {"type": "string", "datatype": "http://www.w3.org/2001/XMLSchema#string"}
               },
               "id": "http://example.onto/City"
           })
    @patch("brainiak.instance.create_instance.get_cached_schema",
           return_value={
               "properties": {
                   "http://www.w3.org/2000/01/rdf-schema#label": {"type": "string"},
                   "http://example.onto/name": {"type": "string", "datatype": "http://www.w3.org/2001/XMLSchema#string"}
               },
               "id": "http://example.onto/City"
           })
    def test_create_instance_with_invalid_values_return_400(
            self, mock_get_schema, mock_get_instance_schema,
            mocked_handler_settings, mockeed_triplestore, mocked_settings,
            mocked_create_instance_uri, mocked_get_schema, mocked_notify_bus, mocked_logger):
        mockeed_triplestore.query_sparql = self.query
        payload = {
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "place": "http://example.onto/place/",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "ex": "http://example.onto/"
            },
            "ex:name": 1,
        }
        response = self.fetch('/example/City?graph_uri=http://example.onto/&class_prefix=http://example.onto/',
                              method='POST',
                              body=json.dumps(payload))
        self.assertEqual(response.code, 400)

    @patch("brainiak.instance.create_instance.are_there_label_properties_in", return_value=False)
    def test_return_400_without_rdfs_label(self, mock_are_there_label_properties_in):
        payload = {
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "place": "http://example.onto/place/",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "ex": "http://example.onto/"
            },
            "ex:sssssss": "isNotSubPropertyOfLabel",
        }

        response = self.fetch('/example/City?graph_uri=http://example.onto/&class_prefix=http://example.onto/',
                              method='POST',
                              body=json.dumps(payload))
        self.assertEqual(response.code, 400)
        expected_msg_substring = "Label properties like rdfs:label or its subproperties are required"
        self.assertIn(expected_msg_substring, json.loads(response.body)["errors"][0])


class CreateInstanceTestCaseWithoutMocks(TornadoAsyncHTTPTestCase, QueryTestCase):
    fixtures_by_graph = {"http://on.to/": ["tests/sample/people.ttl"]}

    def test_put_suceeds(self):
        info = {
            "instance": "http://on.to/rubensAzambuja",
            "class": "http://on.to/Person",
            "graph": "http://on.to/",
            "meta": "0"
        }
        url = '/_/_/_/?graph_uri={graph}&class_uri={class}&instance_uri={instance}&lang=en'
        url = url.format(**info)

        data = {
            u'http://on.to/weight': 88.5,
            u'http://on.to/isHuman': True,
            u'http://on.to/name': u'Rubens Azambuja',
            u'http://on.to/age': 40
        }

        response = self.fetch(url, method='PUT', body=json.dumps(data))
        self.assertEqual(response.code, 201)
        self.assertEqual(response.body, "")
        computed_location = response.headers['Location']
        expected_location = '/_/_/_/?graph_uri=http://on.to/&class_uri=http://on.to/Person&instance_uri=http://on.to/rubensAzambuja&lang=en'
        self.assertTrue(expected_location in computed_location)

    def test_put_suceeds_with_rdfs_type(self):
        info = {
            "instance": "http://on.to/rubensAzambuja",
            "class": "http://on.to/Person",
            "graph": "http://on.to/",
            "meta": "0"
        }
        url = '/_/_/_/?graph_uri={graph}&class_uri={class}&instance_uri={instance}&lang=en'
        url = url.format(**info)

        data = {
            u'http://on.to/weight': 88.5,
            u'http://on.to/isHuman': True,
            u'http://on.to/name': u'Rubens Azambuja',
            u'http://on.to/age': 40,
            u'rdfs:type': "http://on.to/Person"
        }

        response = self.fetch(url, method='PUT', body=json.dumps(data))
        self.assertEqual(response.code, 201)
        self.assertEqual(response.body, "")
        computed_location = response.headers['Location']
        expected_location = '/_/_/_/?graph_uri=http://on.to/&class_uri=http://on.to/Person&instance_uri=http://on.to/rubensAzambuja&lang=en'
        self.assertTrue(expected_location in computed_location)

    def test_put_fails_with_incompatible_rdfs_type(self):
        info = {
            "instance": "http://on.to/rubensAzambuja",
            "class": "http://on.to/Person",
            "graph": "http://on.to/",
            "meta": "0"
        }
        url = '/_/_/_/?graph_uri={graph}&class_uri={class}&instance_uri={instance}&lang=en'
        url = url.format(**info)

        data = {
            u'http://on.to/weight': 88.5,
            u'http://on.to/isHuman': True,
            u'http://on.to/name': u'Rubens Azambuja',
            u'http://on.to/age': 40,
            u'rdfs:type': "http://on.to/Manager"
        }

        response = self.fetch(url, method='PUT', body=json.dumps(data))
        self.assertEqual(response.code, 400)
        computed = json.loads(response.body)
        expected = {"errors": ["HTTP error: 400\nIncompatible values for rdfs:type <http://on.to/Manager> and class URI <http://on.to/Person>"]}
        self.assertEqual(computed, expected)
