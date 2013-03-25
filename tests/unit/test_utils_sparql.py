import unittest
import uuid

from brainiak.utils.sparql import compress_keys_and_values, create_instance_uri, \
    get_one_value, filter_values, has_lang, is_result_empty, \
    some_triples_deleted, UnexpectedResultException, is_result_true, \
    create_explicit_triples, unpack_tuples, create_implicit_triples, join_prefixes, \
    join_triples
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


class IsResponseSuccessfulTestCase(unittest.TestCase):

    def test_is_response_successful_true(self):
        msg = "Insert into <http://semantica.globo.com/sample-place/>, 7 (or less) triples -- done"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertTrue(is_response_successful(fake_response))

    def test_is_response_successful_false_with_0_tuples(self):
        msg = "Insert into <http://semantica.globo.com/sample-place/>, 0 (or less) triples -- done"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertFalse(is_response_successful(fake_response))

    def test_is_response_successful_false_with_different_message(self):
        msg = "Failed"
        fake_response = {'results': {'bindings': [{'callret-0': {'value': msg}}]}}
        self.assertFalse(is_response_successful(fake_response))

    def test_is_response_successful_false_with_no_response(self):
        self.assertFalse(is_response_successful(None))


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


class IsResultTrueTestCase(unittest.TestCase):

    def test_is_result_true(self):
        result_dict = {"head": {"link": []}, "boolean": True}
        self.assertTrue(is_result_true(result_dict))

    def test_is_result_false(self):
        result_dict = {"head": {"link": []}, "boolean": False}
        self.assertFalse(is_result_true(result_dict))

    def test_is_result_false_boolean_not_in_dict(self):
        result_dict = {"head": {"link": [], "vars": ["callret-0"]}, "results": {"distinct": False, "ordered": True, "bindings": [{"callret-0": {"type": "literal", "value": "Unknown message"}}]}}
        self.assertFalse(is_result_true(result_dict))


class CreateExplicitTriples(unittest.TestCase):

    def test_create_explicit_triples_all_predicates_and_objects_are_compressed_uris(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {"personpedia": "http://personpedia.com"},
            "personpedia:birthPlace": "place:Dublin",
            "personpedia:gender": "personpedia:Male",
            "personpedia:wife": "personpedia:ConstanceLloyd"
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthPlace", "place:Dublin"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:gender", "personpedia:Male"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:wife", "personpedia:ConstanceLloyd")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_and_objects_are_full_uris(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {},
            "http://personpedia.com/birthPlace": "http://placepedia.com/Dublin",
            "http://personpedia.com/gender": "http://personpedia.com/Male",
            "http://personpedia.com/wife": "http://personpedia.com/ConstanceLloyd"
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/birthPlace>", "<http://placepedia.com/Dublin>"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/gender>", "<http://personpedia.com/Male>"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/wife>", "<http://personpedia.com/ConstanceLloyd>")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_are_uris_and_objects_are_literals(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {},
            "personpedia:birthDate": "16/10/1854",
            "personpedia:birthPlace": "place:Dublin",
            "personpedia:occupation": "writer",
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthDate", '"16/10/1854"'),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthPlace", "place:Dublin"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:occupation", '"writer"')
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_are_uris_and_one_object_is_literal_and_is_translated(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {},
            "personpedia:birthDate": "16/10/1854",
            "personpedia:birthPlace": "place:Dublin",
            "personpedia:occupation": "'writer'@en",
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthDate", '"16/10/1854"'),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthPlace", "place:Dublin"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:occupation", "'writer'@en")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_are_uris_and_one_object_is_list(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {"personpedia": "http://personpedia.com"},
            "rdfs:label": "Oscar Wilde",
            "personpedia:gender": "personpedia:Male",
            "personpedia:child": ["personpedia:VyvyanHolland", "personpedia:CyrilHolland"]
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "rdfs:label", '"Oscar Wilde"'),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:gender", "personpedia:Male"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:child", "personpedia:VyvyanHolland"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:child", "personpedia:CyrilHolland")
        ]
        self.assertEqual(sorted(response), sorted(expected))

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
