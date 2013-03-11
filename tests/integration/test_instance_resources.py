import json

from brainiak.instance.resource import QUERY_FILTER_INSTANCE
from tests import TestHandlerBase
from tests.sparql import QueryTestCase


class TestFilterInstanceResource(TestHandlerBase):

    def test_filter_without_params(self):
        response = self.fetch('/person/Gender/_filter', method='GET')
        expected_response = {'items': [
            {u'label': u'Masculino', u'subject': u'http://semantica.globo.com/person/Gender/Male'},
            {u'label': u'Transg\xeanero', u'subject': u'http://semantica.globo.com/person/Gender/Transgender'},
            {u'label': u'Feminino', u'subject': u'http://semantica.globo.com/person/Gender/Female'}]}
        self.assertEqual(response.code, 200)
        self.assertEqual(eval(response.body), expected_response)

    def test_filter_with_object_as_string(self):
        response = self.fetch('/person/Gender/_filter?object=Masculino', method='GET')
        expected_response = {'items': [
            {u'label': u'Masculino', u'subject': u'http://semantica.globo.com/person/Gender/Male'}]}
        self.assertEqual(response.code, 200)
        self.assertEqual(eval(response.body), expected_response)

    def test_filter_with_no_results(self):
        response = self.fetch('/person/Gender/_filter?object=Xubiru', method='GET')
        self.assertEqual(response.code, 204)


def build_json(bindings):
    return {
        u'head': {u'link': [], u'vars': [u'subject', u'label']},
        u'results': {
            u'bindings': bindings,
            u'distinct': False,
            u'ordered': True
        }
    }


class InstancesQueryTestCase(QueryTestCase):
    allow_triplestore_connection = True
    fixtures = ["tests/sample/instances.n3"]

    def test_instance_filter_query_by_predicate_and_object(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "<http://tatipedia.org/likes>",
            "object": "<http://tatipedia.org/Capoeira>"
        }

        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'},
                    u'label': {u'type': u'literal', u'value': u'Mary Land'}}]
        expected = build_json(bindings)

        self.assertEquals(computed, expected)

    def test_instance_filter_query_by_object(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "?predicate",
            "object": "<http://tatipedia.org/BungeeJump>"
        }
        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'},
                     u'label': {u'type': u'literal', u'value': u'Mary Land'}}]
        expected = build_json(bindings)

        self.assertEquals(computed, expected)

    def test_instance_filter_query_by_predicate(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "<http://tatipedia.org/dislikes>",
            "object": "?object"
        }
        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'},
                     u'label': {u'type': u'literal', u'value': u'Mary Land'}}]
        expected = build_json(bindings)

        self.assertEquals(computed, expected)

    def test_instance_filter_query_by_predicate_with_multiple_response(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "<http://tatipedia.org/likes>",
            "object": "?object"
        }
        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'}, u'label': {u'type': u'literal', u'value': u'Mary Land'}},
                    {u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'}, u'label': {u'type': u'literal', u'value': u'John Jones'}}]

        expected = build_json(bindings)

        self.assertEquals(computed, expected)

    def test_instance_filter_query_by_object_represented_as_string(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "?predicate",
            "object": '"Aikido"'
        }
        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'},
                     u'label': {u'type': u'literal', u'value': u'John Jones'}}]

        expected = build_json(bindings)

        self.assertEquals(computed, expected)
