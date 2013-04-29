# -*- coding: utf-8 -*-
import unittest
from brainiak.context import list_resource
from brainiak.utils.params import ParamDict
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

        self.original_get_one_value = list_resource.get_one_value

    def tearDown(self):
        list_resource.add_language_support = self.original_add_language_support
        list_resource.query_count_classes = self.original_query_count_classes
        list_resource.query_classes_list = self.original_query_classes_list
        list_resource.get_one_value = self.original_get_one_value
        list_resource.assemble_list_json = self.original_assemble_list_json

    def test_list_classes_return_None(self):
        list_resource.get_one_value = lambda x, y: "0"

        handler = MockHandler()
        params = ParamDict(handler, context_name="context_name", class_name="class_name")
        expected = list_resource.list_classes(params)
        self.assertEqual(expected, None)

    def test_list_classes_return_something(self):
        list_resource.get_one_value = lambda x, y: "1"
        list_resource.assemble_list_json = lambda x, y, z: "expected result"

        handler = MockHandler()
        params = ParamDict(handler, context_name="context_name", class_name="class_name")
        expected = list_resource.list_classes(params)
        self.assertEqual(expected, "expected result")
