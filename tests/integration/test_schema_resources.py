import brainiak.schema.resource as schema

from brainiak import prefixes
from brainiak import triplestore
from brainiak.schema.resource import build_class_schema_query, \
        _query_superclasses, query_superclasses

from tests import TornadoAsyncTestCase
from tests.sparql import QueryTestCase


class ClassSchemaQueryTestCase(QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/schemas.n3"]

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        triplestore.query_sparql = lambda query: self.query(query)

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    def test_query_superclasses(self):
        params = {"class_uri": "http://example.onto/City"}

        expected_bindings = [{u'class': {u'type': u'uri', u'value': u'http://example.onto/City'}},
                             {u'class': {u'type': u'uri', u'value': u'http://example.onto/Place'}}]

        response = _query_superclasses(params)
        self.assertEqual(response["results"]["bindings"], expected_bindings)

    def test_query_superclasses_result(self):
        params = {"class_uri": "http://example.onto/City"}

        expected_list = [u'http://example.onto/City',
                             u'http://example.onto/Place']

        response = query_superclasses(params)
        self.assertEqual(response, expected_list)

    def test_schema_with_label_and_comment_in_pt(self):
        params = {"class_uri": "http://example.onto/Place",
                  "graph_uri": self.graph_uri,
                  "lang": "pt"}

        query = build_class_schema_query(params)

        response_bindings = self.query(query)['results']['bindings']
        expected_bindings = [{u'comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Procure no dicionario.'},
                              u'title': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Lugar'}}]

        self.assertEqual(response_bindings, expected_bindings)

    def test_schema_with_label_and_comment_in_en(self):
        params = {"class_uri": "http://example.onto/Place",
                  "graph_uri": self.graph_uri,
                  "lang": "en"}

        query = build_class_schema_query(params)

        response_bindings = self.query(query)['results']['bindings']
        expected_bindings = [{u'comment': {u'xml:lang': u'en', u'type': u'literal', u'value': u'Search in the dictionary.'},
                              u'title': {u'xml:lang': u'en', u'type': u'literal', u'value': u'Place'}}]

        self.assertEqual(response_bindings, expected_bindings)

    def test_schema_with_label_and_comment_without_lang(self):
        params = {"class_uri": "http://example.onto/PlaceWithoutLanguage",
                  "graph_uri": self.graph_uri,
                  "lang": False}

        query = build_class_schema_query(params)

        response_bindings = self.query(query)['results']['bindings']
        expected_bindings = [{u'comment': {u'type': u'literal', u'value': u'Search in the dictionary.'},
                              u'title': {u'type': u'literal', u'value': u'Place'}}]

        self.assertEqual(response_bindings, expected_bindings)

    def test_schema_with_label_and_without_comment(self):
        params = {"class_uri": "http://example.onto/Lugar",
                  "graph_uri": self.graph_uri,
                  "lang": False}

        query = build_class_schema_query(params)

        response_bindings = self.query(query)['results']['bindings']
        expected_bindings = [{u'title': {u'type': u'literal', u'value': u'Lugar'}}]

        self.assertEqual(response_bindings, expected_bindings)


class GetSchemaTestCase(TornadoAsyncTestCase):

    def setUp(self):
        super(TornadoAsyncTestCase, self).setUp()
        self.original_query_class_schema = schema.query_class_schema
        self.original_get_predicates_and_cardinalities = schema.get_predicates_and_cardinalities
        self.original_query_superclasses = schema.query_superclasses

    def tearDown(self):
        schema.query_class_schema = self.original_query_class_schema
        schema.get_predicates_and_cardinalities = self.original_get_predicates_and_cardinalities
        schema.query_superclasses = self.original_query_superclasses
        super(TornadoAsyncTestCase, self).tearDown()

    def test_query_get_schema(self):
        class_schema = {"results": {"bindings": [{"dummy_key": "dummy_value"}]}}

        schema.query_class_schema = lambda query: class_schema
        schema.query_superclasses = lambda query: ["classeA", "classeB"]

        def mock_get_predicates_and_cardinalities(context, params):
            return "property_dict"

        schema.get_predicates_and_cardinalities = mock_get_predicates_and_cardinalities

        params = {
            "context_name": "ctx",
            "class_name": "klass",
            "class_uri": "test_class",
            "graph_uri": "test_graph",
            "lang": "en"
        }

        response = schema.get_schema(params)
        schema_response = response

        self.assertIn("title", schema_response)
        self.assertIn("type", schema_response)
        self.assertIn("@id", schema_response)
        self.assertIn("properties", schema_response)

        self.assertEqual(schema_response["properties"], "property_dict")
        # FIXME: enhance the structure of the response
        self.stop()


class GetPredicatesCardinalitiesTestCase(TornadoAsyncTestCase):
    maxDiff = None

    def setUp(self):
        super(TornadoAsyncTestCase, self).setUp()
        self.original_query_cardinalities = schema.query_cardinalities
        self.original_query_predicates = schema.query_predicates
        self.original_extract_cardinalities = schema._extract_cardinalities

    def tearDown(self):
        schema.query_cardinalities = self.original_query_cardinalities
        schema.query_predicates = self.original_query_predicates
        schema._extract_cardinalities = self.original_extract_cardinalities
        super(TornadoAsyncTestCase, self).tearDown()

    def test_get_predicates_and_cardinalities(self):

        # Mocks
        fake_response_predicates = {"results": {"bindings": [
            {"predicate": {"type": "uri", "value": "http://test/person/root_gender"},
             "predicate_graph": {"type": "uri", "value": "http://test/person/"},
             "type": {"type": "uri", "value": "http://www.w3.org/2002/07/owl#ObjectProperty"},
             "range": {"type": "uri", "value": "http://test/person/Gender"},
             "title": {"type": "literal", "xml:lang": "pt", "value": "Root (to be removed from answer)"},
             "range_graph": {"type": "uri", "value": "http://test/person/"}},
            {"predicate": {"type": "uri", "value": "http://test/person/gender"},
                "super_property": {"type": "uri", "value": "http://test/person/root_gender"},
                "predicate_graph": {"type": "uri", "value": "http://test/person/"},
                "predicate_comment": {"type": "literal", "xml:lang": "pt", "value": u"G\u00EAnero."},
                "type": {"type": "uri", "value": "http://www.w3.org/2002/07/owl#ObjectProperty"},
                "range": {"type": "uri", "value": "http://test/person/Gender"},
                "title": {"type": "literal", "xml:lang": "pt", "value": "Sexo"},
                "range_graph": {"type": "uri", "value": "http://test/person/"},
                "range_label": {"type": "literal", "xml:lang": "pt", "value": u"G\u00EAnero da Pessoa"}}]}}

        fake_response_cardinalities = {"results": {
            "bindings": [
                {"max": {"datatype": "http://www.w3.org/2001/XMLSchema#integer", "type": "typed-literal", "value": "1"},
                 "predicate": {"type": "uri", "value": "http://test/person/gender"},
                 "range": {"type": "uri", "value": "http://test/person/Gender"}
                 },
                {"min": {"datatype": "http://www.w3.org/2001/XMLSchema#integer", "type": "typed-literal", "value": "1"},
                 "predicate": {"type": "uri", "value": "http://test/person/gender"},
                 "range": {"type": "uri", "value": "http://test/person/Gender"}
                 },
                {"enumerated_value": {"type": "uri", "value": "http://test/person/Gender/Male"},
                 "enumerated_value_label": {"type": "literal", "value": "Masculino", "xml:lang": "pt"},
                 "predicate": {"type": "uri", "value": "http://test/person/gender"},
                 "range": {"type": "bnode", "value": "nodeID://b72146"}
                 },
                {"enumerated_value": {"type": "uri", "value": "http://test/person/Gender/Female"},
                 "enumerated_value_label": {"type": "literal", "value": "Feminino", "xml:lang": "pt"},
                 "predicate": {"type": "uri", "value": "http://test/person/gender"},
                 "range": {"type": "bnode", "value": "nodeID://b72146"}
                 }
            ]}
        }

        schema.query_cardinalities = lambda query: fake_response_cardinalities
        schema.query_predicates = lambda query: fake_response_predicates

        context = prefixes.MemorizeContext()
        params = {"class_uri": "http://test/person/gender",
                  "class_schema": None}

        response_predicates_and_cardinalities = schema.get_predicates_and_cardinalities(context, params)
        expected_predicates_and_cardinalities = {
            'http://test/person/gender': {
                'comment': u'G\xeanero.',
                'title': 'Sexo',
                'enum': ['http://test/person/Gender/Male', 'http://test/person/Gender/Female'],
                'graph': 'http://test/person/',
                'format': 'uri',
                'maxItems': '1',
                'minItems': '1',
                'type': 'string',
                'range': {'graph': 'http://test/person/',
                          '@id': 'http://test/person/Gender',
                          'title': u'G\xeanero da Pessoa'
                          }
            }
        }
        self.assertEqual(response_predicates_and_cardinalities, expected_predicates_and_cardinalities)
        self.stop()
