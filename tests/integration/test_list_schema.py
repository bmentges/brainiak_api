# -*- coding: utf-8 -*-

from mock import patch
import json
from brainiak.prefixes import SHORTEN

import brainiak.schema.get_class as schema

from brainiak import prefixes
from brainiak import triplestore
from brainiak.schema.get_class import build_class_schema_query, \
    _query_superclasses, query_superclasses, QUERY_CARDINALITIES, \
    QUERY_PREDICATE_WITHOUT_LANG, QUERY_PREDICATE_WITH_LANG, \
    QUERY_SUPERCLASS
from brainiak.utils.params import ParamDict

from tests.mocks import MockHandler, Params
from tests.tornado_cases import TornadoAsyncTestCase, TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class ClassSchemaQueryTestCase(QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/schemas.n3"]

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        triplestore.query_sparql = lambda query, params: self.query(query)

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    def test_query_superclasses(self):
        params = Params({"class_uri": "http://example.onto/City"})

        expected_bindings = [{u'class': {u'type': u'uri', u'value': u'http://example.onto/City'}},
                             {u'class': {u'type': u'uri', u'value': u'http://example.onto/Place'}}]

        response = _query_superclasses(params)
        self.assertEqual(response["results"]["bindings"], expected_bindings)

    def test_query_superclasses_result(self):
        params = Params({"class_uri": "http://example.onto/City"})

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
    graph_uri = "http://example.onto/"

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
    graph_uri = "http://example.onto/"

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
            }
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
        ]
        for expected_item in expected:
            self.assertIn(expected_item, computed)


class PredicatesQueryTestCase(QueryTestCase):

    maxDiff = None
    allow_triplestore_connection = True
    fixtures = ["tests/sample/animalia.n3"]
    graph_uri = "http://example.onto/"

    def test_query_predicate_multiple_classes(self):
        filter_ = "FILTER (?domain_class IN (<http://example.onto/Mammalia>, <http://example.onto/Canidae>))"
        params = {"filter_classes_clause": filter_}
        query = QUERY_PREDICATE_WITHOUT_LANG % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furLenght'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://example.onto/'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurLenght'},
                u'title': {u'type': u'literal', u'value': u'Fur or hair lenght'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/furColour'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://example.onto/'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/FurColour'},
                u'title': {u'type': u'literal', u'value': u'Fur or hair colour'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            }
        ]
        self.assertEqual(sorted(expected), sorted(computed))

    def test_query_predicate_subproperty(self):
        filter_ = "FILTER (?domain_class IN (<http://example.onto/Yorkshire_Terrier>))"
        params = {"filter_classes_clause": filter_}
        query = QUERY_PREDICATE_WITHOUT_LANG % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/birthCity'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://example.onto/'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/City'},
                u'range_graph': {u'type': u'uri', u'value': u'http://example.onto/'},
                u'range_label': {u'type': u'literal', u'value': u'City'},
                u'super_property': {u'type': u'uri', u'value': u'http://example.onto/birthPlace'},
                u'title': {u'type': u'literal', u'value': u'Birth city of first known member of Species'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            }
        ]
        self.assertEqual(sorted(expected), sorted(computed))

    def test_query_predicate_with_lang_and_comment(self):
        filter_ = "FILTER (?domain_class IN (<http://example.onto/Bird>, <http://example.onto/Animal>))"
        params = {"filter_classes_clause": filter_, "lang": "en"}
        query = QUERY_PREDICATE_WITH_LANG % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/canFlight'},
                u'predicate_comment': {u'type': u'literal', u'value': u'Defines if the bird species can flight or not.', u'xml:lang': u'en'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://example.onto/'},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/2001/XMLSchema#string'},
                u'title': {u'type': u'literal', u'value': u'Can flight', u'xml:lang': u'en'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/birthPlace'},
                u'range_label': {u'type': u'literal', u'value': u'Place'},
                u'range_graph': {u'type': u'uri', u'value': u'http://example.onto/'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://example.onto/'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/Place'},
                u'title': {u'type': u'literal', u'value': u'Birth place of first known member of Species'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://example.onto/gender'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://example.onto/'},
                u'range': {u'type': u'uri', u'value': u'http://example.onto/Gender'},
                u'title': {u'type': u'literal', u'value': u'Gender'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            }
        ]
        self.assertEqual(sorted(expected), sorted(computed))


class PredicatesQueryTestCaseMultipleDomainRange(QueryTestCase):

    maxDiff = None
    allow_triplestore_connection = True
    fixtures = ["tests/sample/place_and_university.n3"]
    graph_uri = "http://example.onto/"

    def test_query_predicate_multiple_ranges(self):
        filter_ = "FILTER (?domain_class IN (<http://example.onto/ResearchGroup>))"
        params = {"filter_classes_clause": filter_}
        query = QUERY_PREDICATE_WITHOUT_LANG % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u"predicate": {u"type": u"uri", u"value": u"http://example.onto/isBasedIn"},
                u"predicate_graph": {u"type": u"uri", u"value": u"http://example.onto/"},
                u"type": {u"type": u"uri", u"value": u"http://www.w3.org/2002/07/owl#ObjectProperty"},
                u"range": {u"type": u"uri", u"value": u"http://example.onto/University"},
                u"title": {u"type": u"literal", u"value": u"is based in"},
                u"range_graph": {u"type": u"uri", u"value": u"http://example.onto/"},
                u"range_label": {u"type": u"literal", u"value": u"University"}
            },
            {
                u"predicate": {u"type": u"uri", u"value": u"http://example.onto/isBasedIn"},
                u"predicate_graph": {u"type": u"uri", u"value": u"http://example.onto/"},
                u"type": {u"type": u"uri", u"value": u"http://www.w3.org/2002/07/owl#ObjectProperty"},
                u"range": {u"type": u"uri", u"value": u"http://example.onto/Institute"},
                u"title": {u"type": u"literal", u"value": u"is based in"},
                u"range_graph": {u"type": u"uri", u"value": u"http://example.onto/"},
                u"range_label": {u"type": u"literal", u"value": u"Institute"}
            }
        ]
        self.assertEqual(sorted(expected), sorted(computed))

    def test_query_predicate_multiple_domains(self):
        filter_ = "FILTER (?domain_class IN (<http://example.onto/City>))"
        params = {"filter_classes_clause": filter_}
        query = QUERY_PREDICATE_WITHOUT_LANG % params
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u"predicate": {u"type": u"uri", u"value": u"http://example.onto/partOfCountry"},
                u"predicate_graph": {u"type": u"uri", u"value": u"http://example.onto/"},
                u"type": {u"type": u"uri", u"value": u"http://www.w3.org/2002/07/owl#ObjectProperty"},
                u"range": {u"type": u"uri", u"value": u"http://example.onto/Country"},
                u"title": {u"type": u"literal", u"value": u"Faz parte do país"},
                u"range_graph": {u"type": u"uri", u"value": u"http://example.onto/"},
                u"range_label": {u"type": u"literal", u"value": u"País"},
                u'predicate_comment': {u'type': u'literal', u'value': u'Estado est\xe1 no pa\xeds.'},
            }
        ]
        self.assertEqual(sorted(expected), sorted(computed))


class GetSchemaTestCase(TornadoAsyncTestCase):

    @patch("brainiak.schema.get_class.query_class_schema", return_value={"results": {"bindings": [{"dummy_key": "dummy_value"}]}})
    @patch("brainiak.schema.get_class.query_superclasses", return_value=["classeA", "classeB"])
    @patch("brainiak.schema.get_class.get_predicates_and_cardinalities", return_value="property_dict")
    def test_query_get_schema(self, mocked_get_preds_and_cards, mocked_query_superclasses, mocked_query_class_schema):

        params = {
            "context_name": "ctx",
            "class_name": "klass",
            "class_uri": "test_class",
            "graph_uri": "test_graph",
            "expand_uri": prefixes.SHORTEN,
            "lang": "en"
        }
        handler = MockHandler(uri="http://class.uri")
        query_params = ParamDict(handler, **params)

        response = schema.get_schema(query_params)
        schema_response = response

        self.assertIn("title", schema_response)
        self.assertIn("type", schema_response)
        self.assertIn("id", schema_response)
        self.assertIn("properties", schema_response)

        self.assertEqual(schema_response["properties"], "property_dict")
        # FIXME: enhance the structure of the response
        self.stop()

    @patch("brainiak.schema.get_class.query_class_schema", return_value={"results": {"bindings": []}})
    @patch("brainiak.schema.get_class.query_superclasses", return_value=["classeA", "classeB"])
    @patch("brainiak.schema.get_class.get_predicates_and_cardinalities", return_value="property_dict")
    def test_query_get_schema_empty_response(self, mocked_get_preds_and_cards, mocked_query_superclasses, mocked_query_class_schema):

        params = {
            "context_name": "ctx",
            "class_name": "klass",
            "class_uri": "test_class",
            "graph_uri": "test_graph",
            "expand_uri": prefixes.SHORTEN,
            "lang": "en"
        }
        handler = MockHandler(uri="http://class.uri")
        query_params = ParamDict(handler, **params)

        response = schema.get_schema(query_params)
        self.assertIsNone(response)


class GetCardinalitiesFullTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):
    maxDiff = None
    allow_triplestore_connection = True
    fixtures = ["tests/sample/animalia.n3"]
    graph_uri = "http://example.onto/"

    def test_schema_json(self):
        response = self.fetch('/any/Human/_schema?graph_uri=http://example.onto/&class_prefix=http://example.onto/', method='GET')

        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['title'], 'Humano')
        self.assertEqual(body['type'], 'object')
        self.assertEqual(body['@context'], {u'@language': u'pt'})
        self.assertEqual(body['$schema'], 'http://json-schema.org/draft-04/schema#')
        properties = body['properties']
        expected_properties = {
            u'http://example.onto/birthPlace': {
                u'graph': u'http://example.onto/',
                u'range': {
                    u'@id': u'http://example.onto/Place',
                    u'format': u'uri',
                    u'graph': u'http://example.onto/',
                    u'title': u'Place',
                    u'type': u'string'
                },
                u'title': u'Birth place of first known member of Species',
                u'type': u'array',
                u'items': {u'type': 'string', u'format': 'uri'}
            },
            u'http://example.onto/hasChild': {
                u'graph': u'http://example.onto/',
                u'range': {
                    u'@id': u'http://example.onto/Human',
                    u'format': u'uri',
                    u'graph': u'http://example.onto/',
                    u'title': u'Humano',
                    u'type': u'string'
                },
                u'maxItems': 888,
                u'title': u"Has child (son or daughter)",
                u'type': u'array',
                u'items': {u'type': 'string', u'format': 'uri'}
            },
            u'http://example.onto/furColour': {
                u'graph': u'http://example.onto/',
                u'minItems': 1,
                u'range': {
                    u'@id': u'http://example.onto/FurColour',
                    u'format': u'uri',
                    u'graph': u'',
                    u'title': u'',
                    u'type': u'string'
                },
                u'required': True,
                u'title': u'Fur or hair colour',
                u'type': u'array',
                u'items': {u'type': 'string', u'format': 'uri'}

            },
            u'http://example.onto/gender': {
                u'format': u'uri',
                u'graph': u'http://example.onto/',
                u'range': {u'@id': u'http://example.onto/Gender',
                           u'format': u'uri',
                           u'graph': u'',
                           u'title': u'',
                           u'type': u'string'},
                u'required': True,
                u'title': u'Gender',
                u'type': u'string'
            },
            u'http://example.onto/hasParent': {
                u'graph': u'http://example.onto/',
                u'maxItems': 2,
                u'minItems': 2,
                u'range': {u'@id': u'http://example.onto/Human',
                          u'format': u'uri',
                          u'graph': u'http://example.onto/',
                          u'title': u'Humano',
                          u'type': u'string'},
                u'required': True,
                u'title': u'Has parent (mother or father)',
                u'type': u'array',
                u'items': {u'type': 'string', u'format': 'uri'}

            }

        }
        self.assertEqual(properties, expected_properties)


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
            {
                "predicate": {"type": "uri", "value": "http://test/person/root_gender"},
                "predicate_graph": {"type": "uri", "value": "http://test/person/"},
                "type": {"type": "uri", "value": "http://www.w3.org/2002/07/owl#ObjectProperty"},
                "range": {"type": "uri", "value": "http://test/person/Gender"},
                "title": {"type": "literal", "xml:lang": "pt", "value": "Root (to be removed from answer)"},
                "range_graph": {"type": "uri", "value": "http://test/person/"}
            },
            {
                "predicate": {"type": "uri", "value": "http://test/person/gender"},
                "super_property": {"type": "uri", "value": "http://test/person/root_gender"},
                "predicate_graph": {"type": "uri", "value": "http://test/person/"},
                "predicate_comment": {"type": "literal", "xml:lang": "pt", "value": u"G\u00EAnero."},
                "type": {"type": "uri", "value": "http://www.w3.org/2002/07/owl#ObjectProperty"},
                "range": {"type": "uri", "value": "http://test/person/Gender"},
                "title": {"type": "literal", "xml:lang": "pt", "value": "Sexo"},
                "range_label": {"type": "literal", "xml:lang": "pt", "value": u"G\u00EAnero da Pessoa"},
                "range_graph": {"type": "uri", "value": "http://test/person/"}
            }
        ]}}

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

        context = prefixes.MemorizeContext(normalize_keys=SHORTEN, normalize_values=SHORTEN)
        params = {"class_uri": "http://test/person/gender",
                  "class_schema": None}

        response_predicates_and_cardinalities = schema.get_predicates_and_cardinalities(context, params)
        expected_predicates_and_cardinalities = {
            'http://test/person/gender': {
                'description': u'G\xeanero.',
                'title': 'Sexo',
                'graph': 'http://test/person/',
                'format': 'uri',
                'required': True,
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
