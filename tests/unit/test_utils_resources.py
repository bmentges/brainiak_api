from unittest import TestCase

from mock import patch, MagicMock

from brainiak.prefixes import ROOT_CONTEXT
from brainiak.utils.resources import decorate_with_class_prefix, decorate_with_resource_id, compress_duplicated_ids, LazyObject, calculate_offset, \
    build_resource_url
from brainiak.utils.params import ParamDict

from tests.mocks import MockHandler


class TestLazyObject(TestCase):

    def test_lazy_object(self):
        def factory():
            return [1]
        lazy = LazyObject(factory)
        lazy.append(2)
        self.assertEqual(1, lazy.pop())


class TestCaseListInstanceResource(TestCase):

    def test_decorate_with_resource_id_successfully(self):
        expected_result = [{u"@id": u"http://a/b", u"resource_id": u"b"}]
        target = [{u"@id": u"http://a/b"}]
        decorate_with_resource_id(target)
        self.assertEqual(expected_result, target)

    def test_decorate_with_missing_resource_id(self):
        target = [{u"id": u"http://a/b"}]
        self.assertRaises(TypeError, decorate_with_resource_id, target)

    def test_decorate_with_root_context(self):
        target = [{u"@id": u"http://a/b", u"title": ROOT_CONTEXT}]
        decorate_with_resource_id(target)
        self.assertEqual(target[0]['resource_id'], u'')


class ResourceUtilsTestCase(TestCase):

    def test_build_resource_url_with_params(self):
        computed_url = build_resource_url(
            'http',
            'localhost:5100',
            '/g1/Materia?class_uri=g1:Materia',
            '092bb93a-9e0b-4e66-905b-64d0fcb86edc',
            'class_uri=g1:Materia')
        self.assertEqual(computed_url, u'http://localhost:5100/g1/Materia/092bb93a-9e0b-4e66-905b-64d0fcb86edc?class_uri=g1:Materia')

    def test_decorate_with_resource_id_with_single_dict(self):
        list_of_dicts = [{"@id": "http://a/b/c"}]
        decorate_with_resource_id(list_of_dicts)
        self.assertIn('resource_id', list_of_dicts[0])
        self.assertEquals(list_of_dicts[0].get('resource_id'), "c")

    def test_decorate_with_resource_id_with_multiple_dicts(self):
        list_of_dicts = [{"@id": "http://a/b/c"}, {"@id": "https://x/y/z"}]
        decorate_with_resource_id(list_of_dicts)
        self.assertEquals(list_of_dicts[0].get('resource_id'), "c")
        self.assertEquals(list_of_dicts[1].get('resource_id'), "z")

    def test_decorate_with_resource_id_with_curie(self):
        list_of_dicts = [{"@id": "person:Person"}]
        decorate_with_resource_id(list_of_dicts)
        self.assertEquals(list_of_dicts[0].get('resource_id'), "Person")

    def test_compress_duplicated_ids(self):
        input_dict = [
            {"@id": "person:Person", "title": "Pessoa"},
            {"@id": "person:Person", "title": "Person"},
            {"@id": "person:Gender", "title": "Gender"}
        ]
        expected_dict = [
            {"@id": "person:Person", "title": ["Pessoa", "Person"]},
            {"@id": "person:Gender", "title": "Gender"}
        ]
        result = compress_duplicated_ids(input_dict)
        self.assertItemsEqual(expected_dict, result)

    def test_compress_duplicated_ids_with_missing_key(self):
        input_dict = [
            {"@id": "person:Person", "title": "Pessoa"},
            {"@id": "person:Person", "title": "Person"},
            {"title": "This is missing @id, should raise TypeError"}
        ]
        self.assertRaises(TypeError, compress_duplicated_ids, input_dict)

    def test_decorate_with_class_prefix(self):
        list_of_dicts = [
            {"@id": "dbpedia:AnyClass"}
        ]
        decorate_with_class_prefix(list_of_dicts)
        expected = [
            {
                "@id": "dbpedia:AnyClass",
                "class_prefix": "dbpedia"}
        ]
        self.assertEqual(list_of_dicts, expected)

    def test_decorate_with_class_prefix_full_url(self):
        list_of_dicts = [
            {"@id": "http://xubiru/AnyClass"}
        ]
        decorate_with_class_prefix(list_of_dicts)
        expected = [
            {
                "@id": "http://xubiru/AnyClass",
                "class_prefix": "http://xubiru/"}
        ]
        self.assertEqual(list_of_dicts, expected)


class OffsetTestCase(TestCase):

    @patch("brainiak.utils.resources.settings", DEFAULT_PAGE=2, DEFAULT_PER_PAGE=10)
    def test_offset_defaults(self, mocked_settings):
        handler = MockHandler()
        params = ParamDict(handler)
        response = calculate_offset(params)
        expected = '20'
        self.assertEqual(expected, response)

    @patch("brainiak.utils.resources.settings", DEFAULT_PAGE=2, DEFAULT_PER_PAGE=10)
    def test_offset_calculation(self, mocked_settings):
        handler = MockHandler()
        params = ParamDict(handler, page=3, per_page=5)
        response = calculate_offset(params)
        expected = '15'
        self.assertEqual(expected, response)
