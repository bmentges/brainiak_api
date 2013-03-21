import unittest

from brainiak.instance import get_resource
from tests import MockRequest


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
