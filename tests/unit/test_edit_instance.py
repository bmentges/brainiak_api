# -*- coding: utf-8 -*-

import unittest
from mock import patch
from tornado.web import HTTPError
from brainiak.instance import edit_instance
from brainiak.utils.params import ParamDict
from tests.mocks import MockHandler, mock_schema


class TestCaseInstanceResource(unittest.TestCase):

    def setUp(self):
        self.original_instance_exists = edit_instance.instance_exists
        edit_instance.instance_exists = lambda x: True

    def tearDown(self):
        edit_instance.instance_exists = self.original_instance_exists

    def test_edit_instance_without_params(self):
        query_params = {}
        self.assertRaises(HTTPError, edit_instance.edit_instance, query_params, None)

    def test_edit_instance_with_just_instance_uri(self):
        query_params = {'instance_uri': 'anything'}
        self.assertRaises(HTTPError, edit_instance.edit_instance, query_params, None)

    def test_edit_instance_without_class_uri(self):
        query_params = {'instance_uri': 'anything', 'graph_uri': 'anything'}
        self.assertRaises(HTTPError, edit_instance.edit_instance, query_params, None)


class TestCaseRaise500(unittest.TestCase):

    def setUp(self):
        self.original_is_modify_response_successful = edit_instance.is_modify_response_successful
        edit_instance.is_modify_response_successful = lambda x: False

        self.original_create_explicit_triples = edit_instance.create_explicit_triples
        edit_instance.create_explicit_triples = lambda x, y, z: []

        self.original_create_implicit_triples = edit_instance.create_implicit_triples
        edit_instance.create_implicit_triples = lambda x, y: []

        self.original_modify_instance = edit_instance.modify_instance
        edit_instance.modify_instance = lambda params: None

    def tearDown(self):
        edit_instance.is_modify_response_successful = self.original_is_modify_response_successful
        edit_instance.create_explicit_triples = self.original_create_explicit_triples
        edit_instance.create_implicit_triples = self.original_create_implicit_triples

    @patch("brainiak.instance.edit_instance.get_cached_schema", return_value=mock_schema({"rdfs:label": "string"}))
    def test_edit_instance_raise500(self, mock_get_cached_schema):
        handler = MockHandler()
        query_params = ParamDict(handler, instance_uri='anything', graph_uri='anything', class_uri='anything')
        self.assertRaises(HTTPError, edit_instance.edit_instance, query_params, {'@context': {}})
        with self.assertRaises(HTTPError) as ex:
            edit_instance.edit_instance(query_params, {'@context': {}})
        the_exception = ex.exception
        self.assertEqual(the_exception.status_code, 500)
