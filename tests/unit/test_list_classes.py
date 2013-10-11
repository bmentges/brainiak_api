# -*- coding: utf-8 -*-
import unittest

from mock import patch

from brainiak import settings

from brainiak.context import get_context
from brainiak.utils.params import ParamDict, LIST_PARAMS
from tests.mocks import MockHandler


class GetContextTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.original_add_language_support = get_context.add_language_support
        get_context.add_language_support = lambda query, lang: (query, lang)

        self.original_query_count_classes = get_context.query_count_classes
        get_context.query_count_classes = lambda x: 1

        self.original_query_classes_list = get_context.query_classes_list
        get_context.query_classes_list = lambda x: None

        self.original_assemble_list_json = get_context.assemble_list_json
        self.original_query_classes_list = get_context.query_classes_list

    def tearDown(self):
        get_context.add_language_support = self.original_add_language_support
        get_context.query_count_classes = self.original_query_count_classes
        get_context.query_classes_list = self.original_query_classes_list
        get_context.assemble_list_json = self.original_assemble_list_json
        get_context.query_classes_list = self.original_query_classes_list

    @patch("brainiak.context.get_context.graph_exists", return_value=True)
    def test_list_classes_with_no_result(self, mocked_graph_exists):
        get_context.get_one_value = lambda x, y: "0"
        handler = MockHandler(page="1")
        params = ParamDict(handler, context_name="context_name", class_name="class_name", **LIST_PARAMS)
        result = get_context.list_classes(params)
        self.assertEqual(result["items"], [])

    @patch("brainiak.context.get_context.graph_exists", return_value=True)
    def test_list_classes_return_result(self, mocked_graph_exists):
        get_context.get_one_value = lambda x, y: "1"
        get_context.assemble_list_json = lambda x, y: "expected result"
        get_context.query_classes_list = lambda x: {'results': {'bindings': 'do not remove this'}}
        handler = MockHandler(page="1")
        params = ParamDict(handler, context_name="context_name", class_name="class_name", **LIST_PARAMS)
        expected = get_context.list_classes(params)
        self.assertEqual(expected, "expected result")

    def test_assemble_list_json_with_class_prefix(self):
        handler = MockHandler(uri="http://poke.oioi/company/")
        params = ParamDict(handler, context_name="company", **LIST_PARAMS)
        item = {
            u'class': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/Company'},
            u'label': {u'type': u'literal', u'value': u'Company'}
        }
        query_result_dict = {'results': {'bindings': [item]}}
        computed = get_context.assemble_list_json(params, query_result_dict)

        expected_context = {'@language': settings.DEFAULT_LANG}
        expected_items = [
            {
                '@id': u'http://dbpedia.org/ontology/Company',
                'resource_id': u'Company',
                'title': u'Company',
                'class_prefix': u'http://dbpedia.org/ontology/'
            }
        ]

        self.assertEqual(computed['@context'], expected_context)
        self.assertEqual(computed['items'], expected_items)
        self.assertEqual("http://poke.oioi/company", computed['_base_url'])
