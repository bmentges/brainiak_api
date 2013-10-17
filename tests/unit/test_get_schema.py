import unittest
from brainiak.prefixes import SHORTEN
import brainiak.schema.get_class as schema
from brainiak import prefixes
from brainiak.schema.get_class import _extract_cardinalities, assemble_predicate, convert_bindings_dict, normalize_predicate_range, merge_ranges, join_predicates, get_common_key


class AuxiliaryFunctionsTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        prefixes._MAP_SLUG_TO_PREFIX['test'] = 'http://test/person/'
        prefixes._MAP_PREFIX_TO_SLUG['http://test/person/'] = 'test'

    def tearDown(self):
        del prefixes._MAP_SLUG_TO_PREFIX['test']
        del prefixes._MAP_PREFIX_TO_SLUG['http://test/person/']

    #def test_extract_cardinalities_raises_exception_due_to_lack_of_range(self):
    #    binding = [{
    #        u'predicate': {u'type': u'uri',
    #                       u'value': u'http://test/person/gender'},
    #        u'min': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
    #                 u'type': u'typed-literal', u'value': u'1'}
    #    }]
    #    with self.assertRaises(schema.InvalidSchema) as error:
    #        _extract_cardinalities(binding, {})
    #        self.assertEqual(error.exception, "InvalidSchema: The property http://test/person/gender does not have a range definition")

    def test_extract_cardinalities_raises_exception_due_to_improper_min_value(self):
        binding = [{
            u'predicate': {u'type': u'uri',
                           u'value': u'http://test/person/gender'},
            u'range': {u'type': u'uri',
                       u'value': u'http://test/person/Gender'},
            u'min': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                     u'type': u'typed-literal', u'value': u'abc'}
        }]
        with self.assertRaises(schema.InvalidSchema) as error:
            _extract_cardinalities(binding, {})
            self.assertEqual(error.exception, "InvalidSchema: The property http://test/person/gender defines a non-integer owl:minQualifiedCardinality abc")

    def test_extract_cardinalities_raises_exception_due_to_improper_max_value(self):
        binding = [{
            u'predicate': {u'type': u'uri',
                           u'value': u'http://test/person/gender'},
            u'range': {u'type': u'uri',
                       u'value': u'http://test/person/Gender'},
            u'max': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                     u'type': u'typed-literal', u'value': u'abc'}
        }]
        with self.assertRaises(schema.InvalidSchema) as error:
            _extract_cardinalities(binding, {})
            self.assertEqual(error.exception, "InvalidSchema: The property http://test/person/gender defines a non-integer owl:maxQualifiedCardinality abc")

    def test_extract_min_1_required_true(self):
        binding = [{
            u'predicate': {u'type': u'uri',
                           u'value': u'http://test/person/gender'},
            u'range': {u'type': u'uri',
                       u'value': u'http://test/person/Gender'},
            u'min': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                     u'type': u'typed-literal', u'value': u'1'}
        }]
        extracted = _extract_cardinalities(binding, {})
        expected = {u'http://test/person/gender': {u'http://test/person/Gender': {'required': True, 'minItems': 1}}}
        self.assertEqual(extracted, expected)

    def test_extract_min_0(self):
        binding = [{
            u'predicate': {u'type': u'uri',
                           u'value': u'http://test/person/gender'},
            u'range': {u'type': u'uri',
                       u'value': u'http://test/person/Gender'},
            u'min': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                     u'type': u'typed-literal', u'value': u'0'}
        }]
        extracted = _extract_cardinalities(binding, {})
        expected = {u'http://test/person/gender': {u'http://test/person/Gender': {'minItems': 0}}}
        self.assertEqual(extracted, expected)

    def test_extract_max_1_show_omit(self):
        binding = [{
            u'predicate': {u'type': u'uri',
                           u'value': u'http://test/person/gender'},
            u'range': {u'type': u'uri',
                       u'value': u'http://test/person/Gender'},
            u'max': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                     u'type': u'typed-literal', u'value': u'1'}
        }]
        extracted = _extract_cardinalities(binding, {})
        expected = {u'http://test/person/gender': {u'http://test/person/Gender': {'maxItems': 1}}}
        self.assertEqual(extracted, expected)

    def test_extract_min_1_and_max_1_required_true(self):
        binding = [{
            u'predicate': {u'type': u'uri',
                           u'value': u'http://test/person/gender'},
            u'range': {u'type': u'uri',
                       u'value': u'http://test/person/Gender'},
            u'min': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                     u'type': u'typed-literal', u'value': u'1'},
            u'max': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                     u'type': u'typed-literal', u'value': u'1'}
        }]
        extracted = _extract_cardinalities(binding, {})
        expected = {u'http://test/person/gender': {u'http://test/person/Gender': {'required': True, 'minItems': 1, 'maxItems': 1}}}
        self.assertEqual(extracted, expected)

    def test_assemble_predicate_with_object_property(self):
        expected_predicate_dict = {'description': u'G\xeanero.',
                                   'range': {'graph': u'http://test/person/',
                                             '@id': u'http://test/person/Gender',
                                             'title': u'G\xeanero da Pessoa',
                                             'type': 'string',
                                             'format': 'uri'},
                                   'graph': u'http://test/person/',
                                   'class': u'http://test/person/AnyClass',
                                   'format': 'uri',
                                   'title': u'Sexo',
                                   'type': 'string'}
        name = u'http://test/person/gender'
        predicate = {u'predicate': {u'type': u'uri', u'value': u'http://test/person/gender'},
                     u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
                     u'range': {u'type': u'uri', u'value': u'http://test/person/Gender'},
                     u'range_graph': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'range_label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'G\xeanero da Pessoa'},
                     u'title': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Sexo'},
                     u'predicate_graph': {u'typce': u'uri', u'value': u'http://test/person/'},
                     u'predicate_comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'G\xeanero.'},
                     u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}}
        cardinalities = {u'http://test/person/gender': {u'http://test/person/Gender': {'minItems': 1, 'maxItems': 1}}}
        context = prefixes.MemorizeContext(normalize_uri=SHORTEN)
        context.prefix_to_slug('http://test/person')
        # test call

        effective_predicate_dict = assemble_predicate(name, predicate, cardinalities, context)
        self.assertEqual(context.object_properties, {'test:gender': 'test:Gender'})
        self.assertEqual(context.context, {})
        self.assertEqual(expected_predicate_dict, effective_predicate_dict)

    def test_ignore_annotation_properties(self):
        name = u'http://test/person/gender'
        predicate = {u'predicate': {u'type': u'uri', u'value': u'http://test/person/gender'},
                     u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
                     u'range': {u'type': u'uri', u'value': u'http://test/person/Gender'},
                     u'range_graph': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'range_label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'G\xeanero da Pessoa'},
                     u'title': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Sexo'},
                     u'predicate_graph': {u'typce': u'uri', u'value': u'http://test/person/'},
                     u'predicate_comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'G\xeanero.'},
                     u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#AnnotationProperty'}}
        cardinalities = {u'http://test/person/gender': {u'http://test/person/Gender': {'minItems': 1, 'maxItems': 1}}}
        context = prefixes.MemorizeContext(normalize_uri=SHORTEN)
        context.prefix_to_slug('http://test/person')
        with self.assertRaises(schema.InvalidSchema) as error:
            assemble_predicate(name, predicate, cardinalities, context)
            self.assertEqual(error.exception, "InvalidSchema: Predicates of type http://www.w3.org/2002/07/owl#AnnotationProperty are not supported yet")

    def test_assemble_predicate_with_datatype_property(self):
        expected_predicate_dict = {'description': u'Nome completo da pessoa',
                                   'graph': u'http://test/person/',
                                   'title': u'Nome',
                                   'type': 'string',
                                   'class': u'http://test/person/AnyClass',
                                   'datatype': u'http://www.w3.org/2001/XMLSchema#string'}
        name = u'http://test/person/gender'
        predicate = {u'predicate': {u'type': u'uri', u'value': u'http://test/person/name'},
                     u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
                     u'range': {u'type': u'uri', u'value': u'http://www.w3.org/2001/XMLSchema#string'},
                     u'title': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nome'},
                     u'range_graph': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'range_label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nome da Pessoa'},
                     u'predicate_graph': {u'type': u'uri', u'value': u'http://test/person/'},
                     u'predicate_comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nome completo da pessoa'},
                     u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'}}
        cardinalities = {}
        context = prefixes.MemorizeContext(normalize_uri=SHORTEN)
        context.prefix_to_slug('http://test/person')
        # test call
        effective_predicate_dict = assemble_predicate(name, predicate, cardinalities, context)
        self.assertEqual(len(context.object_properties), 0)
        self.assertEqual(expected_predicate_dict, effective_predicate_dict)
        self.assertEqual(context.context, {})

    def test_assemble_predicate_cardinality_influences_type(self):
        predicate_uri = "http://example.onto/hasChild"
        binding_row = {
            u'domain_class': {u'type': u'uri', u'value': u'http://example.onto/Human'},
            u'predicate': {u'type': u'uri', u'value': u'http://example.onto/hasChild'},
            u'predicate_graph': {u'type': u'uri', u'value': u'http://test.com/'},
            u'range': {u'type': u'uri', u'value': u'http://example.onto/Human'},
            u'range_graph': {u'type': u'uri', u'value': u'http://test.com/'},
            u'range_label': {u'type': u'literal', u'value': u'Humano', u'xml:lang': u'pt'},
            u'title': {u'type': u'literal', u'value': u'Has child (son or daughter)'},
            u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'}
        }
        cardinalities = {
            u'http://example.onto/furColour': {
                u'http://example.onto/FurColour': {'minItems': 1, 'required': True}
            },
            u'http://example.onto/gender': {
                u'http://example.onto/Gender': {'maxItems': 1, 'minItems': 1, 'required': True}
            },
            u'http://example.onto/hasChild': {
                u'http://example.onto/Human': {'maxItems': 888}
            },
            u'http://example.onto/hasParent': {
                u'http://example.onto/Human': {'maxItems': 2}
            }
        }
        context = prefixes.MemorizeContext(normalize_uri=SHORTEN)
        context.prefix_to_slug('http://test/person')
        computed = assemble_predicate(predicate_uri, binding_row, cardinalities, context)
        expected = {
            'class': u'http://example.onto/Human',
            'graph': u'http://test.com/',
            'items': {
                'format': 'uri',
                'type': 'string'
            },
            'maxItems': 888,
            'range': {
                '@id': u'http://example.onto/Human',
                'format': 'uri',
                'graph': u'http://test.com/',
                'title': u'Humano',
                'type': 'string'
            },
            'title': u'Has child (son or daughter)',
            'type': 'array'
        }
        self.assertEqual(computed, expected)

    def test_normalize_predicate_range_in_predicate_without_range_without_format(self):
        sample_predicate = {'type': 'some type'}
        expected = {'type': 'some type', 'range': {'type': 'some type'}}
        computed = normalize_predicate_range(sample_predicate)
        self.assertEqual(computed, expected)

    def test_normalize_predicate_range_in_predicate_without_range_with_format(self):
        sample_predicate = {'type': 'some type', 'format': 'some format'}
        expected = {'type': 'some type', 'format': 'some format', 'range': {'type': 'some type', 'format': 'some format'}}
        computed = normalize_predicate_range(sample_predicate)
        self.assertEqual(computed, expected)

    def test_normalize_predicate_range_in_predicate_with_range(self):
        sample_predicate = {'type': 'some type', 'format': 'some format', 'range': 'xubiru'}
        expected = {'type': 'some type', 'format': 'some format', 'range': 'xubiru'}
        computed = normalize_predicate_range(sample_predicate)
        self.assertEqual(computed, expected)

    def test_merge_ranges_both_arent_lists(self):
        r1 = {'r1': 1}
        r2 = {'r2': 2}
        expected = [{'r1': 1}, {'r2': 2}]
        computed = merge_ranges(r1, r2)
        self.assertEqual(sorted(computed), sorted(expected))

    def test_merge_ranges_first_is_list(self):
        r1 = [{'r0': 0}, {'r1': 1}]
        r2 = {'r2': 2}
        expected = [{'r0': 0}, {'r1': 1}, {'r2': 2}]
        computed = merge_ranges(r1, r2)
        self.assertEqual(sorted(computed), sorted(expected))

    def test_merge_ranges_first_is_not_list(self):
        r1 = {'r1': 1}
        r2 = [{'r2': 2}, {'r3': 3}]
        expected = [{'r2': 2}, {'r3': 3}, {'r1': 1}]
        computed = merge_ranges(r1, r2)
        self.assertEqual(sorted(computed), sorted(expected))

    def test_merge_ranges_both_are_lists(self):
        r1 = [{'r0': 0}, {'r1': 1}]
        r2 = [{'r2': 2}, {'r3': 3}]
        expected = [{'r0': 0}, {'r1': 1}, {'r2': 2}, {'r3': 3}]
        computed = merge_ranges(r1, r2)
        self.assertEqual(sorted(computed), sorted(expected))

    def test_merge_ranges_deals_with_duplicates(self):
        r1 = {'r1': 1}
        r2 = {'r1': 1}
        expected = [{'r1': 1}]
        computed = merge_ranges(r1, r2)
        self.assertEqual(sorted(computed), sorted(expected))

    def test_get_common_key_exists(self):
        items = [{'a': 1}, {'a': 1}]
        expected = 1
        computed = get_common_key(items, 'a')
        self.assertEqual(computed, expected)

    def test_get_common_key_doesnt_exist(self):
        items = [{'a': 1}, {'a': 2}]
        expected = ''
        computed = get_common_key(items, 'a')
        self.assertEqual(computed, expected)

    def test_join_predicates(self):
        a_predicate = {
            'type': 'not your business',
            'format': 'as you like'
        }
        same_predicate = {
            'type': 'who knows',
            'format': 'who cares'
        }
        expected = {
            'type': 'array',
            'range': [
                {'type': 'not your business', 'format': 'as you like'},
                {'type': 'who knows', 'format': 'who cares'}
            ]
        }
        computed = join_predicates(a_predicate, same_predicate)
        self.assertEqual(computed['type'], expected['type'])
        self.assertFalse('format' in expected)
        self.assertEqual(sorted(computed['range']), sorted(expected['range']))


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

    def test_convert_bindings_dict_single_datatypeproperty(self):

        class ContextMock(prefixes.MemorizeContext):
            object_properties = {}
            context = {'test': 'http://test.graph/'}

        context = ContextMock(normalize_uri=SHORTEN)
        cardinalities = {}
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://test.graph/creation_date'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://test.graph/'},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/2001/XMLSchema#dateTime'},
                u'title': {u'type': u'literal', u'value': u'Creation Date'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'},
                u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
            }
        ]
        hierarchy = [u'http://test/person/AnyClass']
        computed = convert_bindings_dict(context, bindings, cardinalities, hierarchy)
        expected = {
            'http://test.graph/creation_date': {
                'graph': 'http://test.graph/',
                'title': u'Creation Date',
                'class': u'http://test/person/AnyClass',
                'type': 'string',
                'format': 'date',
                'datatype': u'http://www.w3.org/2001/XMLSchema#dateTime'
            }
        }

        self.assertEqual(computed, expected)

    def test_convert_bindings_dict_single_predicate_single_range(self):

        class ContextMock(prefixes.MemorizeContext):
            object_properties = {}
            context = {'test': 'http://test.graph/'}

        context = ContextMock(normalize_uri=SHORTEN)
        cardinalities = {}
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://test.graph/hasParent'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://test.graph/'},
                u'range': {u'type': u'uri', u'value': u'http://test.graph/Person'},
                u'title': {u'type': u'literal', u'value': u'Has parent'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
            }
        ]

        hierarchy = [u'http://test/person/AnyClass']
        computed = convert_bindings_dict(context, bindings, cardinalities, hierarchy)
        expected = {
            'http://test.graph/hasParent': {
                'graph': 'http://test.graph/',
                'class': u'http://test/person/AnyClass',
                'range': {
                    'graph': '',
                    '@id': 'http://test.graph/Person',
                    'title': '',
                    'format': 'uri',
                    'type': 'string'},
                'title': u'Has parent',
                'type': 'array',
                'items': {'type': 'string', 'format': 'uri'}

            }
        }

        self.assertEqual(computed, expected)

    def test_convert_bindings_dict_two_predicates_single_range(self):
        class ContextMock(prefixes.MemorizeContext):
            object_properties = {}
            context = {'g1': 'http://semantica.globo.com/G1/'}

        context = ContextMock(normalize_uri=SHORTEN)
        cardinalities = {}
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/cita_a_entidade'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/'},
                u'range_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/'},
                u'range': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Criatura'},
                u'title': {u'type': u'literal', u'value': u'Entidades'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/trata_do_assunto'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/'},
                u'range': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/AssuntoCarro'},
                u'range_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/'},
                u'title': {u'type': u'literal', u'value': u'Assuntos'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
            },
        ]
        hierarchy = [u'http://test/person/AnyClass']
        computed = convert_bindings_dict(context, bindings, cardinalities, hierarchy)
        expected = {
            'http://semantica.globo.com/G1/cita_a_entidade': {
                'graph': u'http://semantica.globo.com/G1/',
                'class': u'http://test/person/AnyClass',
                'range': {
                    'graph': u'http://semantica.globo.com/',
                    '@id': u'http://semantica.globo.com/base/Criatura',
                    'title': '',
                    'type': 'string',
                    'format': 'uri'},
                'title': u'Entidades',
                'type': 'array',
                'items': {'type': 'string', 'format': 'uri'}

            },
            'http://semantica.globo.com/G1/trata_do_assunto': {
                'graph': u'http://semantica.globo.com/G1/',
                'class': u'http://test/person/AnyClass',
                'range': {
                    'graph': u'http://semantica.globo.com/',
                    '@id': u'http://semantica.globo.com/G1/AssuntoCarro',
                    'title': '',
                    'type': 'string',
                    'format': 'uri'},
                'title': u'Assuntos',
                'type': 'array',
                'items': {'type': 'string', 'format': 'uri'}
            }
        }

        self.assertEqual(computed, expected)

    def test_convert_bindings_dict_raise_exception(self):
        class ContextMock(prefixes.MemorizeContext):
            object_properties = {}
            context = {'g1': 'http://semantica.globo.com/G1/'}

        context = ContextMock(normalize_uri=SHORTEN)
        cardinalities = {}
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/cita_a_entidade'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/'},
                u'range_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/'},
                u'range': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Criatura'},
                u'title': {u'type': u'literal', u'value': u'Entidades'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/cita_a_entidade'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/'},
                u'range_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/'},
                u'range': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Criatura'},
                u'title': {u'type': u'literal', u'value': u'Entidades'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
            }
        ]
        hierarchy = [u'http://test/person/AnyClass']

        with self.assertRaises(schema.InvalidSchema) as error:
            convert_bindings_dict(context, bindings, cardinalities, hierarchy)
            self.assertEqual(error.exception, "InvalidSchema: The property g1:cita_a_entidade seems to be duplicated in class http://test/person/AnyClass")

    def test_convert_bindings_dict_single_predicate_multiple_ranges_of_same_type(self):

        class ContextMock(prefixes.MemorizeContext):
            object_properties = {}
            context = {'test': 'http://test.graph/'}

        context = ContextMock(normalize_uri=SHORTEN)
        cardinalities = {}
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://test.graph/predicate'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://test.graph/'},
                u'range': {u'type': u'uri', u'value': u'http://test.graph/RangeOne'},
                u'title': {u'type': u'literal', u'value': u'test'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
            },
            {
                u'predicate': {u'type': u'uri', u'value': u'http://test.graph/predicate'},
                u'predicate_graph': {u'type': u'uri', u'value': u'http://test.graph/'},
                u'range': {u'type': u'uri', u'value': u'http://test.graph/RangeTwo'},
                u'title': {u'type': u'literal', u'value': u'test'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'domain_class': {u'type': u'uri', u'value': u'http://test/person/AnyClass'},
            }
        ]
        hierarchy = [u'http://test/person/AnyClass']
        computed = convert_bindings_dict(context, bindings, cardinalities, hierarchy)
        expected = {
            'http://test.graph/predicate': {
                'graph': 'http://test.graph/',
                'range': [
                    {
                        'graph': '',
                        '@id': 'http://test.graph/RangeOne',
                        'title': '',
                        'type': 'string',
                        'format': 'uri'
                    },
                    {
                        'graph': '',
                        '@id': 'http://test.graph/RangeTwo',
                        'title': '',
                        'type': 'string',
                        'format': 'uri'
                    }
                ],
                'title': u'test',
                'type': 'string',
                'format': 'uri'
            }
        }
        self.assertItemsEqual(computed, expected)


class SelectMostSpecializedInHierarchyTestCase(unittest.TestCase):

    def test_most_specialized_predicate_with_valid_hierarchy(self):
        predicate_in_A = {'class': 'A'}
        predicate_in_B = {'class': 'B'}
        hierarchy = ['B', 'A']  # B inherits from A
        result = schema.most_specialized_predicate(hierarchy, predicate_in_A, predicate_in_B)
        self.assertEqual(result, predicate_in_B)
