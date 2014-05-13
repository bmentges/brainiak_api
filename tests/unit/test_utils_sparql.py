import logging
from unittest import TestCase
import uuid
from mock import patch

from brainiak.prefixes import MemorizeContext
from brainiak.utils.sparql import *

from tests.mocks import mock_schema, triplestore_config


class MockSchemaTestCase(TestCase):

    maxDiff = None

    def test_mock_schema(self):
        class_object = mock_schema(
            {"personpedia:birthPlace": 'string_uri',
             "personpedia:gender": 'string_uri',
             "personpedia:wife": 'string_uri'},
            id="http://personpedia.com/Person",
            context={"personpedia": "http://personpedia.com/"}
        )
        expected_object = {
            'properties': {
                'http://personpedia.com/birthPlace': {
                    'range': {'type': 'string', 'format': 'uri'},
                    'type': 'string'
                },
                'http://personpedia.com/gender': {
                    'range': {'type': 'string', 'format': 'uri'},
                    'type': 'string'
                },
                'http://personpedia.com/wife': {
                    'range': {'type': 'string', 'format': 'uri'},
                    'type': 'string'
                }
            },
            "id": "http://personpedia.com/Person"
        }
        self.assertEqual(class_object, expected_object)


class ResultHandlerTestCase(TestCase):

    CLASS = {
        u'head': {u'link': [], u'vars': [u'graph', u'videoClass', u'program']},
        u'results': {u'distinct': False,
                     u'bindings': [
                         {
                             u'graph': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                             u'program': {u'type': u'uri', u'value': u'http://test.domain.com/base/Programa_Bem_Estar'},
                             u'videoClass': {u'type': u'uri', u'value': u'http://test.domain.com/G1/Video'}
                         }],
                     u'ordered': True}}

    def test_create_uri(self):
        original_uuid = uuid.uuid4
        uuid.uuid4 = lambda: "unique-id"
        computed = create_instance_uri("http://class_uri")
        uuid.uuid4 = original_uuid
        expected = "http://class_uri/unique-id"
        self.assertEqual(computed, expected)

    def test_get_result(self):
        expected = "http://test.domain.com/G1/Video"
        self.assertEqual(expected, get_one_value(self.CLASS, "videoClass"))

    def test_get_result_empty(self):
        self.assertFalse(get_one_value(self.CLASS, "chave_inexistente"))

    def test_is_result_empty_returns_true(self):
        empty_result_dict = {u'head': {u'link': [], u'vars': [u'graph', u'p', u'o']},
                             u'results': {u'distinct': False, u'bindings': [], u'ordered': True}}
        self.assertTrue(is_result_empty(empty_result_dict))

    def test_is_result_empty_returns_false(self):
        empty_result_dict = {u'head': {u'link': [], u'vars': [u'graph', u'p', u'o']},
                             u'results': {u'distinct': False, u'bindings': ["teste1", "teste2"], u'ordered': True}}
        self.assertFalse(is_result_empty(empty_result_dict))

    RESULT_DICT_WITH_LANG = {
        u'head': {u'link': [], u'vars': [u'label', u'comment']},
        u'results': {
            u'distinct': False, u'bindings': [
                {u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Pessoa'}},
                {u'comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Ser humano, vivo, morto ou fict\xedcio.'}}], u'ordered': True}}

    def test_filter_values_with_lang(self):
        expected = ["Pessoa"]
        result = filter_values(self.RESULT_DICT_WITH_LANG, "label")
        self.assertEqual(expected, result)

    def test_compress_keys_and_values(self):
        trilogy_from_virtuoso = {'results': {'bindings': [
            {u'title': {u'type': u'literal', u'value': u"The Hitchhiker's Guide to the Galaxy"}, u'year': {u'type': u'literal', u'value': "1979"}},
            {u'title': {u'type': u'literal', u'value': u"The Restaurant at the End of the Universe Life"}, u'year': {u'type': u'literal', u'value': "1980"}},
            {u'title': {u'type': u'literal', u'value': u"Life, the Universe and Everything"}, u'year': {u'type': u'literal', u'value': "1982"}},
            {u'title': {u'type': u'literal', u'value': u"So Long, and Thanks for All the Fish"}, u'year': {u'type': u'literal', u'value': "1984"}},
            {u'title': {u'type': u'literal', u'value': u"Mostly Harmless"}, u'year': {u'type': u'literal', u'value': "1992"}}]}}
        compressed_list = compress_keys_and_values(trilogy_from_virtuoso)
        expected_list = [
            {u'title': u"The Hitchhiker's Guide to the Galaxy", u'year': u"1979"},
            {u'title': u"The Restaurant at the End of the Universe Life", u'year': u"1980"},
            {u'title': u"Life, the Universe and Everything", u'year': u"1982"},
            {u'title': u"So Long, and Thanks for All the Fish", u'year': u"1984"},
            {u'title': u"Mostly Harmless", u'year': u"1992"}]
        self.assertEqual(compressed_list, expected_list)

    def test_compress_keys_and_values_with_keymap(self):
        trilogy_from_virtuoso = {'results': {'bindings': [
            {u'title': {u'type': u'literal', u'value': u"The Hitchhiker's Guide to the Galaxy"}, u'year': {u'type': u'literal', u'value': "1979"}},
            {u'title': {u'type': u'literal', u'value': u"The Restaurant at the End of the Universe Life"}, u'year': {u'type': u'literal', u'value': "1980"}},
            {u'title': {u'type': u'literal', u'value': u"Life, the Universe and Everything"}, u'year': {u'type': u'literal', u'value': "1982"}},
            {u'title': {u'type': u'literal', u'value': u"So Long, and Thanks for All the Fish"}, u'year': {u'type': u'literal', u'value': "1984"}},
            {u'title': {u'type': u'literal', u'value': u"Mostly Harmless"}, u'year': {u'type': u'literal', u'value': "1992"}}]}}
        compressed_list = compress_keys_and_values(trilogy_from_virtuoso, {'title': 'custom_title', 'year': 'custom_year'})
        expected_list = [
            {u'custom_title': u"The Hitchhiker's Guide to the Galaxy", u'custom_year': u"1979"},
            {u'custom_title': u"The Restaurant at the End of the Universe Life", u'custom_year': u"1980"},
            {u'custom_title': u"Life, the Universe and Everything", u'custom_year': u"1982"},
            {u'custom_title': u"So Long, and Thanks for All the Fish", u'custom_year': u"1984"},
            {u'custom_title': u"Mostly Harmless", u'custom_year': u"1992"}]
        self.assertEqual(compressed_list, expected_list)

    def test_compress_keys_and_values_with_ignore_keys(self):
        trilogy_from_virtuoso = {'results': {'bindings': [
            {u'title': {u'type': u'literal', u'value': u"The Hitchhiker's Guide to the Galaxy"}, u'year': {u'type': u'literal', u'value': "1979"}},
            {u'title': {u'type': u'literal', u'value': u"The Restaurant at the End of the Universe Life"}, u'year': {u'type': u'literal', u'value': "1980"}},
            {u'title': {u'type': u'literal', u'value': u"Life, the Universe and Everything"}, u'year': {u'type': u'literal', u'value': "1982"}},
            {u'title': {u'type': u'literal', u'value': u"So Long, and Thanks for All the Fish"}, u'year': {u'type': u'literal', u'value': "1984"}},
            {u'title': {u'type': u'literal', u'value': u"Mostly Harmless"}, u'year': {u'type': u'literal', u'value': "1992"}}]}}
        compressed_list = compress_keys_and_values(trilogy_from_virtuoso, ignore_keys=['year'])
        expected_list = [
            {u'title': u"The Hitchhiker's Guide to the Galaxy"},
            {u'title': u"The Restaurant at the End of the Universe Life"},
            {u'title': u"Life, the Universe and Everything"},
            {u'title': u"So Long, and Thanks for All the Fish"},
            {u'title': u"Mostly Harmless"}]
        self.assertEqual(compressed_list, expected_list)

    def test_compress_keys_and_values_with_context_and_value_that_is_uri(self):
        trilogy_from_virtuoso = {'results': {'bindings': [{'key': {'type': 'uri', 'value': 'http://xmlns.com/foaf/0.1/value'}}]}}
        context = MemorizeContext()
        compressed_list = compress_keys_and_values(trilogy_from_virtuoso, context=context)
        expected_list = [{'key': 'foaf:value'}]
        self.assertEqual(compressed_list, expected_list)

    def test_compress_keys_and_values_with_context_and_value_that_is_not_uri(self):
        trilogy_from_virtuoso = {'results': {'bindings': [{'key': {'type': 'not_uri', 'value': 'http://xmlns.com/foaf/0.1/value'}}]}}
        context = MemorizeContext()
        compressed_list = compress_keys_and_values(trilogy_from_virtuoso, context=context)
        expected_list = [{'key': 'http://xmlns.com/foaf/0.1/value'}]
        self.assertEqual(compressed_list, expected_list)


class GetOneTestCase(TestCase):

    response = {u'head': {u'link': [], u'vars': [u'graph', u'videoClass', u'program']},
                u'results': {u'distinct': False, u'bindings':
                             [{u'videoClass': {u'type': u'uri', u'value': u'http://test.domain.com/G1/Video'}}],
                             u'ordered': True}}

    def test_get_result(self):
        computed = get_one_value(self.response, "videoClass")
        expected = "http://test.domain.com/G1/Video"
        self.assertEqual(computed, expected)

    def test_get_result_empty(self):
        computed = get_one_value(self.response, "chave_inexistente")
        expected = False
        self.assertEqual(computed, expected)


class IsInsertResponseSuccessfulTestCase(TestCase):

    def test_is_response_successful_true(self):
        msg = "Insert into <http://some_graph/sample-place/>, 1 (or less) triples -- done"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertTrue(is_insert_response_successful(fake_response))

    def test_is_response_successful_false_with_0_tuples(self):
        msg = "Insert into <http://some_graph/sample-place/>, 0 (or less) triples -- done"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertFalse(is_insert_response_successful(fake_response))

    def test_is_response_successful_false_with_different_message(self):
        msg = "Failed"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertFalse(is_insert_response_successful(fake_response))

    def test_is_response_successful_false_with_no_response(self):
        self.assertFalse(is_insert_response_successful(None))


class IsModifyResponseSuccessfulTestCase(TestCase):

    def test_is_response_successful_true(self):
        msg = "Modify <http://somegraph/bla>, delete 2 (or less) and insert 1 (or less) triples -- done"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertTrue(is_modify_response_successful(fake_response))

    def test_is_response_successful_true_verify_delete_ok(self):
        msg = "Modify <http://somegraph/bla>, delete 2 (or less) and insert 1 (or less) triples -- done"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertTrue(is_modify_response_successful(fake_response, n_deleted=2))

    def test_is_response_successful_true_verify_delete_not_ok(self):
        msg = "Modify <http://somegraph/bla>, delete 2 (or less) and insert 1 (or less) triples -- done"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertFalse(is_modify_response_successful(fake_response, n_deleted=3))

    def test_is_response_successful_true_verify_insert_ok(self):
        msg = "Modify <http://somegraph/bla>, delete 2 (or less) and insert 1 (or less) triples -- done"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertTrue(is_modify_response_successful(fake_response, n_inserted=1))

    def test_is_response_successful_true_verify_insert_not_ok(self):
        msg = "Modify <http://somegraph/bla>, delete 2 (or less) and insert 1 (or less) triples -- done"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertFalse(is_modify_response_successful(fake_response, n_inserted=0))

    def test_is_response_successful_true_return_false_due_to_key_error(self):
        fake_response = {}
        self.assertFalse(is_modify_response_successful(fake_response, n_inserted=0))

    def test_is_response_successful_true_return_false_due_to_type_error(self):
        fake_response = None
        self.assertFalse(is_modify_response_successful(fake_response, n_inserted=0))


class SomeTriplesDeletedTestCase(TestCase):

    def test_deleted_triples(self):
        result_dict = {"head": {"link": [], "vars": ["callret-0"]}, "results": {"distinct": False, "ordered": True, "bindings": [{"callret-0": {"type": "literal", "value": "Delete from <a>, 1 (or less) triples -- done"}}]}}
        self.assertTrue(some_triples_deleted(result_dict, "a"))

    def test_not_deleted_triples(self):
        result_dict = {"head": {"link": [], "vars": ["callret-0"]}, "results": {"distinct": False, "ordered": True, "bindings": [{"callret-0": {"type": "literal", "value": "Delete from <a>, 0 triples -- nothing to do"}}]}}
        self.assertFalse(some_triples_deleted(result_dict, "a"))

    def test_delete_triples_unkown_result_structure(self):
        result_dict = {"head": "", "results": {"bindings": [{"unkown key name": {"value": "deleted"}}]}}
        self.assertRaises(UnexpectedResultException, some_triples_deleted, result_dict, "a")

    def test_delete_triples_unkown_result_message(self):
        result_dict = {"head": {"link": [], "vars": ["callret-0"]}, "results": {"distinct": False, "ordered": True, "bindings": [{"callret-0": {"type": "literal", "value": "Unknown message"}}]}}
        self.assertRaises(UnexpectedResultException, some_triples_deleted, result_dict, "a")


class LiteralLangTestCase(TestCase):

    def test_has_lang_literal_true(self):
        self.assertTrue(has_lang("'i18n'@en"))

    def test_has_lang_literal_false(self):
        self.assertFalse(has_lang("not i18n"))

    def test_has_lang_integer(self):
        self.assertFalse(has_lang(1))

    def test_has_lang_boolean(self):
        self.assertFalse(has_lang(False))


class IsResultTrueTestCase(TestCase):

    def test_is_result_true(self):
        result_dict = {"head": {"link": []}, "boolean": True}
        self.assertTrue(is_result_true(result_dict))

    def test_is_result_false(self):
        result_dict = {"head": {"link": []}, "boolean": False}
        self.assertFalse(is_result_true(result_dict))

    def test_is_result_false_boolean_not_in_dict(self):
        result_dict = {"head": {"link": [], "vars": ["callret-0"]}, "results": {"distinct": False, "ordered": True, "bindings": [{"callret-0": {"type": "literal", "value": "Unknown message"}}]}}
        self.assertFalse(is_result_true(result_dict))


class CreateExplicitTriplesTestCase(TestCase):

    maxDiff = None

    def test_find_undefined_obligatory_properties_empty(self):
        class_object = {"properties": {}}
        instance_data = {}
        computed = find_undefined_obligatory_properties(class_object, instance_data)
        expected = []
        self.assertEqual(computed, expected)

    def test_find_undefined_obligatory_properties_non_empty_but_defined_in_instance(self):
        class_object = {"properties": {"height": {"required": True}}}
        instance_data = {"height": 1.65}
        computed = find_undefined_obligatory_properties(class_object, instance_data)
        expected = []
        self.assertEqual(computed, expected)

    def test_find_undefined_obligatory_properties_not_defined_in_instance(self):
        class_object = {"properties": {"height": {"required": True}}}
        instance_data = {}
        computed = find_undefined_obligatory_properties(class_object, instance_data)
        expected = ["height"]
        self.assertEqual(computed, expected)

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_create_explicit_triples_undefined_property(self, mock_settings):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {"personpedia": "http://personpedia.com/"},
            "http://personpedia.com/occupation": "http://someurl/profession/writer",
        }
        class_object = mock_schema(
            {},
            id="http://personpedia.com/Person",
            context=instance_data['@context']
        )
        with self.assertRaises(InstanceError) as exception:
            create_explicit_triples(instance_uri, instance_data, class_object, None, None)
        expected_error_msg = [u"Inexistent property (http://personpedia.com/occupation) in the schema (http://personpedia.com/Person), used to create instance (http://personpedia.com/Person/OscarWilde)"]
        self.assertEqual(json.loads(str(exception.exception)), expected_error_msg)

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_create_explicit_triples_without_obligatory_properties(self, mock_settings):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
        }
        class_object = {
            u'id': "http://personpedia.com/Person",
            u'properties': {
                u'http://personpedia/full_name': {
                    'datatype': u'http://www.w3.org/2001/XMLSchema#string',
                    'description': u'Formal or informal name of something or someone',
                    'required': True,
                    'title': u'Full name',
                    'type': 'string'
                }
            }
        }

        with self.assertRaises(InstanceError) as exception:
            create_explicit_triples(instance_uri, instance_data, class_object, None, None)

        expected_error_msg = [u'The property (http://personpedia/full_name) is obligatory according to the definition of the class (http://personpedia.com/Person). A value must be provided for this field in order to create or edit (http://personpedia.com/Person/OscarWilde).']
        self.assertEqual(json.loads(str(exception.exception)), expected_error_msg)

    def test_create_explicit_triples_predicates_and_objects_are_full_uris(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        graph_uri = "http://personpedia.com/"
        instance_data = {
            "@context": {"personpedia": "http://personpedia.com/"},
            "http://personpedia.com/birthPlace": "http://placepedia.com/Dublin",
            "http://personpedia.com/gender": "http://personpedia.com/Male",
            "http://personpedia.com/wife": "http://personpedia.com/ConstanceLloyd"
        }
        class_object = mock_schema(
            {"personpedia:birthPlace": 'string_uri',
             "personpedia:gender": 'string_uri',
             "personpedia:wife": 'string_uri'},
            id="http://personpedia.com/Person",
            context=instance_data['@context']
        )
        response = create_explicit_triples(instance_uri, instance_data, class_object, graph_uri, {})
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/birthPlace>", "<http://placepedia.com/Dublin>"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/gender>", "<http://personpedia.com/Male>"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/wife>", "<http://personpedia.com/ConstanceLloyd>")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_are_uris_and_objects_are_literals(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        graph_uri = "http://personpedia.com/"
        instance_data = {
            "@context": {"personpedia": "http://personpedia.com/"},
            "http://personpedia.com/birthDate": u"16/10/1854",
            "http://personpedia.com/birthPlace": u"place:Dublin",
            "http://personpedia.com/occupation": u"writer",
        }
        class_object = mock_schema(
            {"http://personpedia.com/birthDate": 'string',
             "http://personpedia.com/birthPlace": 'string_uri',
             "http://personpedia.com/occupation": 'string'},
            id="http://personpedia.com/Person",
            context=instance_data['@context']
        )
        response = create_explicit_triples(instance_uri, instance_data, class_object, graph_uri, {})
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/birthDate>", '"16/10/1854"'),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/birthPlace>", "place:Dublin"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/occupation>", '"writer"')
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_objects_are_urls_as_strings(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        graph_uri = "http://personpedia.com/"
        instance_data = {
            "@context": {"personpedia": u"http://personpedia.com/"},
            "http://personpedia.com/occupation": u"http://someurl/profession/writer",
        }
        class_object = mock_schema({"personpedia:occupation": 'string'},
                                   id="http://personpedia.com/Person",
                                   context=instance_data['@context'])
        response = create_explicit_triples(instance_uri, instance_data, class_object, graph_uri, {})
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>",
             "<http://personpedia.com/occupation>",
             '"http://someurl/profession/writer"')
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_are_uris_and_one_object_is_literal_and_is_translated(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        graph_uri = "http://personpedia.com/"
        instance_data = {
            "@context": {"personpedia": u"http://personpedia.com/"},
            "http://personpedia.com/birthDate": u"16/10/1854",
            "http://personpedia.com/birthPlace": u"place:Dublin",
            "http://personpedia.com/occupation": u"'writer'@en",
        }
        class_object = mock_schema(
            {"http://personpedia.com/birthDate": u'string',
             "http://personpedia.com/birthPlace": u'string_uri',
             "http://personpedia.com/occupation": u'string'},
            id="http://personpedia.com/Person",
            context=instance_data['@context']
        )
        response = create_explicit_triples(instance_uri, instance_data, class_object, graph_uri, {})
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/birthDate>", '"16/10/1854"'),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/birthPlace>", "place:Dublin"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/occupation>", "'writer'@en")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_are_uris_and_one_object_is_list(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        graph_uri = "http://personpedia.com/"
        instance_data = {
            "@context": {"personpedia": u"http://personpedia.com/"},
            "http://www.w3.org/2000/01/rdf-schema#label": u"Oscar Wilde",
            "http://personpedia.com/gender": u"http://personpedia.com/Male",
            "http://personpedia.com/child": [u"http://personpedia.com/VyvyanHolland", u"http://personpedia.com/CyrilHolland"]
        }
        class_object = mock_schema(
            {"http://www.w3.org/2000/01/rdf-schema#label": 'string',
             "http://personpedia.com/gender": 'string_uri',
             "http://personpedia.com/child": 'array_string_uri'},
            id="http://personpedia.com/Person",
            context=instance_data['@context']
        )
        response = create_explicit_triples(instance_uri, instance_data, class_object, graph_uri, {})
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "<http://www.w3.org/2000/01/rdf-schema#label>", '"Oscar Wilde"'),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/gender>", "<http://personpedia.com/Male>"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/child>", "<http://personpedia.com/VyvyanHolland>"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/child>", "<http://personpedia.com/CyrilHolland>")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_create_explicit_triples_predicates_raises_exception_due_to_wrong_boolean_value(self, mock_settings):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {"personpedia": "http://personpedia.com/"},
            "http://personpedia.com/isAlive": "0",

        }
        class_object = mock_schema(
            {
                "http://personpedia.com/isAlive": "boolean",

            },
            id="http://personpedia.com/Person",
            context=instance_data['@context']
        )
        with self.assertRaises(InstanceError) as exception:
            create_explicit_triples(instance_uri, instance_data, class_object, None, None)
        excepted_error_msg = [u'Incorrect value for property (http://personpedia.com/isAlive). A (http://www.w3.org/2001/XMLSchema#boolean) was expected, but (0) was given.']
        self.assertEqual(json.loads(str(exception.exception)), excepted_error_msg)

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_create_explicit_triples_predicates_raises_exception_due_to_multiple_wrong_values(self, settings_mock):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {"personpedia": "http://personpedia.com/"},
            "http://personpedia.com/isAlive": u"http://personpedia.com/TheImportanceOfBeingEarnest",
            "http://personpedia.com/deathAge": u"Irish",
            "http://personpedia.com/hasNationality": 46,
            "http://personpedia.com/wroteBook": u"true",
        }
        class_object = mock_schema(
            {
                "http://personpedia.com/isAlive": "boolean",
                "http://personpedia.com/deathAge": "integer",
                "http://personpedia.com/hasNationality": "string",
                "http://personpedia.com/wroteBook": "string_uri"
            },
            id="http://personpedia.com/Person",
            context=instance_data['@context']
        )
        with self.assertRaises(InstanceError) as exception:
            create_explicit_triples(instance_uri, instance_data, class_object, None, None)

        expected_error_msg = [
            u"Incorrect value for property (http://personpedia.com/wroteBook). A (owl:ObjectProperty) was expected, but (true) was given.",
            u"Incorrect value for property (http://personpedia.com/hasNationality). A (http://www.w3.org/2001/XMLSchema#string) was expected, but (46) was given.",
            u"Incorrect value for property (http://personpedia.com/deathAge). A (http://www.w3.org/2001/XMLSchema#integer) was expected, but (Irish) was given.",
            u"Incorrect value for property (http://personpedia.com/isAlive). A (http://www.w3.org/2001/XMLSchema#boolean) was expected, but (http://personpedia.com/TheImportanceOfBeingEarnest) was given."]
        self.assertEqual(json.loads(str(exception.exception)), expected_error_msg)

    def test_unpack_tuples(self):
        instance_data = {
            "key1": "1a",
            "key2": ["2a", "2b"]
        }
        computed = unpack_tuples(instance_data)
        expected = [("key1", "1a"), ("key2", "2a"), ("key2", "2b")]
        self.assertEqual(sorted(computed), sorted(expected))
        self.assertEqual(len(instance_data), 1)
        self.assertEqual(instance_data["key1"], "1a")

    def test_create_implicit_triples(self):
        instance_uri = "http://instance"
        class_uri = "http://class"
        computed = create_implicit_triples(instance_uri, class_uri)
        expected = [("<http://instance>", "a", "<http://class>")]
        self.assertEqual(computed, expected)

    def test_join_triples_empty(self):
        triples = []
        computed = join_triples(triples)
        expected = ''
        self.assertEqual(computed, expected)

    def test_join_triples(self):
        triples = [
            ("<a>", "<b>", "<c>"),
            ("<d>", "<e>", "<f>"),
            ("<g>", "<h>", "<i>")
        ]
        computed = join_triples(triples)
        expected = '   <a> <b> <c> .\n   <d> <e> <f> .\n   <g> <h> <i> .'
        self.assertEqual(computed, expected)

    def test_join_prefixes_empty(self):
        prefixes = {}
        computed = join_prefixes(prefixes)
        expected = ''
        self.assertEqual(computed, expected)

    def test_join_prefixes(self):
        prefixes = {"base": "http://base.com", "upper": "http://upper.com"}
        computed = join_prefixes(prefixes)
        expected = 'PREFIX upper: <http://upper.com>\nPREFIX base: <http://base.com>'
        self.assertEqual(computed, expected)

    def test_join_prefixes_with_non_valid_field(self):
        prefixes = {"valid": "http://valid.com", "@language": "pt"}
        computed = join_prefixes(prefixes)
        expected = 'PREFIX valid: <http://valid.com>'
        self.assertEqual(computed, expected)

    def test_predicate_is_reserved_word(self):
        self.assertTrue(is_reserved_attribute("@context"))

    def test_predicate_begins_with_reserved_prefix(self):
        self.assertTrue(is_reserved_attribute("@xubiru"))
        self.assertTrue(is_reserved_attribute("$nissim"))
        self.assertTrue(is_reserved_attribute("_resource_id"))

    def test_predicate_is_not_reserved_attribute(self):
        self.assertFalse(is_reserved_attribute("bla"))

    def test_extract_instance_id(self):
        instance_uri = "http://my.domain/instance_id"
        instance_id = extract_instance_id(instance_uri)
        self.assertEqual(instance_id, "instance_id")

    def test_clean_up_attributes(self):
        expected_clean_instance_data = {
            'upper:fullName': u'Globoland (RJ)',
            'dct:isPartOf': 'base:UF_RJ',
            'rdf:type': 'place:City',
            'place:longitude': u'-43.407133',
            'upper:name': u'Globoland',
            'rdfs:comment': u"City of Globo's companies. Historically known as PROJAC.",
            'place:latitude': u'-22.958314',
            'place:partOfState': 'base:UF_RJ'
        }
        dirty_instance_data = {
            '_instance_prefix': 'http://semantica.globo.com/place/',
            '_base_url': 'http://localhost:5100/place/City/',
            '_resource_id': '3b62b2e1-d495-4e1f-be27-8ee9382ca46b',
            '@context': {'upper': 'http://semantica.globo.com/upper/',
                         'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                         'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                         'place': 'http://semantica.globo.com/place/',
                         'base': 'http://semantica.globo.com/base/',
                         'dbpedia': 'http://dbpedia.org/ontology/',
                         'dct': 'http://purl.org/dc/terms/',
                         'schema': 'http://schema.org/'},
            '@id': 'http://semantica.globo.com/place/City/3b62b2e1-d495-4e1f-be27-8ee9382ca46b',
            '@type': 'place:City',
        }
        dirty_instance_data.update(expected_clean_instance_data)
        cleaned_instance_data = clean_up_reserved_attributes(dirty_instance_data)
        self.assertEqual(cleaned_instance_data, expected_clean_instance_data)


class LanguageSupportTestCase(TestCase):

    def test_language_tag_empty(self):
        query_params = {"a": 1}
        (response_params, language_tag) = add_language_support(query_params, "label")
        self.assertEqual(response_params, query_params)

    def test_language_supported_added(self):
        expected_filter = 'FILTER(langMatches(lang(?label), "en") OR langMatches(lang(?label), ""))'

        query_params = {"lang": "en"}
        (response_params, language_tag) = add_language_support(query_params, "label")
        self.assertIn(expected_filter, response_params["lang_filter_label"])
        self.assertEquals("@en", language_tag)


class NormalizeTerm(TestCase):

    def test_normalize_term_expanded_uri(self):
        term = "http://expanded.uri"
        computed = normalize_term(term)
        expected = "<http://expanded.uri>"
        self.assertEqual(computed, expected)

    def test_normalize_term_short_uri(self):
        term = "short:uri"
        computed = normalize_term(term)
        expected = "short:uri"
        self.assertEqual(computed, expected)

    def test_normalize_term_translated_literal(self):
        term = "Some string"
        computed = normalize_term(term)
        expected = '"Some string"'
        self.assertEqual(computed, expected)

    def test_normalize_term_translated_literal_translated(self):
        term = "Some string"
        computed = normalize_term(term, "pt")
        expected = '"Some string"@pt'
        self.assertEqual(computed, expected)

    def test_normalize_term_variable(self):
        term = "?variable"
        computed = normalize_term(term, "pt")
        expected = "?variable"
        self.assertEqual(computed, expected)

    def test_is_literal_given_a_variable_return_false(self):
        response = is_literal("?a_variable")
        self.assertFalse(response)

    def test_is_literal_given_a_url_return_false(self):
        response = is_literal("http://xubiru.com")
        self.assertFalse(response)

    def test_is_literal_given_a_compressed_url_return_false(self):
        response = is_literal("upper:something")
        self.assertFalse(response)

    def test_is_literal_given_a_literal_return_true(self):
        response = is_literal("literal")
        self.assertTrue(response)


class SuperPropertiesTestCase(TestCase):

    def test_get_super_properties(self):
        sample_bindings = [
            {
                'predicate': {'value': 'son'},
                'super_property': {'value': 'father'}
            },
            {
                'predicate': {'value': 'father'}
            },
            {
                'predicate': {'value': 'grandfather'}
            }
        ]

        computed = get_super_properties(sample_bindings)
        expected = {'father': 'son'}
        self.assertEqual(computed, expected)

    def test_get_multiple_super_properties(self):
        sample_bindings = [
            {
                'predicate': {'value': 'son'},
                'super_property': {'value': 'father'}
            },
            {
                'predicate': {'value': 'father'},
                'super_property': {'value': 'grandfather'}
            },
            {
                'predicate': {'value': 'grandfather'}
            }
        ]
        computed = get_super_properties(sample_bindings)
        expected = {'father': 'son', 'grandfather': 'father'}
        self.assertEqual(computed, expected)


class POTestCase(TestCase):

    def test_extract_po_tuples_p(self):
        params = {"p": "some:predicate"}
        response = extract_po_tuples(params)
        expected = [('some:predicate', '?o', '')]
        self.assertEqual(response, expected)

    def test_extract_po_tuples_o(self):
        params = {"o": "Nina"}
        response = extract_po_tuples(params)
        expected = [('?p', 'Nina', '')]
        self.assertEqual(response, expected)

    def test_extract_po_tuples_p_o(self):
        params = {"o": "Nina", "p": "canidae:hasDog"}
        response = extract_po_tuples(params)
        expected = [('canidae:hasDog', 'Nina', '')]
        self.assertEqual(response, expected)

    def test_extract_po_tuples_o_o1_o2_o3(self):
        params = {"o": "0", "o1": "1", "o2": "2", "o3": "?o3"}
        response = extract_po_tuples(params)
        expected = [('?p', '0', ''), ('?p1', '1', '1'), ('?p2', '2', '2'), ('?p3', '?o3', '3')]
        self.assertEqual(response, expected)

    def test_extract_po_tuples_complex_case(self):
        params = {"o": "0", "o1": "1", "p2": "predicate2", "p4": "predicate4", "p5": "predicate5", "o5": "object5"}
        response = extract_po_tuples(params)
        expected = [('?p', '0', ''), ('?p1', '1', '1'), ('predicate2', '?o2', '2'), ('predicate4', '?o4', '4'), ('predicate5', 'object5', '5')]
        self.assertEqual(response, expected)

    def test_extract_po_invalid_params(self):
        params = {}
        response = extract_po_tuples(params)
        expected = []
        self.assertEqual(response, expected)

    def test_pattern_p(self):
        self.assertTrue(PATTERN_P.match("p"))
        self.assertTrue(PATTERN_P.match("p1"))
        self.assertTrue(PATTERN_P.match("p200"))
        self.assertFalse(PATTERN_P.match("page"))
        self.assertFalse(PATTERN_P.match("op3"))

    def test_pattern_o(self):
        self.assertTrue(PATTERN_O.match("o"))
        self.assertTrue(PATTERN_O.match("o1"))
        self.assertTrue(PATTERN_O.match("o200"))
        self.assertFalse(PATTERN_O.match("other_key"))
        self.assertFalse(PATTERN_O.match("no"))

    def test_escape_quotes(self):
        object_value = u'Aos 15 anos, lan\xe7ou o 1\xba disco com o sucesso "Musa do ver\xe3o"'
        expected_object_value = u'Aos 15 anos, lan\xe7ou o 1\xba disco com o sucesso \\"Musa do ver\xe3o\\"'
        self.assertEqual(expected_object_value, escape_quotes(object_value))

    def test_escape_quotes_not_string(self):
        object_value = 15
        expected = 15
        computed = escape_quotes(object_value)
        self.assertEqual(computed, expected)


class GetPredicatedDatatypeTestCase(TestCase):

    def setUp(self):
        self.class_object = {
            "properties": {
                "http://www.w3.org/2000/01/rdf-schema#label": {
                    "datatype": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral",
                },
                "http://example.onto/description": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#string"
                },
                "http://example.onto/partOfCountry": {
                    "range": {}
                }
            }
        }

    def test_get_predicate_datatype_object_property(self):
        result = get_predicate_datatype(self.class_object, "http://example.onto/partOfCountry")
        self.assertIsNone(result)


class EncodeBooleanTestCase(TestCase):

    def test_encode_true(self):
        result = encode_boolean(True)
        self.assertEqual(result, "true")

    def test_encode_false(self):
        result = encode_boolean(False)
        self.assertEqual(result, "false")

    def test_encode_other_value(self):
        self.assertRaises(InstanceError, encode_boolean, "aaa")


class DecodeBooleanTestCase(TestCase):

    def test_decode_1(self):
        result = decode_boolean("1")
        self.assertEqual(result, True)

    def test_decode_0(self):
        result = decode_boolean("0")
        self.assertEqual(result, False)

    def test_decode_other_value(self):
        self.assertRaises(InstanceError, decode_boolean, "aaa")


class BindingsToDictTestCase(TestCase):

    maxDiff = None

    def test_convert_valid_input(self):
        key_name = 'predicate'
        bindings = {
            u'head': {
                u'link': [],
                u'vars': [u'predicate', u'predicate_graph', u'predicate_comment', u'type', u'range', u'title', u'range_graph', u'range_label', u'super_property', u'domain_class']
            },
            u'results': {
                u'distinct': False,
                u'bindings': [{
                    u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                    u'range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'}
                }]
            }
        }

        expected = {
            u'http://www.w3.org/2000/01/rdf-schema#label': {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'}
            }
        }
        computed = bindings_to_dict(key_name, bindings)
        self.assertEqual(computed, expected)

    def test_convert_invalid_input(self):
        key_name = 'inexistent'
        bindings = {
            u'head': {
                u'link': [],
                u'vars': [u'predicate', u'predicate_graph', u'predicate_comment', u'type', u'range', u'title', u'range_graph', u'range_label', u'super_property', u'domain_class']},
            u'results': {
                u'distinct': False,
                u'bindings': [
                    {
                        u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                        u'range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'}
                    }]
            }
        }

        expected = {}
        computed = bindings_to_dict(key_name, bindings)
        self.assertEqual(computed, expected)


class SparqlfyTestCase(TestCase):

    def test_generic_sparqlfy(self):
        response = generic_sparqlfy("dummy")
        expected = '"dummy"'
        self.assertEqual(response, expected)

    def test_generic_sparqlfy_with_multiline_string(self):
        response = generic_sparqlfy("dummy\nmultiline")
        expected = '"""dummy\nmultiline"""'
        self.assertEqual(response, expected)

    def test_is_multiline_string(self):
        self.assertTrue(is_multiline_string("multi\nline\r\nstring"))

    def test_is_not_multiline_string(self):
        self.assertFalse(is_multiline_string("not multi line string"))

    def test_sparqlfy_string_without_lang(self):
        response = sparqlfy_string("No i18n")
        expected = '"No i18n"'
        self.assertEqual(response, expected)

    def test_sparqlfy_string_with_lang(self):
        response = sparqlfy_string("'English string'@en")
        expected = "'English string'@en"
        self.assertEqual(response, expected)

    def test_sparqlfy_boolean_true(self):
        response = sparqlfy_boolean(True, "http://www.w3.org/2001/XMLSchema#boolean")
        expected = '"true"^^<http://www.w3.org/2001/XMLSchema#boolean>'
        self.assertEqual(response, expected)

    def test_sparqlfy_boolean_false(self):
        response = sparqlfy_boolean(False, "http://www.w3.org/2001/XMLSchema#boolean")
        expected = '"false"^^<http://www.w3.org/2001/XMLSchema#boolean>'
        self.assertEqual(response, expected)

    def test_sparqlfy_boolean_1(self):
        response = sparqlfy_boolean(1, "http://www.w3.org/2001/XMLSchema#boolean")
        expected = '"true"^^<http://www.w3.org/2001/XMLSchema#boolean>'
        self.assertEqual(response, expected)

    def test_sparqlfy_object(self):
        response = sparqlfy_object("http://some/object")
        expected = "<http://some/object>"
        self.assertEqual(response, expected)

    def test_sparqlfy_object_compressed(self):
        response = sparqlfy_object("xsd:object")
        expected = "xsd:object"
        self.assertEqual(response, expected)

    def test_sparqlfy_object_raises_exception(self):
        with self.assertRaises(InstanceError) as exception:
            sparqlfy_object("non_uri")
        expected_msg = "(non_uri) is not a URI or cURI"
        self.assertEqual(str(exception.exception), expected_msg)

    def test_sparqlfy_object_dict(self):
        response = sparqlfy_object({"@id": "http://some/object"})
        expected = "<http://some/object>"
        self.assertEqual(response, expected)

    def test_sparqlfy_with_casting(self):
        response = sparqlfy_with_casting("value", "http://some/cast")
        expected = u'"value"^^<http://some/cast>'
        self.assertEqual(response, expected)

    def test_sparqlfy_with_casting_compressed(self):
        response = sparqlfy_with_casting("value", "http://some/cast")
        expected = u'"value"^^<http://some/cast>'
        self.assertEqual(response, expected)

    def test_sparqlfy_xmlliteral(self):
        response = sparqlfy("some literal", "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral")
        expected = '"some literal"'
        self.assertEqual(response, expected)

    def test_sparqlfy_xmlstring(self):
        response = sparqlfy('"some string"@en', "http://www.w3.org/2001/XMLSchema#string")
        expected = '"some string"@en'
        self.assertEqual(response, expected)

    def test_sparqlfy_anyuri(self):
        response = sparqlfy('http://any.uri', "http://www.w3.org/2001/XMLSchema#string")
        expected = '"http://any.uri"'
        self.assertEqual(response, expected)

    def test_sparqlfy_boolean(self):
        response = sparqlfy(False, "http://www.w3.org/2001/XMLSchema#boolean")
        expected = '"false"^^<http://www.w3.org/2001/XMLSchema#boolean>'
        self.assertEqual(response, expected)

    def test_sparqlfy_integer(self):
        response = sparqlfy(2, "http://www.w3.org/2001/XMLSchema#integer")
        expected = '"2"^^<http://www.w3.org/2001/XMLSchema#integer>'
        self.assertEqual(response, expected)

    def test_is_instance_unicode_true(self):
        value = u"Some random unicode"
        _type = "http://www.w3.org/2001/XMLSchema#string"
        response = is_instance(value, _type)
        self.assertTrue(response)

    def test_is_instance_string_true(self):
        value = u"Some random string"
        _type = "http://www.w3.org/2001/XMLSchema#string"
        response = is_instance(value, _type)
        self.assertTrue(response)

    def test_is_instance_integer_true(self):
        value = 1
        _type = "http://www.w3.org/2001/XMLSchema#int"
        response = is_instance(value, _type)
        self.assertTrue(response)

    def test_is_instance_integer_false(self):
        value = 1.1
        _type = "http://www.w3.org/2001/XMLSchema#int"
        response = is_instance(value, _type)
        self.assertFalse(response)

    def test_is_instance_expanded_string_true(self):
        value = u"abc"
        _type = "http://www.w3.org/2001/XMLSchema#string"
        response = is_instance(value, _type)
        self.assertTrue(response)

    @patch("brainiak.utils.sparql.logger.info")
    @patch("brainiak.utils.sparql.logger", logging.getLogger("test"))
    def test_is_instance_undefined_type(self, mock_info):
        value = 1
        _type = "http://undefined/property"
        response = is_instance(value, _type)
        self.assertTrue(response)
        msg = u"Could not validate input due to unknown property type: <http://undefined/property>"
        mock_info.assert_called_with(msg)

    def test_is_instance_datetime_without_zone(self):
        value = "2002-05-30T09:00:00"
        _type = "http://www.w3.org/2001/XMLSchema#dateTime"
        response = is_instance(value, _type)
        self.assertTrue(response)

    def test_is_instance_datetime_in_utc_time(self):
        value = "2002-05-30T09:30:10Z"
        _type = "http://www.w3.org/2001/XMLSchema#dateTime"
        response = is_instance(value, _type)
        self.assertTrue(response)

    def test_is_instance_datetime_with_utc_offset(self):
        value = "2002-05-30T09:30:10-06:00"
        _type = "http://www.w3.org/2001/XMLSchema#dateTime"
        response = is_instance(value, _type)
        self.assertTrue(response)

    def test_is_instance_datetime_with_invalid_utc_offset(self):
        value = "2002-05-30T09:30:10-AB:CD"
        _type = "http://www.w3.org/2001/XMLSchema#dateTime"
        response = is_instance(value, _type)
        self.assertFalse(response)

    def test_is_instance_datetime_with_miliseconds(self):
        value = "2014-01-09T18:20:25.848436"
        _type = "http://www.w3.org/2001/XMLSchema#dateTime"
        response = is_instance(value, _type)
        self.assertTrue(response)

    def test_is_instance_with_invalid_offset(self):
        value = "abc"
        _type = "http://www.w3.org/2001/XMLSchema#dateTime"
        response = is_instance(value, _type)
        self.assertFalse(response)


class ValidateValueUniquenessTestCase(TestCase):

    def test_property_must_map_a_unique_value_is_true(self):
        class_object = {
            "properties": {
                "some_property": {"unique_value": True}
            }
        }
        computed = property_must_map_a_unique_value(class_object, "some_property")
        self.assertTrue(computed)

    def test_property_must_map_a_unique_value_is_false(self):
        class_object = {
            "properties": {
                "some_property": {}
            }
        }
        computed = property_must_map_a_unique_value(class_object, "some_property")
        self.assertFalse(computed)

    @patch("brainiak.utils.sparql.triplestore.query_sparql")
    @patch("brainiak.utils.sparql.is_result_true", return_value=False)
    def test_property_with_unique_value(self, mock_is_result_true, mock_query_sparql):
        class QueryParams:

            triplestore_config = triplestore_config
        object_value = "any"
        predicate_uri = "http://example.onto/description"
        instance_uri = "http://example.onto/York"
        graph_uri = "http://example.onto/"
        class_object = {
            "properties": {
                "http://example.onto/description": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#string",
                    "unique_value": True
                }
            },
            "id": "http://example.onto/City"
        }
        is_value_already_used(instance_uri, object_value, predicate_uri,
                              class_object, graph_uri, QueryParams())

    @patch("brainiak.utils.sparql.triplestore.query_sparql")
    @patch("brainiak.utils.sparql.is_result_true", return_value=False)
    def test_property_with_duplicated_value_raises_exception(self, mock_is_result_true, mock_query_sparql):
        class QueryParams:

            triplestore_config = triplestore_config

        object_value = "any"
        predicate_uri = "http://example.onto/description"
        instance_uri = "http://example.onto/York"
        graph_uri = "http://example.onto/"
        class_object = {
            "properties": {
                "http://example.onto/description": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#string",
                    "unique_value": True
                }
            },
            "id": "http://example.onto/City"
        }
        response = is_value_already_used(instance_uri, object_value, predicate_uri, class_object, graph_uri, QueryParams())
        self.assertFalse(response)


class RdfsLabelValidationTestCase(TestCase):

    def test_exists_label_property(self):
        instance_data = {
            u'rdfs:label': "a label",
            u"a:property": "a value"
        }
        self.assertTrue(are_there_label_properties_in(instance_data))

    def test_does_not_exist_label_property(self):
        instance_data = {
            u"a:property": "a value"
        }
        self.assertFalse(are_there_label_properties_in(instance_data))
