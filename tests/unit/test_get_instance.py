# -*- coding: utf-8 -*-
import unittest

from mock import patch

from brainiak import settings, triplestore
from brainiak.instance import get_instance
from brainiak.prefixes import SHORTEN
from brainiak.utils.params import ParamDict
from tests.mocks import MockRequest, MockHandler, mock_schema
from tests.sparql import strip


class TestCaseInstanceResource(unittest.TestCase):

    def setUp(self):
        self.original_query_all_properties_and_objects = get_instance.query_all_properties_and_objects
        self.original_assemble_instance_json = get_instance.assemble_instance_json
        self.original_query_sparql = triplestore.query_sparql

    def tearDown(self):
        get_instance.query_all_properties_and_objects = self.original_query_all_properties_and_objects
        get_instance.assemble_instance_json = self.original_assemble_instance_json
        triplestore.query_sparql = self.original_query_sparql

    @patch("brainiak.instance.get_instance.query_all_properties_and_objects", return_value={"results": {"bindings": ["not_empty"]}})
    @patch("brainiak.instance.get_instance.assemble_instance_json", return_value="ok")
    @patch("brainiak.schema.get_class.get_cached_schema", return_value={})
    def test_get_instance_with_result(self, get_cached_schema, assemble_instance_json, query_all_properties_and_objects):
        query_params = {'request': MockRequest(instance="instance"),
                        'class_name': 'Country',
                        'class_uri': 'http://www.onto.sample/place/Country',
                        'context_name': 'place',
                        'expand_uri': '0',
                        'graph_uri': 'http://www.onto.sample/place',
                        'instance_id': 'Brazil',
                        'instance_uri': settings.URI_PREFIX + 'place/Country/Brazil',
                        'lang': 'pt'}

        response = get_instance.get_instance(query_params)

        self.assertEqual(response, "ok")
        self.assertTrue(assemble_instance_json.called)
        self.assertTrue(get_cached_schema.called)
        self.assertTrue(query_all_properties_and_objects.called)

    @patch("brainiak.instance.get_instance.query_all_properties_and_objects", return_value={"results": {"bindings": []}})
    @patch("brainiak.instance.get_instance.assemble_instance_json", return_value="ok")
    @patch("brainiak.schema.get_class.get_cached_schema", return_value={})
    def test_get_instance_without_result(self, get_cached_schema, assemble_instance_json, query_all_properties_and_objects):
        query_params = {'request': MockRequest(instance="instance"),
                        'class_name': 'Country',
                        'class_uri': 'http://www.onto.sample/place/Country',
                        'context_name': 'place',
                        'expand_uri': '0',
                        'graph_uri': 'http://www.onto.sample/place',
                        'instance_id': 'Brazil',
                        'instance_uri': settings.URI_PREFIX + 'place/Country/Brazil',
                        'lang': 'pt'}

        response = get_instance.get_instance(query_params)

        self.assertEqual(response, None)
        self.assertFalse(assemble_instance_json.called)
        self.assertFalse(get_cached_schema.called)
        self.assertTrue(query_all_properties_and_objects.called)

    def test_query_all_properties_and_objects_with_expand_object_properties(self):
        triplestore.query_sparql = lambda query, query_params: query

        class Params(dict):
            triplestore_config = {}

        params = Params({})
        params.update({
            "instance_uri": "instance_uri",
            "class_uri": "class_uri",
            "lang": "en",
            "expand_object_properties": "1"
        })

        computed = get_instance.query_all_properties_and_objects(params)
        expected = """
            DEFINE input:inference <http://semantica.globo.com/ruleset>
            SELECT DISTINCT ?predicate ?object ?object_label ?super_property isBlank(?object) as ?is_object_blank {
                <instance_uri> a <class_uri> ;
                    ?predicate ?object .
            OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
            OPTIONAL { ?object rdfs:label ?object_label } .
            FILTER((langMatches(lang(?object), "en") OR langMatches(lang(?object), "")) OR (IsURI(?object)) AND !isBlank(?object)) .
            }
            """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_all_properties_and_objects_without_expand_object_properties(self):
        triplestore.query_sparql = lambda query, query_params: query

        class Params(dict):
            triplestore_config = {}

        params = Params({})
        params.update({
            "instance_uri": "instance_uri",
            "class_uri": "class_uri",
            "lang": "en",
            "expand_object_properties": "0"
        })

        computed = get_instance.query_all_properties_and_objects(params)
        expected = """
            DEFINE input:inference <http://semantica.globo.com/ruleset>
            SELECT DISTINCT ?predicate ?object  ?super_property isBlank(?object) as ?is_object_blank {
                <instance_uri> a <class_uri> ;
                    ?predicate ?object .
            OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .

            FILTER((langMatches(lang(?object), "en") OR langMatches(lang(?object), "")) OR (IsURI(?object)) AND !isBlank(?object)) .
            }
            """
        self.assertEqual(strip(computed), strip(expected))


class AssembleTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.original_build_items = get_instance.build_items_dict
        get_instance.build_items_dict = lambda bindings, class_uri, expand_direct_properties, class_schema: {}

    def tearDown(self):
        get_instance.build_items_dict = self.original_build_items

    def prepare_params(self, instance_uri="http://mock.test.com/schema/klass/instance", meta_properties=None):
        param_dict = {
            'context_name': 'schema',
            'class_name': 'klass',
            'instance_prefix': 'http://schema.org/klass/',
            'instance_id': 'instance',
            'expand_uri': SHORTEN
        }
        if meta_properties:
            param_dict.update({'meta_properties': meta_properties})
        handler = MockHandler(uri=instance_uri, **param_dict)
        self.query_params = ParamDict(handler, **param_dict)
        self.class_schema = {"title": "class label"}
        self.query_result_dict = {'results': {'bindings': []}}

    def assertResults(self, computed):
        self.assertEqual(computed["@id"], "http://schema.org/klass/instance")
        self.assertEqual(computed["@type"], "http://schema.org/klass")

    def test_assemble_instance_json_links(self):
        self.prepare_params()
        computed = get_instance.assemble_instance_json(self.query_params, self.query_result_dict, self.class_schema)
        self.assertResults(computed)

    def test_assemble_instance_json_links_with_context(self):
        self.prepare_params()
        computed = get_instance.assemble_instance_json(self.query_params, self.query_result_dict, self.class_schema)
        self.assertResults(computed)

    def test_assemble_instance_json_links_with_context_expanding_uri(self):
        self.prepare_params(instance_uri="http://mock.test.com/schema/klass/instance")
        computed = get_instance.assemble_instance_json(self.query_params, self.query_result_dict, self.class_schema)
        self.assertEqual(computed["@type"], "http://schema.org/klass")

    def test_assemble_instance_json_with_no_meta_properties(self):
        self.prepare_params(meta_properties="0")
        computed = get_instance.assemble_instance_json(self.query_params, self.query_result_dict, self.class_schema)
        expected = {}  # because build_items is empty
        self.assertEqual(computed, expected)


class BuildItemsDictTestCase(unittest.TestCase):

    maxDiff = None

    def test_build_items_dict(self):
        bindings = [
            {"predicate": {"value": "key1"}, "object": {"value": 1}, "label": {"value": "label1"}},
            {"predicate": {"value": "key1"}, "object": {"value": 2}, "label": {"value": "label1"}},
            {"predicate": {"value": "key2"}, "object": {"value": "value2"}, "label": {"value": "label1"}}
        ]
        class_schema = {
            "properties": {
                "key1": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "datatype": u'http://www.w3.org/2001/XMLSchema#integer'
                },
                "key2": {
                    "type": "string",
                    "datatype": u'http://www.w3.org/2001/XMLSchema#string'
                },
                "rdf:type": {
                    "type": "string",
                    "datatype": u'http://www.w3.org/2001/XMLSchema#string'
                }
            }
        }
        expected = {
            "key1": [1, 2],
            "key2": "value2",
            u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': "some:Class"}
        response = get_instance.build_items_dict(bindings, "some:Class", True, class_schema)
        self.assertEqual(response, expected)

    def test_build_items_dict_with_blank_nodes(self):
        bindings = [
            {"predicate": {"value": "key1"}, "object": {"value": 1}, "label": {"value": "label1"}, "is_object_blank": {"value": "1"}},
            {"predicate": {"value": "key1"}, "object": {"value": 2}, "label": {"value": "label1"}},
            {"predicate": {"value": "key2"}, "object": {"value": "value2"}, "label": {"value": "label1"}}
        ]
        class_schema = {
            "properties": {
                "key1": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "datatype": "http://www.w3.org/2001/XMLSchema#integer"
                },
                "key2": {
                    "type": "string",
                    "datatype": "http://www.w3.org/2001/XMLSchema#string"
                },
                "rdf:type": {
                    "type": "string",
                    "datatype": "http://www.w3.org/2001/XMLSchema#string"
                }
            }
        }
        expected = {
            "key1": [2],
            "key2": "value2",
            u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': "some:Class"}
        response = get_instance.build_items_dict(bindings, "some:Class", True, class_schema)
        self.assertEqual(response, expected)

    def test_assemble_instance_json_with_object_labels(self):
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                u'object': {u'type': u'literal', u'value': u'Cricket becomes the most popular sport of Brazil'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'object_label': {u'type': u'literal', u'value': u'News'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://brmedia.com/related_to'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/Cricket'},
                u'object_label': {u'type': u'literal', u'value': u'Cricket'}
            }
        ]
        class_schema = mock_schema({
            u'http://www.w3.org/2000/01/rdf-schema#label': "string",
            u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': "string",
            u'http://brmedia.com/related_to': "string_uri"
        }, "http://dbpedia.org/ontology/News")
        computed = get_instance.build_items_dict(bindings, "http://dbpedia.org/ontology/News", 1, class_schema)
        expected = {
            u'http://www.w3.org/2000/01/rdf-schema#label': u'Cricket becomes the most popular sport of Brazil',
            u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://dbpedia.org/ontology/News',
            u'http://brmedia.com/related_to': {"@id": "http://dbpedia.org/ontology/Cricket", "title": u"Cricket"}
        }
        self.assertEqual(computed, expected)

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.instance.get_instance.logger.debug")
    @patch("brainiak.instance.get_instance.logger")
    def test_assemble_instance_json_with_an_object_which_does_not_have_label(self, mlogger, mdebug, msettings):
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://brmedia.com/related_to'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/Cricket'},
            }
        ]
        class_schema = mock_schema({
            u'http://www.w3.org/2000/01/rdf-schema#label': "string",
            u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': "string",
            u'http://brmedia.com/related_to': "string_uri"
        }, "http://dbpedia.org/ontology/News")
        get_instance.build_items_dict(bindings, "http://dbpedia.org/ontology/News", 1, class_schema)
        expected_msg = "The predicate http://brmedia.com/related_to refers to an object http://dbpedia.org/ontology/Cricket which doesn't have a label. Set expand_object_properties=0 if you don't care about this ontological inconsistency."
        self.assertTrue(mdebug.called)
        self.assertEqual(mdebug.call_args[0][0], expected_msg)

    def prepare_input_and_expected_output(self, object_value):
        bindings = [
            {
                "predicate": {"value": "birthCity"},
                "object": {"value": "Rio de Janeiro"},
                "label": {"value": "birth place"},
                "super_property": {"value": "birthPlace"}
            },
            {
                "predicate": {"value": "birthPlace"},
                "object": {"value": object_value},
                "label": {"value": "birth place"}
            }
        ]
        return bindings

    def test_build_items_dict_with_super_property_and_same_value(self):
        bindings = self.prepare_input_and_expected_output(object_value="Rio de Janeiro")
        class_schema = mock_schema({
            u'birthPlace': "string",
            u'birthCity': "string",
        }, "http://class.uri")

        expected = {
            "birthCity": "Rio de Janeiro",
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://class.uri'
        }
        response = get_instance.build_items_dict(bindings, "http://class.uri", False, class_schema)

        self.assertEqual(response, expected)

    def test_build_items_dict_with_super_property_and_different_values(self):
        bindings = self.prepare_input_and_expected_output(object_value="Brasil")

        class_schema = mock_schema({
            u'birthPlace': "string",
            u'birthCity': "string",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "string"
        }, "http://class.uri")

        expected = {
            "birthCity": "Rio de Janeiro",
            "birthPlace": "Brasil",
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://class.uri'
        }
        response = get_instance.build_items_dict(bindings, "http://class.uri", False, class_schema)
        self.assertEqual(response, expected)

    def test_build_items_dict_with_super_property_and_different_values_expanding_uri(self):
        bindings = self.prepare_input_and_expected_output(object_value="Brasil")

        class_schema = mock_schema({
            u'birthPlace': "string",
            u'birthCity': "string",
        }, "http://class.uri")

        expected = {
            "birthCity": "Rio de Janeiro",
            "birthPlace": "Brasil",
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://class.uri'
        }
        response = get_instance.build_items_dict(bindings, "http://class.uri", False, class_schema)
        self.assertEqual(response, expected)

    def test_remove_super_properties_does_not_change_items_dict(self):
        items_dict = {
            u'rdfs:label': u'Seba Fern\xe1ndez - Sebasti\xe1n Bruno Fern\xe1ndez Miglierina',
            u'base:nome_completo': u'Sebasti\xe1n Bruno Fern\xe1ndez Miglierina',
            u'base:data_de_nascimento': u'1985-05-23'
        }
        super_predicates = {
            u'rdfs:label': u'upper:name',
            u'virtrdf:label': u'foaf:name',
            u'upper:fullName': u'person:fullName'
        }
        computed = get_instance.remove_super_properties(items_dict, super_predicates)
        self.assertEqual(computed, None)

        expected_items_dict = {
            u'base:data_de_nascimento': u'1985-05-23',
            u'rdfs:label': u'Seba Fern\xe1ndez - Sebasti\xe1n Bruno Fern\xe1ndez Miglierina',
            u'base:nome_completo': u'Sebasti\xe1n Bruno Fern\xe1ndez Miglierina'
        }
        self.assertEqual(items_dict, expected_items_dict)

    def test_remove_super_properties_changes_items_dict(self):
        items_dict = {
            u'rdfs:label': u'Seba Fern\xe1ndez - Sebasti\xe1n Bruno Fern\xe1ndez Miglierina',
            u'upper:name': u'Seba Fern\xe1ndez - Sebasti\xe1n Bruno Fern\xe1ndez Miglierina',
            u'base:data_de_nascimento': u'1985-05-23'
        }
        super_predicates = {
            u'rdfs:label': u'upper:name',
            u'virtrdf:label': u'foaf:name',
            u'upper:fullName': u'person:fullName'
        }
        computed = get_instance.remove_super_properties(items_dict, super_predicates)
        self.assertEqual(computed, None)

        expected_items_dict = {
            u'base:data_de_nascimento': u'1985-05-23',
            u'upper:name': u'Seba Fern\xe1ndez - Sebasti\xe1n Bruno Fern\xe1ndez Miglierina'
        }
        self.assertEqual(items_dict, expected_items_dict)

    def test_convert_to_python_array_with_integer(self):
        class_schema = {
            "properties": {
                "key1": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "datatype": u'http://www.w3.org/2001/XMLSchema#integer'
                },
                "key2": {
                    "type": "string",
                    "datatype": u'http://www.w3.org/2001/XMLSchema#integer'
                },
                "rdf:type": {
                    "type": "string",
                    "datatype": u'http://www.w3.org/2001/XMLSchema#integer'
                }
            }
        }
        predicate_uri = "key1"
        object_value = "12"
        result = get_instance._convert_to_python(object_value, class_schema, predicate_uri)
        expected = 12
        self.assertEqual(expected, result)

    def test_convert_to_python_float(self):
        class_schema = {
            "properties": {
                "key1": {
                    "type": "number",
                    "datatype": u'http://www.w3.org/2001/XMLSchema#float'
                },
            }
        }
        predicate_uri = "key1"
        object_value = "12.5"
        result = get_instance._convert_to_python(object_value, class_schema, predicate_uri)
        expected = 12.5
        self.assertEqual(expected, result)

    def test_convert_to_python_boolean(self):
        class_schema = {
            "properties": {
                "key1": {
                    "type": "boolean",
                    "datatype": u'http://www.w3.org/2001/XMLSchema#boolean'
                },
            }
        }
        predicate_uri = "key1"
        object_value = "0"
        result = get_instance._convert_to_python(object_value, class_schema, predicate_uri)
        expected = False
        self.assertEqual(expected, result)

    def test_convert_to_python_string(self):
        class_schema = {
            "properties": {
                "key1": {
                    "type": "string",
                    "datatype": u'http://www.w3.org/2001/XMLSchema#string'
                },
            }
        }
        predicate_uri = "key1"
        object_value = "value1"
        result = get_instance._convert_to_python(object_value, class_schema, predicate_uri)
        expected = u"value1"
        self.assertEqual(expected, result)

    def test_convert_to_python_predicate_uri_not_in_schema(self):
        class_schema = {
            "properties": {
                "key1": {"type": "string"},
            }
        }
        predicate_uri = "key_not_in_schema"
        object_value = "value1"
        result = get_instance._convert_to_python(object_value, class_schema, predicate_uri)
        expected = "value1"
        self.assertEqual(expected, result)
