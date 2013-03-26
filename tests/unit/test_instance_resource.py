# -*- coding: utf-8 -*-
import unittest
from mock import Mock

from brainiak.instance import get_resource
from tests import MockRequest


class TestCaseInstanceResource(unittest.TestCase):
    def setUp(self):
        self.original_query_all_properties_and_objects = get_resource.query_all_properties_and_objects
        self.original_assemble_instance_json = get_resource.assemble_instance_json

    def tearDown(self):
        get_resource.query_all_properties_and_objects = self.original_query_all_properties_and_objects
        get_resource.assemble_instance_json = self.original_assemble_instance_json

    def test_get_instance_with_result(self):
        db_response = {"results": {"bindings": ["not_empty"]}}

        def mock_query_all_properties_and_objects(query_params):
            return db_response
        get_resource.query_all_properties_and_objects = mock_query_all_properties_and_objects

        mock_assemble_instance_json = Mock(return_value="ok")
        get_resource.assemble_instance_json = mock_assemble_instance_json
        query_params = {'request': MockRequest(instance="instance"),
                        'context_name': 'place',
                        'class_name': 'Country',
                        'instance_id': 'Brazil',
                        'instance_uri': 'http://semantica.globo.com/place/Country/Brazil'}

        response = get_resource.get_instance(query_params)

        self.assertEqual(response, "ok")
        self.assertTrue(mock_assemble_instance_json.called)

    def test_get_instance_without_result(self):
        db_response = {"results": {"bindings": []}}

        def mock_query_all_properties_and_objects(query_params):
            return db_response
        get_resource.query_all_properties_and_objects = mock_query_all_properties_and_objects

        mock_assemble_instance_json = Mock(return_value="ok")
        get_resource.assemble_instance_json = mock_assemble_instance_json
        query_params = {'request': MockRequest(instance="instance"),
                        'context_name': 'place',
                        'class_name': 'Country',
                        'instance_id': 'Brazil',
                        'instance_uri': 'http://semantica.globo.com/place/Country/Brazil'}

        response = get_resource.get_instance(query_params)

        self.assertEqual(response, None)
        self.assertFalse(mock_assemble_instance_json.called)


class AssembleTestCase(unittest.TestCase):

    def test_assemble_instance_json_links(self):
        query_params = {'request': MockRequest(instance="instance"), 'context_name': 'ctx', 'class_name': 'klass'}
        query_result_dict = {'results': {'bindings': []}}
        get_resource.build_items_dict = lambda context, bindings: {}
        computed = get_resource.assemble_instance_json(query_params, query_result_dict)
        expected_links = [
            {'rel': 'self', 'href': 'http://localhost:5100/ctx/klass/instance'},
            {'rel': 'describedBy', 'href': 'http://localhost:5100/ctx/klass/_schema'},
            {'rel': 'edit', 'href': 'http://localhost:5100/ctx/klass/instance', 'method': 'PATCH'},
            {'rel': 'delete', 'href': 'http://localhost:5100/ctx/klass/instance', 'method': 'DELETE'},
            {'rel': 'replace', 'href': 'http://localhost:5100/ctx/klass/instance', 'method': 'PUT'}
        ]

        self.assertEqual(computed["@id"], "http://localhost:5100/ctx/klass/instance")
        self.assertEqual(computed["@type"], "ctx:klass")
        self.assertEqual(computed["@context"], {})
        self.assertEqual(computed["$schema"], 'http://localhost:5100/ctx/klass/_schema')
        self.assertEqual(computed["links"], expected_links)

    def test_assemble_instance_json_links_with_context(self):

        class InnerContextMock():
            pass

        class ContextMock():
            context = InnerContextMock()
            object_properties = {"person": "person:Person"}

        context = ContextMock()
        query_params = {'request': MockRequest(instance="instance"), 'context_name': 'ctx', 'class_name': 'klass'}
        query_result_dict = {'results': {'bindings': []}}
        get_resource.build_items_dict = lambda context, bindings: {}

        computed = get_resource.assemble_instance_json(query_params, query_result_dict, context)
        expected_links = [
            {'rel': 'self', 'href': 'http://localhost:5100/ctx/klass/instance'},
            {'rel': 'describedBy', 'href': 'http://localhost:5100/ctx/klass/_schema'},
            {'rel': 'edit', 'href': 'http://localhost:5100/ctx/klass/instance', 'method': 'PATCH'},
            {'rel': 'delete', 'href': 'http://localhost:5100/ctx/klass/instance', 'method': 'DELETE'},
            {'rel': 'replace', 'href': 'http://localhost:5100/ctx/klass/instance', 'method': 'PUT'},
            {'rel': 'person', 'href': '/person/Person'}
        ]

        self.assertEqual(computed["@id"], "http://localhost:5100/ctx/klass/instance")
        self.assertEqual(computed["@type"], "ctx:klass")
        self.assertIsInstance(computed["@context"], InnerContextMock)
        self.assertEqual(computed["$schema"], 'http://localhost:5100/ctx/klass/_schema')
        self.assertEqual(sorted(computed["links"]), sorted(expected_links))
