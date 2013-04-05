import json
import unittest

import brainiak.schema.resource as schema
from brainiak import prefixes
from brainiak.schema.resource import _extract_cardinalities, build_predicate_dict, convert_bindings_dict
from tests import TornadoAsyncTestCase


class AuxiliaryFunctionsTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        prefixes._MAP_SLUG_TO_PREFIX['test'] = 'http://test/person/'
        prefixes._MAP_PREFIX_TO_SLUG['http://test/person/'] = 'test'

    def tearDown(self):
        del prefixes._MAP_SLUG_TO_PREFIX['test']
        del prefixes._MAP_PREFIX_TO_SLUG['http://test/person/']

    def test_extract_min(self):
        binding = [{
            u'predicate': {u'type': u'uri',
                           u'value': u'http://test/person/gender'},
            u'range': {u'type': u'uri',
                       u'value': u'http://test/person/Gender'},
            u'min': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                     u'type': u'typed-literal', u'value': u'1'}
        }]
        extracted = _extract_cardinalities(binding)
        expected = {u'http://test/person/gender': {u'http://test/person/Gender': {'minItems': u'1'}}}
        self.assertEqual(extracted, expected)

    def test_extract_max(self):
        binding = [{
            u'predicate': {u'type': u'uri',
                           u'value': u'http://test/person/gender'},
            u'range': {u'type': u'uri',
                       u'value': u'http://test/person/Gender'},
            u'max': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                     u'type': u'typed-literal', u'value': u'1'}
        }]
        extracted = _extract_cardinalities(binding)
        expected = {u'http://test/person/gender': {u'http://test/person/Gender': {'maxItems': u'1'}}}
        self.assertEqual(extracted, expected)

    def test_extract_options(self):
        binding = [
            {u'predicate': {u'type': u'uri',
                            u'value': u'http://test/person/gender'},
             u'enumerated_value': {u'type': u'uri',
                                   u'value': u'http://test/person/Gender/Male'},
             u'range': {u'type': u'bnode', u'value': u'nodeID://b72146'},
             u'enumerated_value_label': {u'xml:lang': u'pt', u'type': u'literal',
                                         u'value': u'Masculino'}},
            {u'predicate': {u'type': u'uri',
                            u'value': u'http://test/person/gender'},
             u'enumerated_value': {u'type': u'uri',
                                   u'value': u'http://test/person/Gender/Female'},
             u'range': {u'type': u'bnode', u'value': u'nodeID://b72146'},
             u'enumerated_value_label': {u'xml:lang': u'pt', u'type': u'literal',
                                         u'value': u'Feminino'}}
        ]
        extracted = _extract_cardinalities(binding)
        expected = {u'http://test/person/gender': {
                    'enum': [u'http://test/person/Gender/Male', u'http://test/person/Gender/Female']}}
        self.assertEqual(extracted, expected)

    def test_build_predicate_dict_with_object_property(self):
        expected_predicate_dict = {'comment': u'G\xeanero.',
                                   'range': {'graph': 'test',
                                             '@id': 'test:Gender',
                                             'title': u'G\xeanero da Pessoa'},
                                   'graph': 'test',
                                   'maxItems': u'1',
                                   'format': 'uri',
                                   'minItems': u'1',
                                   'title': u'Sexo',
                                   'enum': [u'http://test/person/Gender/Male',
                                            u'http://test/person/Gender/Female'],
                                   'type': 'string'}
        # params
        name = u'http://test/person/gender'
        predicate = {u'predicate': {u'type': u'uri', u'value': u'http://test/person/gender'},
                     u'range': {u'type': u'uri', u'value': u'http://test/person/Gender'},
                     u'grafo_do_range': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'label_do_range': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'G\xeanero da Pessoa'},
                     u'title': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Sexo'},
                     u'predicate_graph': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'predicate_comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'G\xeanero.'},
                     u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}}
        cardinalities = {u'http://test/person/gender': {'enum': [u'http://test/person/Gender/Male',
                                                                 u'http://test/person/Gender/Female'],
                                                        u'http://test/person/Gender': {'minItems': u'1', 'maxItems': u'1'}}}
        context = prefixes.MemorizeContext()
        context.prefix_to_slug('http://test/person')
        # test call
        effective_predicate_dict = build_predicate_dict(name, predicate, cardinalities, context)
        self.assertEqual(expected_predicate_dict, effective_predicate_dict)

    def test_build_predicate_dict_with_datatype_property(self):
        expected_predicate_dict = {'comment': u'Nome completo da pessoa',
                                   'graph': 'test',
                                   'title': u'Nome',
                                   'type': 'string'}
        # params
        name = u'http://test/person/gender'
        predicate = {u'predicate': {u'type': u'uri', u'value': u'http://test/person/name'},
                     u'range': {u'type': u'uri', u'value': u'http://www.w3.org/2001/XMLSchema#string'},
                     u'title': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nome'},
                     u'grafo_do_range': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'label_do_range': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nome da Pessoa'},
                     u'predicate_graph': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'predicate_comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nome completo da pessoa'},
                     u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'}}
        cardinalities = {}
        context = prefixes.MemorizeContext()
        context.prefix_to_slug('http://test/person')
        # test call
        effective_predicate_dict = build_predicate_dict(name, predicate, cardinalities, context)
        self.assertEqual(expected_predicate_dict, effective_predicate_dict)
#        u'http://semantica.globo.com/person/fullName': {u'http://www.w3.org/2001/XMLSchema#string': {'maxItems': u'1'}},


class AuxiliaryFunctionsTestCase2(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.original_query_predicate_with_lang = schema._query_predicate_with_lang
        self.original_query_predicate_without_lang = schema._query_predicate_without_lang

    def tearDown(self):
        schema._query_predicate_with_lang = self.original_query_predicate_with_lang
        schema._query_predicate_without_lang = self.original_query_predicate_without_lang

    def test_query_predicates_successful_with_lang(self):
        result_dict = {"results": {"bindings": [1]}}

        schema._query_predicate_with_lang = lambda params: result_dict

        response = schema.query_predicates({"class_uri": "class_uri", "lang": ""})
        self.assertEqual(response, result_dict)

    def test_query_predicates_successful_without_lang(self):
        response_text = {"results": {"bindings": []}}
        response_without_lang_text = {"results": {"bindings": [1]}}

        schema._query_predicate_with_lang = lambda params: response_text
        schema._query_predicate_without_lang = lambda params: response_without_lang_text

        params = {
            "class_uri": "class_uri",
            "graph_uri": "graph_uri",
            "lang": ""
        }
        response = schema.query_predicates(params)
        self.assertEqual(response, response_without_lang_text)

    def test_convert_bindings_dict_single_predicate_single_range(self):

        class ContextMock(prefixes.MemorizeContext):
            object_properties = {}
            context = {'g1': 'http://semantica.globo.com/G1/'}

        context = ContextMock()
        cardinalities = {}
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/cita_a_entidade'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/'},
                u'range': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Criatura'},
                u'title': {u'type': u'literal', u'value': u'Entidades'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            }
        ]

        computed = convert_bindings_dict(context, bindings, cardinalities)
        expected = {
            'g1:cita_a_entidade': {
                'graph': 'g1',
                'range': {'graph': '', '@id': 'base:Criatura', 'title': ''},
                'title': u'Entidades',
                'type': 'string',
                'format': 'uri'
            }
        }

        self.assertEqual(computed, expected)

    def test_convert_bindings_dict_two_predicates_single_range(self):

        class ContextMock(prefixes.MemorizeContext):
            object_properties = {}
            context = {'g1': 'http://semantica.globo.com/G1/'}

        context = ContextMock()
        cardinalities = {}
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/cita_a_entidade'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/'},
                u'range': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Criatura'},
                u'title': {u'type': u'literal', u'value': u'Entidades'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/trata_do_assunto'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/'},
                u'range': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/AssuntoCarro'},
                u'title': {u'type': u'literal', u'value': u'Assuntos'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}},
        ]

        computed = convert_bindings_dict(context, bindings, cardinalities)
        expected = {
            'g1:cita_a_entidade': {
                'graph': 'g1',
                'range': {'graph': '', '@id': 'base:Criatura', 'title': ''},
                'title': u'Entidades',
                'type': 'string',
                'format': 'uri'
            },
            'g1:trata_do_assunto': {
                'graph': 'g1',
                'range': {'graph': '', '@id': 'g1:AssuntoCarro', 'title': ''},
                'title': u'Assuntos',
                'type': 'string',
                'format': 'uri'
            }
        }

        self.assertEqual(computed, expected)

    # def test_convert_bindings_dict_single_predicate_multiple_range(self):

    #     class ContextMock(prefixes.MemorizeContext):
    #         object_properties = {}
    #         context = {'g1': 'http://semantica.globo.com/G1/'}

    #     context = ContextMock()
    #     cardinalities = {}
    #     bindings = [
    #         {
    #             u'predicate': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/cita_a_entidade'},
    #             u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/'},
    #             u'range': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Criatura'},
    #             u'title': {u'type': u'literal', u'value': u'Entidades'},
    #             u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
    #         },
    #         {
    #             u'predicate': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/cita_a_entidade'},
    #             u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/'},
    #             u'range': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Lugar'},
    #             u'title': {u'type': u'literal', u'value': u'Entidades'},
    #             u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}}
    #     ]

    #     computed = convert_bindings_dict(context, bindings, cardinalities)
    #     expected = [
    #         {
    #             'g1:cita_a_entidade': {
    #                 'graph': 'g1',
    #                 'range': [
    #                     {'graph': '', '@id': 'base:Lugar', 'title': ''},
    #                     #{'graph': '', '@id': 'base:Criatura', 'title': ''}
    #                 ],
    #                 'title': u'Entidades',
    #                 'type': 'string',
    #                 'format': 'uri'
    #             }
    #         }
    #     ]
    #     self.assertEqual(computed, expected)
