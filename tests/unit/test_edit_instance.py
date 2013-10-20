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

    def test_should_edit_instance_by_instance_uri_is_true(self):
        query_params = {
            "class_name": u"_",
            "graph_uri": u"_"
        }
        response = edit_instance.should_edit_instance_by_instance_uri(query_params)
        self.assertTrue(response)

    def test_should_edit_instance_by_instance_uri_is_false_due_to_graph_uri(self):
        query_params = {
            "class_name": u"_",
            "graph_uri": u"some_uri"
        }
        response = edit_instance.should_edit_instance_by_instance_uri(query_params)
        self.assertFalse(response)

    def test_should_edit_instance_by_instance_uri_is_false_due_to_class_name(self):
        query_params = {
            "class_name": u"some_class",
            "graph_uri": u"_"
        }
        response = edit_instance.should_edit_instance_by_instance_uri(query_params)
        self.assertFalse(response)

    def test_should_edit_instance_by_instance_uri_raises_exception(self):
        query_params = {}
        with self.assertRaises(HTTPError) as exception:
            edit_instance.should_edit_instance_by_instance_uri(query_params)
        msg = "HTTP 404: Not Found (Parameter <'class_name'> is missing in order to update instance.)"
        self.assertEqual(str(exception.exception), msg)


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
