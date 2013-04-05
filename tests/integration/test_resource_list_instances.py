import json
import urllib
from mock import patch

from brainiak import triplestore
from brainiak.instance import list_resource
from brainiak.instance.list_resource import process_params, query_filter_instances, QUERY_COUNT_FILTER_INSTANCE, QUERY_FILTER_INSTANCE
from tests import TornadoAsyncHTTPTestCase, MockRequest
from tests.sparql import QueryTestCase


class TestFilterInstanceResource(TornadoAsyncHTTPTestCase):

    maxDiff = None

    @patch("brainiak.handlers.log")
    def test_filter_with_invalid_query_string(self, log):
        response = self.fetch('/person/Gender/?love=u', method='GET')
        self.assertEqual(response.code, 400)

    def test_filter_without_predicate_and_object(self):
        response = self.fetch('/person/Gender/', method='GET')
        expected_items = [
            {u'title': u'Feminino', u'@id': u'http://semantica.globo.com/person/Gender/Female', u'resource_id': u'Female'},
            {u'title': u'Masculino', u'@id': u'http://semantica.globo.com/person/Gender/Male', u'resource_id': u'Male'},
            {u'title': u'Transg\xeanero', u'@id': u'http://semantica.globo.com/person/Gender/Transgender', u'resource_id': u'Transgender'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['item_count'], 3)
        self.assertEqual(sorted(received_response['items']), sorted(expected_items))

    def test_list_by_page(self):
        response = self.fetch('/person/Gender/?page=1&per_page=2', method='GET')
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['item_count'], 3)
        self.assertEqual(len(received_response['items']), 2)

    def test_filter_with_object_as_string(self):
        response = self.fetch('/person/Gender/?o=Masculino&lang=pt', method='GET')
        expected_items = [{u'title': u'Masculino', u'@id': u'http://semantica.globo.com/person/Gender/Male', u'resource_id': u'Male'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['item_count'], 1)
        self.assertEqual(sorted(received_response['items']), sorted(expected_items))

    def test_filter_with_predicate_as_uri(self):
        url = urllib.quote("http://www.w3.org/2000/01/rdf-schema#label")
        response = self.fetch('/person/Gender/?lang=pt&p=%s' % url, method='GET')
        expected_items = [
            {u'title': u'Feminino', u'@id': u'http://semantica.globo.com/person/Gender/Female', u'resource_id': u'Female'},
            {u'title': u'Masculino', u'@id': u'http://semantica.globo.com/person/Gender/Male', u'resource_id': u'Male'},
            {u'title': u'Transg\xeanero', u'@id': u'http://semantica.globo.com/person/Gender/Transgender', u'resource_id': u'Transgender'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['item_count'], 3)
        self.assertEqual(sorted(received_response['items']), sorted(expected_items))

    def test_filter_with_predicate_as_compressed_uri_and_object_as_label(self):
        url = urllib.quote("rdfs:label")
        response = self.fetch('/person/Gender/?o=Feminino&lang=pt&p=%s' % url, method='GET')
        expected_items = [{u'title': u'Feminino', u'@id': u'http://semantica.globo.com/person/Gender/Female', u'resource_id': u'Female'}]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(received_response['item_count'], 1)
        self.assertEqual(received_response['items'], expected_items)

    @patch("brainiak.handlers.log")
    def test_filter_with_no_results(self, log):
        response = self.fetch('/person/Gender/?o=Xubiru&lang=pt', method='GET')
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


class FilterInstancesQueryTestCase(QueryTestCase):
    allow_triplestore_connection = True
    fixtures = ["tests/sample/instances.n3"]
    graph_uri = "http://tatipedia.org/"

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        triplestore.query_sparql = lambda query: query
        self.original_query_filter_instances = list_resource.query_filter_instances
        self.original_query_count_filter_instances = list_resource.query_count_filter_instances

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql
        list_resource.query_filter_instances = self.original_query_filter_instances
        list_resource.query_count_filter_instances = self.original_query_count_filter_instances

    def test_process_params(self):
        params = {
            "class_uri": 'http://tatipedia.org/Species',
            "p": 'http://tatipedia.org/livesIn',
            "o": 'dbpedia:Australia',
            "lang": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0"
        }
        expected = {'class_uri': 'http://tatipedia.org/Species',
                    'graph_uri': 'http://tatipedia.org/',
                    'lang': 'pt',
                    'lang_filter_label': '\n    FILTER(langMatches(lang(?label), "pt") OR langMatches(lang(?label), "")) .\n',
                    'o': '<http://dbpedia.org/ontology/Australia>',
                    'p': '<http://tatipedia.org/livesIn>',
                    'page': '0',
                    'per_page': '10',
                    'po': '; <http://tatipedia.org/livesIn> <http://dbpedia.org/ontology/Australia> .'}
        computed = process_params(params)
        self.assertEqual(expected, computed)

    def test_count_query(self):
        params = {
            "class_uri": "http://tatipedia.org/Species",
            "p": "http://tatipedia.org/order",
            "o": "http://tatipedia.org/Monotremata",
            "lang_filter": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0"
        }
        params = process_params(params)
        query = QUERY_COUNT_FILTER_INSTANCE % params
        computed = self.query(query)["results"]["bindings"]
        expected = [{u'total': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer', u'type': u'typed-literal', u'value': u'3'}}]
        self.assertEqual(computed, expected)

    def test_instance_filter_query_by_predicate_and_object(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "p": "<http://tatipedia.org/likes>",
            "o": "<http://tatipedia.org/Capoeira>",
            "lang_filter": "",
            "lang_filter_label": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
            "po": "; <http://tatipedia.org/likes> <http://tatipedia.org/Capoeira> ."
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
            "o": "http://tatipedia.org/BungeeJump",
            "lang_filter": "",
            "lang_filter_label": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0"
        }
        params = process_params(params)
        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'},
                     u'label': {u'type': u'literal', u'value': u'Mary Land'}}]
        expected = build_json(bindings)

        self.assertEqual(computed, expected)

    def test_instance_filter_query_by_predicate(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "lang_filter_label": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
            "po": "; <http://tatipedia.org/dislikes> ?object ."
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
            "lang_filter_label": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
            "po": "; <http://tatipedia.org/likes> ?object ."
        }
        query = QUERY_FILTER_INSTANCE % params
        computed_bindings = self.query(query)['results']['bindings']

        expected_bindings = [
                                {
                                    u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'},
                                    u'label': {u'type': u'literal', u'value': u'John Jones'}
                                },
                                {
                                    u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'},
                                    u'label': {u'type': u'literal', u'value': u'Mary Land'}
                                }
        ]

        expected = build_json(computed_bindings)

        self.assertEqual(len(computed_bindings), 2)
        self.assertEqual(sorted(computed_bindings), sorted(expected_bindings))

    def test_instance_filter_query_by_object_represented_as_string(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "p": "?predicate",
            "o": "Aikido",
            "lang_filter_label": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
        }
        params = process_params(params)

        query = query_filter_instances(params)
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'},
                     u'label': {u'type': u'literal', u'value': u'John Jones'}
                     }]

        expected = build_json(bindings)

        self.assertEqual(computed, expected)

    # def test_instance_filter_in_inexistent_graph(self):
    #     params = {
    #         "class_uri": "http://tatipedia.org/test/Person",
    #         "p": "?predicate",
    #         "o": "Aikido",
    #         "lang_filter": "",
    #         "graph_uri": "http://neverland.com/",
    #         "per_page": "10",
    #         "page": "0"
    #     }

    #     query = query_filter_instances(params)
    #     response = self.query(query, params["graph_uri"])
    #     self.assertFalse(response["results"]["bindings"])

    def test_query_filter_instances_with_language_restriction_to_pt(self):
        params = {
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "Ingles",
            "lang": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0"
        }
        params = process_params(params)
        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        expected_bindings = [
                                {
                                    u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/london'},
                                    u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Londres'}
                                },
                                {
                                    u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/new_york'},
                                    u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nova Iorque'}
                                }
        ]

        self.assertEqual(len(computed_bindings), 2)
        self.assertEqual(sorted(computed_bindings), sorted(expected_bindings))

    def test_query_filter_instances_with_language_restriction_to_pt_and_any(self):
        params = {
            "class_uri": "http://tatipedia.org/Species",
            "p": "http://tatipedia.org/order",
            "o": "http://tatipedia.org/Monotremata",
            "lang_filter": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0"
        }
        params = process_params(params)
        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        expected_bindings = [
                                {
                                    u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/Platypus'},
                                    u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Ornitorrinco'}
                                },
                                {
                                    u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/Echidna'},
                                    u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Equidna'}
                                },
                                {
                                    u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/Teinolophos'},
                                    u'label': {u'type': u'literal', u'value': u"Teinolophos trusleri"}
                                }
        ]

        self.assertEqual(len(computed_bindings), 3)
        self.assertEqual(sorted(computed_bindings), sorted(expected_bindings))

    def test_query_page_0(self):
        params = {
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "Ingles",
            "lang": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "1",
            "page": "0"
        }
        params = process_params(params)
        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        self.assertEqual(len(computed_bindings), 1)

    def test_query_page_1(self):
        params = {
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "Ingles",
            "lang": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "1",
            "page": "1"
        }
        params = process_params(params)
        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        self.assertEqual(len(computed_bindings), 1)

    def test_query_filter_instances_with_language_restriction_to_en(self):
        params = {
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "?test_filter_with_object_as_string",
            "lang": "en",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0"
        }
        params = process_params(params)
        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        expected_bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/london'},
                              u'label': {u'xml:lang': u'en', u'type': u'literal', u'value': u'London'}},
                             {u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/new_york'},
                              u'label': {u'xml:lang': u'en', u'type': u'literal', u'value': u'New York'}}]

        self.assertEqual(len(computed_bindings), 2)
        self.assertEqual(sorted(computed_bindings), sorted(expected_bindings))

    def test_filter_instances_result_is_empty(self):
        # mock
        list_resource.query_filter_instances = lambda params: {"results": {"bindings": []}}
        list_resource.query_count_filter_instances = lambda params: {"results": {"bindings": []}}

        params = {"o": "", "p": "", "class_uri": ""}
        response = list_resource.filter_instances(params)
        self.assertEquals(response, None)

    def test_filter_instances_result_is_not_empty(self):
        query_string = "page=2&per_page=3"  # page based on API (begins with 1)
        sample_json = {"results": {"bindings": []}}
        count_json = {"results": {"bindings": [{"total": {"value": "12"}}]}}
        list_resource.query_filter_instances = lambda params: sample_json
        list_resource.query_count_filter_instances = lambda params: count_json
        params = {"context_name": "ctx",
          "class_name": "klass",
          "request": MockRequest(query_string),
          "per_page": "3",
          "page": "1"}
        response = list_resource.filter_instances(params)  # page based on virtuoso (begins with 0)
        expected_links = [
            {
                'href': "http://localhost:5100/ctx/klass/?page=2&per_page=3",
                'rel': "self"
            },
            {
                'href': "http://localhost:5100/ctx/klass/",
                'rel': "list"
            },
            {
                'href': "http://localhost:5100/ctx/klass/{resource_id}",
                'rel': "item"
            },
            {
                'href': "http://localhost:5100/ctx/klass/",
                'method': "POST",
                'rel': "create"
            },
            {
                'href': "http://localhost:5100/ctx/klass/{resource_id}",
                'method': "DELETE",
                'rel': "delete"

            },
            {
                'href': "http://localhost:5100/ctx/klass/{resource_id}",
                'method': "PUT",
                'rel': "replace"

            },
            {
                'href': "http://localhost:5100/ctx/klass/?per_page=3&page=1",
                'method': "GET",
                'rel': "first"
            },
            {
                'href': "http://localhost:5100/ctx/klass/?per_page=3&page=4",
                'method': "GET",
                'rel': "last"
            },
            {
                'href': "http://localhost:5100/ctx/klass/?per_page=3&page=1",
                'method': "GET",
                'rel': "previous"
            },
            {
                'href': "http://localhost:5100/ctx/klass/?per_page=3&page=3",
                'method': "GET",
                'rel': "next"
            }
        ]
        self.assertEquals(response["item_count"], 12)
        self.assertEquals(response["links"], expected_links)
