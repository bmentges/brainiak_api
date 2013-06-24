# -*- coding: utf-8 -*-
import unittest
from brainiak import settings

from brainiak.context import list_resource
from brainiak.utils.params import ParamDict, LIST_PARAMS
from tests.mocks import MockHandler


class GetContextTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.original_add_language_support = list_resource.add_language_support
        list_resource.add_language_support = lambda query, lang: (query, lang)

        self.original_query_count_classes = list_resource.query_count_classes
        list_resource.query_count_classes = lambda x: 1

        self.original_query_classes_list = list_resource.query_classes_list
        list_resource.query_classes_list = lambda x: None

        self.original_assemble_list_json = list_resource.assemble_list_json
        self.original_query_classes_list = list_resource.query_classes_list

    def tearDown(self):
        list_resource.add_language_support = self.original_add_language_support
        list_resource.query_count_classes = self.original_query_count_classes
        list_resource.query_classes_list = self.original_query_classes_list
        list_resource.assemble_list_json = self.original_assemble_list_json
        list_resource.query_classes_list = self.original_query_classes_list

    def test_list_classes_with_no_result(self):
        list_resource.get_one_value = lambda x, y: "0"
        handler = MockHandler(page="1")
        params = ParamDict(handler, context_name="context_name", class_name="class_name", **LIST_PARAMS)
        result = list_resource.list_classes(params)
        self.assertEqual(result, None)

    def test_list_classes_return_result(self):
        list_resource.get_one_value = lambda x, y: "1"
        list_resource.assemble_list_json = lambda x, y: "expected result"
        list_resource.query_classes_list = lambda x: {'results': {'bindings': 'do not remove this'}}
        handler = MockHandler(page="1")
        params = ParamDict(handler, context_name="context_name", class_name="class_name", **LIST_PARAMS)
        expected = list_resource.list_classes(params)
        self.assertEqual(expected, "expected result")

    def test_assemble_list_json_with_class_prefix(self):
        handler = MockHandler(uri="http://poke.oioi/company/")
        params = ParamDict(handler, context_name="company", **LIST_PARAMS)
        item = {
            u'class': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/Company'},
            u'label': {u'type': u'literal', u'value': u'Company'}
        }
        query_result_dict = {'results': {'bindings': [item]}}
        computed = list_resource.assemble_list_json(params, query_result_dict)

        expected_context = {
            '@language': settings.DEFAULT_LANG,
            'dbpedia': 'http://dbpedia.org/ontology/'
        }
        expected_items = [
            {
                '@id': 'dbpedia:Company',
                'resource_id': 'Company',
                'title': u'Company',
                'class_prefix': 'dbpedia'
            }
        ]

        self.assertEqual(computed['@context'], expected_context)
        self.assertEqual(computed['items'], expected_items)

        self_link = {
            'href': 'http://poke.oioi/company/',
            'method': 'GET',
            'rel': 'self',
        }
        instances_link = {
            'href': 'http://poke.oioi/company/{resource_id}?class_prefix={class_prefix}',
            'method': 'GET',
            'rel': 'instances'
        }
        collection_link = {
            'href': 'http://poke.oioi/company/{resource_id}?class_prefix={class_prefix}',
            'method': 'GET',
            'rel': 'collection'
        }
        self.assertIn(self_link, computed['links'])
        self.assertIn(collection_link, computed['links'])
        self.assertIn(instances_link, computed['links'])
