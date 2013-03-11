import json
import urllib

from brainiak.instance.resource import QUERY_FILTER_INSTANCE
from tests import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class TestFilterInstanceResource(TornadoAsyncHTTPTestCase):

    maxDiff = None

    def test_filter_without_params(self):
        response = self.fetch('/person/Gender/_filter', method='GET')
        expected_items = [
            {u'label': u'Masculino', u'subject': u'http://semantica.globo.com/person/Gender/Male'},
            {u'label': u'Transg\xeanero', u'subject': u'http://semantica.globo.com/person/Gender/Transgender'},
            {u'label': u'Feminino', u'subject': u'http://semantica.globo.com/person/Gender/Female'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        for item in received_response['items']:
            self.assertIn(item, expected_items)
        self.assertEqual(received_response['item_count'], 3)

    def test_filter_with_object_as_string(self):
        response = self.fetch('/person/Gender/_filter?object=Masculino', method='GET')
        expected_items = [{u'label': u'Masculino', u'subject': u'http://semantica.globo.com/person/Gender/Male'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['items'], expected_items)
        self.assertEqual(received_response['item_count'], 1)

    def test_filter_with_predicate_as_uri(self):
        url = urllib.quote("http://www.w3.org/2000/01/rdf-schema#label")
        response = self.fetch('/person/Gender/_filter?predicate=%s' % url, method='GET')
        expected_items = [
            {u'label': u'Masculino', u'subject': u'http://semantica.globo.com/person/Gender/Male'},
            {u'label': u'Transg\xeanero', u'subject': u'http://semantica.globo.com/person/Gender/Transgender'},
            {u'label': u'Feminino', u'subject': u'http://semantica.globo.com/person/Gender/Female'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        for item in received_response['items']:
            self.assertIn(item, expected_items)
        self.assertEqual(received_response['item_count'], 3)

    def test_filter_with_predicate_as_compressed_uri_and_object_as_label(self):
        url = urllib.quote("rdfs:label")
        response = self.fetch('/person/Gender/_filter?predicate=%s&object=Feminino' % url, method='GET')
        expected_items = [{u'label': u'Feminino', u'subject': u'http://semantica.globo.com/person/Gender/Female'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['items'], expected_items)
        self.assertEqual(received_response['item_count'], 1)

    def test_filter_with_no_results(self):
        response = self.fetch('/person/Gender/_filter?object=Xubiru', method='GET')
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['items'], [])
        self.assertEqual(received_response['item_count'], 0)


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

        self.assertEqual(computed, expected)

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

        self.assertEqual(computed, expected)

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

        self.assertEqual(computed, expected)

    def test_instance_filter_query_by_predicate_with_multiple_response(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "<http://tatipedia.org/likes>",
            "object": "?object"
        }
        query = QUERY_FILTER_INSTANCE % params
        computed_bindings = self.query(query)['results']['bindings']

        expected_bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'}, u'label': {u'type': u'literal', u'value': u'Mary Land'}},
                    {u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'}, u'label': {u'type': u'literal', u'value': u'John Jones'}}]

        expected = build_json(computed_bindings)

        self.assertEqual(len(computed_bindings), 2)
        for item in computed_bindings:
            self.assertIn(item, expected_bindings)

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

        self.assertEqual(computed, expected)
