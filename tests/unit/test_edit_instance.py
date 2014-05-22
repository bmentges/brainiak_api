# -*- coding: utf-8 -*-

import unittest
from mock import patch
from tornado.web import HTTPError

from brainiak.utils.sparql import InstanceError
from brainiak.instance import edit_instance


class ErrorTestCase(unittest.TestCase):

    @patch("brainiak.instance.edit_instance.create_explicit_triples", side_effect=InstanceError())
    @patch("brainiak.instance.edit_instance.get_cached_schema")
    @patch("brainiak.instance.edit_instance.must_retrieve_graph_and_class_uri", return_value=False)
    def test_raises_400(self, mock_must, mock_get_cache, mock_create_triples):
        dummy_query_params = {
            "instance_uri": 1,
            "class_uri": 2,
            "graph_uri": 3
        }
        with self.assertRaises(HTTPError) as exception:
            edit_instance.edit_instance(dummy_query_params, {})
        self.assertEqual(exception.exception.status_code, 400)


class TestCaseInstanceResource(unittest.TestCase):

    def setUp(self):
        self.original_instance_exists = edit_instance.instance_exists
        edit_instance.instance_exists = lambda x: True

    def tearDown(self):
        edit_instance.instance_exists = self.original_instance_exists

    def test_edit_instance_without_params(self):
        query_params = {}
        self.assertRaises(HTTPError, edit_instance.edit_instance, query_params, {})

    def test_edit_instance_with_just_instance_uri(self):
        query_params = {'instance_uri': 'anything', 'rdfs:label': 'a label'}
        self.assertRaises(HTTPError, edit_instance.edit_instance, query_params, {})

    def test_edit_instance_without_class_uri(self):
        query_params = {'instance_uri': 'anything', 'graph_uri': 'anything', 'rdfs:label': 'a label'}
        self.assertRaises(HTTPError, edit_instance.edit_instance, query_params, {})


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
