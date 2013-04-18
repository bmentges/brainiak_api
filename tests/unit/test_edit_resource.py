# -*- coding: utf-8 -*-

import unittest
from tornado.web import HTTPError
from brainiak.instance import edit_resource


class TestCaseInstanceResource(unittest.TestCase):

    def setUp(self):
        self.original_instance_exists = edit_resource.instance_exists
        edit_resource.instance_exists = lambda x: True

    def tearDown(self):
        edit_resource.instance_exists = self.original_instance_exists

    def test_edit_instance_without_params(self):
        query_params = {}
        self.assertRaises(HTTPError, edit_resource.edit_instance, query_params, None)

    def test_edit_instance_with_just_instance_uri(self):
        query_params = {'instance_uri': 'anything'}
        self.assertRaises(HTTPError, edit_resource.edit_instance, query_params, None)

    def test_edit_instance_without_class_uri(self):
        query_params = {'instance_uri': 'anything', 'graph_uri': 'anything'}
        self.assertRaises(HTTPError, edit_resource.edit_instance, query_params, None)


class TestCaseRaise500(unittest.TestCase):

    def setUp(self):
        self.original_is_modify_response_successful = edit_resource.is_modify_response_successful
        edit_resource.is_modify_response_successful = lambda x: False

        self.original_create_explicit_triples = edit_resource.create_explicit_triples
        edit_resource.create_explicit_triples = lambda x, y: []

        self.original_create_implicit_triples = edit_resource.create_implicit_triples
        edit_resource.create_implicit_triples = lambda x, y: []

        self.original_modify_instance = edit_resource.modify_instance
        edit_resource.modify_instance = lambda x, y, z, w: None

    def tearDown(self):
        edit_resource.is_modify_response_successful = self.original_is_modify_response_successful
        edit_resource.create_explicit_triples = self.original_create_explicit_triples
        edit_resource.create_implicit_triples = self.original_create_implicit_triples

    def test_edit_instance_raise500(self):
        query_params = {'instance_uri': 'anything', 'graph_uri': 'anything', 'class_uri': 'anything'}
        self.assertRaises(HTTPError, edit_resource.edit_instance, query_params, {'@context': {}})
        with self.assertRaises(HTTPError) as ex:
            edit_resource.edit_instance(query_params, {'@context': {}})
        the_exception = ex.exception
        self.assertEqual(the_exception.status_code, 500)
