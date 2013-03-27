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
