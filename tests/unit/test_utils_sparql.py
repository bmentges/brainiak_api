import unittest
import uuid

from brainiak.utils.sparql import compress_keys_and_values, create_instance_uri, get_one_value, filter_values, has_lang, is_result_empty, \
    some_triples_deleted, UnexpectedResultException
from brainiak.prefixes import MemorizeContext


class ResultHandlerTestCase(unittest.TestCase):

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


class GetOneTestCase(unittest.TestCase):

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


class SomeTriplesDeletedTestCase(unittest.TestCase):

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


class LiteralLangTestCase(unittest.TestCase):

    def test_has_lang_literal_true(self):
        self.assertEqual(has_lang("'i18n'@en"), True)

    def test_has_lang_literal_false(self):
        self.assertEqual(has_lang("not i18n"), False)
