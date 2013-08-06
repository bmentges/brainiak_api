from unittest import TestCase

from mock import patch
from tornado.web import HTTPError

from brainiak.prefixes import ROOT_CONTEXT
from brainiak.utils.resources import decorate_with_class_prefix, decorate_with_resource_id, compress_duplicated_ids, LazyObject, validate_pagination_or_raise_404


class TestLazyObject(TestCase):

    def test_lazy_object(self):
        def factory():
            return [1]
        lazy = LazyObject(factory)
        lazy.append(2)
        self.assertEqual(1, lazy.pop())


class TestValidatePagination(TestCase):

    @patch('brainiak.utils.resources.valid_pagination', return_value=False)
    def test_validatePagination_raises(self, mock):
        self.assertRaises(HTTPError, validate_pagination_or_raise_404, params={'page': 0, 'per_page': 3}, total_items=10)


class TestCaseListInstanceResource(TestCase):

    def test_decorate_with_resource_id_successfully(self):
        expected_result = [{u"@id": u"http://a/b", u"resource_id": u"b"}]
        target = [{u"@id": u"http://a/b"}]
        decorate_with_resource_id(target)
        self.assertEqual(expected_result, target)

    def test_decorate_with_resource_id_successfully(self):
        expected_result = [{u"@id": u"http://a/b/", u"resource_id": u"b"}]
        target = [{u"@id": u"http://a/b/"}]
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
