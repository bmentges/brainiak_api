import brainiak.schema.resource as schema

from brainiak import prefixes
from brainiak import triplestore
from brainiak.schema.resource import build_class_schema_query, \
        _query_superclasses, query_superclasses, QUERY_CARDINALITIES, \
        QUERY_PREDICATE_WITHOUT_LANG, \
        QUERY_SUPERCLASS
from brainiak.utils.params import ParamDict
from tests.mocks import MockHandler

from tests.tornado_cases import TornadoAsyncTestCase
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


class SuperClassQueryTestCase(QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/animalia.n3"]
    graph_uri = "http://schema.test/"

    def test_query_superclass(self):
        params = {"class_uri": "http://example.onto/Yorkshire_Terrier"}
        query = QUERY_SUPERCLASS % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {u'class': {u'type': u'uri', u'value': u'http://example.onto/Yorkshire_Terrier'}},
            {u'class': {u'type': u'uri', u'value': u'http://example.onto/Canidae'}},
            {u'class': {u'type': u'uri', u'value': u'http://example.onto/Mammalia'}},
            {u'class': {u'type': u'uri', u'value': u'http://example.onto/Animal'}},
            {u'class': {u'type': u'uri', u'value': u'http://example.onto/Species'}}]
        self.assertEqual(computed, expected)


class CardinalitiesQueryTestCase(QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/animalia.n3"]

    def test_query_cardinalities(self):
        params = {"class_uri": "http://example.onto/Animal"}
        query = QUERY_CARDINALITIES % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u'max': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/Gender'}
            },
            {
                u'min': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/Gender'}
            },
            # {
            #     u'enumerated_value': {u'type': u'uri', u'value': u'http://example.onto/Male'},
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # },
            # {
            #     u'enumerated_value': {u'type': u'uri', u'value': u'http://example.onto/Female'},
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # },
            # {
            #     u'enumerated_value': {u'type': u'uri', u'value': u'http://example.onto/Transgender'},
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # },
            # {
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # }
        ]
        for expected_item in expected:
            self.assertIn(expected_item, computed)

    def test_query_cardinalities_from_super_classes(self):
        params = {"class_uri": "http://example.onto/Canidae"}
        query = QUERY_CARDINALITIES % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u'max': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/Gender'}
            },
            {
                u'min': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/Gender'}
            },
            {
                u'max': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furLenght'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurLenght'}
            },
            {
                u'min': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furLenght'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurLenght'}
            },
            {
                u'min': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furColour'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurColour'}
            },
            # {
            #     u'enumerated_value': {u'type': u'uri', u'value': u'http://example.onto/Male'},
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # },
            # {
            #     u'enumerated_value': {u'type': u'uri', u'value': u'http://example.onto/Female'},
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # },
            # {
            #     u'enumerated_value': {u'type': u'uri', u'value': u'http://example.onto/Transgender'},
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # },
            # {
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # }
        ]
        for expected_item in expected:
            self.assertIn(expected_item, computed)

    def test_query_cardinalities_multiple_ranges(self):
        params = {"class_uri": "http://example.onto/SubAnimal"}
        query = QUERY_CARDINALITIES % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u'max': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/Gender'}
            },
            {
                u'min': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/Gender'}
            },
            {
                u'max': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furStyle'},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/2001/XMLSchema#string'}
            },
            {
                u'max': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'},
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furStyle'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurColour'}
            },
            {
                u'max': {
                    u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                    u'type': u'typed-literal',
                    u'value': u'1'
                },
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furStyle'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurLenght'}
            },
            # {
            #     u'enumerated_value': {u'type': u'uri', u'value': u'http://example.onto/Male'},
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # },
            # {
            #     u'enumerated_value': {u'type': u'uri', u'value': u'http://example.onto/Female'},
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # },
            # {
            #     u'enumerated_value': {u'type': u'uri', u'value': u'http://example.onto/Transgender'},
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # },
            # {
            #     u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
            #     u'range': {u'type': u'bnode', u'value': u'nodeID://b12726'}
            # }
        ]
        for expected_item in expected:
            self.assertIn(expected_item, computed)


class PredicatesQueryTestCase(QueryTestCase):

    maxDiff = None
    allow_triplestore_connection = True
    fixtures = ["tests/sample/animalia.n3"]

    def test_query_predicates(self):
        filter_ = "FILTER (?domain_class IN (<http://example.onto/Mammalia>))"
        params = {"filter_classes_clause": filter_}
        query = QUERY_PREDICATE_WITHOUT_LANG % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furColour'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://test.graph/'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurColour'},
                u'title': {u'type': u'literal', u'value': u'Fur or hair colour'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            }
        ]
        for expected_item in expected:
            self.assertIn(expected_item, computed)

    def test_query_predicate_multiple_ranges(self):
        filter_ = "FILTER (?domain_class IN (<http://example.onto/SubAnimal>))"
        params = {"filter_classes_clause": filter_}
        query = QUERY_PREDICATE_WITHOUT_LANG % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furStyle'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://test.graph/'},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/2001/XMLSchema#string'},
                u'title': {u'type': u'literal', u'value': u'Fur or hair style (could be a description, FurLenght or FurColour)'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furStyle'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://test.graph/'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurColour'},
                u'title': {u'type': u'literal', u'value': u'Fur or hair style (could be a description, FurLenght or FurColour)'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furStyle'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://test.graph/'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurLenght'},
                u'title': {u'type': u'literal', u'value': u'Fur or hair style (could be a description, FurLenght or FurColour)'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            }
        ]
        for expected_item in expected:
            self.assertIn(expected_item, computed)

# TODO: test
# QUERY_PREDICATE_WITH_LANG
# subproperties
# subclasses
# multiple ranges
# QUERY_PREDICATE_WITHOUT_LANG


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
        handler = MockHandler(uri="http://class.uri")
        query_params = ParamDict(handler, **params)

        response = schema.get_schema(query_params)
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
                {"predicate": {"type": "uri", "value": "http://test/person/gender"},
                 "range": {"type": "bnode", "value": "nodeID://b72146"}
                 },
                {"predicate": {"type": "uri", "value": "http://test/person/gender"},
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
                'graph': 'http://test/person/',
                'format': 'uri',
                'maxItems': '1',
                'minItems': '1',
                'type': 'string',
                'range': {'graph': 'http://test/person/',
                          '@id': 'http://test/person/Gender',
                          'title': u'G\xeanero da Pessoa',
                          'format': 'uri',
                          'type': 'string'
                          }
            }
        }
        self.assertEqual(response_predicates_and_cardinalities, expected_predicates_and_cardinalities)
        self.stop()
