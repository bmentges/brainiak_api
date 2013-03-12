import json
import urllib

from brainiak import triplestore
from brainiak.instance import resource
from brainiak.instance.resource import filter_instances, query_filter_instances, QUERY_FILTER_INSTANCE
from tests import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class MockResponse(object):
    def __init__(self, body):
        self.body = json.dumps(body)


class TestFilterInstanceResource(TornadoAsyncHTTPTestCase):

    maxDiff = None

    def test_filter_with_invalid_query_string(self):
        response = self.fetch('/person/Gender/_filter?love=u', method='GET')
        self.assertEqual(response.code, 400)

    def test_filter_without_predicate_and_object(self):
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
        response = self.fetch('/person/Gender/_filter?o=Masculino&lang=pt', method='GET')
        expected_items = [{u'label': u'Masculino', u'subject': u'http://semantica.globo.com/person/Gender/Male'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['items'], expected_items)
        self.assertEqual(received_response['item_count'], 1)

    def test_filter_with_predicate_as_uri(self):
        url = urllib.quote("http://www.w3.org/2000/01/rdf-schema#label")
        response = self.fetch('/person/Gender/_filter?p=%s&lang=pt' % url, method='GET')
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
        response = self.fetch('/person/Gender/_filter?p=%s&o=Feminino&lang=pt' % url, method='GET')
        expected_items = [{u'label': u'Feminino', u'subject': u'http://semantica.globo.com/person/Gender/Female'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['items'], expected_items)
        self.assertEqual(received_response['item_count'], 1)

    def test_filter_with_no_results(self):
        response = self.fetch('/person/Gender/_filter?o=Xubiru&lang=pt', method='GET')
        self.assertEqual(response.code, 404)


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

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        triplestore.query_sparql = lambda query: query

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    def test_instance_filter_query_by_predicate_and_object(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "p": "<http://tatipedia.org/likes>",
            "o": "<http://tatipedia.org/Capoeira>",
            "lang_filter": ""
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
            "p": "?predicate",
            "o": "<http://tatipedia.org/BungeeJump>",
            "lang_filter": ""
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
            "p": "<http://tatipedia.org/dislikes>",
            "o": "?object",
            "lang_filter": ""
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
            "p": "<http://tatipedia.org/likes>",
            "o": "?object",
            "lang_filter": ""
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
            "p": "?predicate",
            "o": "Aikido",
            "lang_filter": ""
        }

        query = query_filter_instances(params)
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'},
                     u'label': {u'type': u'literal', u'value': u'John Jones'}}]

        expected = build_json(bindings)

        self.assertEqual(computed, expected)

    def test_query_filter_instances_with_language_restriction_to_pt(self):
        params = {
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "Ingles",
            "lang": "pt"
        }

        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        expected_bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/london'},
                     u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Londres'}},
                    {u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/new_york'},
                     u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nova Iorque'}}]

        self.assertEqual(len(computed_bindings), 2)
        for item in computed_bindings:
            self.assertIn(item, expected_bindings)

    def test_query_filter_instances_with_language_restriction_to_en(self):
        params = {
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "?test_filter_with_object_as_string",
            "lang": "en"
        }

        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        expected_bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/london'},
                     u'label': {u'xml:lang': u'en', u'type': u'literal', u'value': u'London'}},
                    {u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/new_york'},
                     u'label': {u'xml:lang': u'en', u'type': u'literal', u'value': u'New York'}}]

        self.assertEqual(len(computed_bindings), 2)
        for item in computed_bindings:
            self.assertIn(item, expected_bindings)

    def test_filter_instances_result_is_empty(self):
        # mock
        original = resource.query_filter_instances
        resource.query_filter_instances = lambda params: MockResponse({"results": {"bindings": []}})

        response = resource.filter_instances({})
        self.assertEquals(response, None)

        # unmock
        resource.query_filter_instances = original

    def test_filter_instances_result_is_not_empty(self):
        # mock
        original = resource.query_filter_instances
        resource.query_filter_instances = lambda params: MockResponse({"results": {"bindings": [{"jj:armlock": {"type": None, "value": "Armlock"}}]}})

        response = resource.filter_instances({})
        self.assertEquals(response["items"], [{u'jj:armlock': u'Armlock'}])
        self.assertEquals(response["item_count"], 1)

        # unmock
        resource.query_filter_instances = original
