import unittest
from tornado.web import HTTPError

from brainiak import triplestore
from brainiak.root.get import filter_and_build_contexts, build_json, list_all_contexts
from brainiak.root import get
from brainiak.utils import sparql
from tests import MockRequest


class MockedTestCase(unittest.TestCase):

    def setUp(self):
        self.original_filter_and_build_contexts = get.filter_and_build_contexts
        self.original_filter_values = sparql.filter_values
        self.original_query_sparql = triplestore.query_sparql

    def tearDown(self):
        get.filter_and_build_contexts = self.original_filter_and_build_contexts
        sparql.filter_values = self.original_filter_values
        triplestore.query_sparql = self.original_query_sparql

    def test_raises_http_error(self):
        triplestore.query_sparql = lambda query: None
        sparql.filter_values = lambda a, b: []

        def mock_filter_and_build_contexts(contexts_uris):
            return []
        get.filter_and_build_contexts = mock_filter_and_build_contexts
        self.assertRaises(HTTPError, list_all_contexts, 'irrelevant_params', 'irrelevant_request')


class GetContextTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    def test_list_contexts(self):
        response = {
            "results":
                {"bindings": [
                    {"graph": {"value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}},
                    {"graph": {"value": "http://www.w3.org/2002/07/owl#"}}
                ]}
        }
        triplestore.query_sparql = lambda query: response
        params = {"per_page": "30", "page": "0"}
        base_url = "http://api.semantica.dev.globoi.com"
        request = MockRequest(uri=base_url)
        computed = list_all_contexts(params, request)
        expected_items = [
            {'@id': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
             'title': 'rdf',
             'resource_id': '22-rdf-syntax-ns#'},
            {'@id': 'http://www.w3.org/2002/07/owl#',
             'title': 'owl',
             'resource_id': 'owl#'}
        ]
        self.assertEqual(computed["items"], expected_items)
        self.assertEqual(computed["item_count"], 2)
        expected_links = [
            {'rel': 'self', 'href': base_url},
            {'rel': 'list', 'href': base_url},
            {'rel': 'item', 'href': base_url + '/{resource_id}'},
            {'rel': 'create', 'href': base_url, 'method': 'POST'},
            {'rel': 'delete', 'href': base_url + '/{resource_id}', 'method': 'DELETE'},
            {'rel': 'replace', 'href': base_url + '/{resource_id}', 'method': 'PUT'},
            {'rel': 'first', 'href': base_url + '?page=1', 'method': 'GET'},
            {'rel': 'last', 'href': base_url + '?page=1', 'method': 'GET'},
        ]
        self.assertEqual(computed["links"], expected_links)

    def test_build_contexts_that_exist_in_prefixes(self):
        contexts_uris = [
            "http://www.w3.org/2006/time#",
            'http://xmlns.com/foaf/0.1/'
        ]
        computed = filter_and_build_contexts(contexts_uris)
        expected = [
            {'@id': 'http://www.w3.org/2006/time#',
             'title': 'time',
             'resource_id': 'time#'},
            {'@id': 'http://xmlns.com/foaf/0.1/',
             'title': 'foaf',
             'resource_id': '0.1'}
        ]
        self.assertEqual(computed, expected)

    def test_build_contexts_of_which_one_doesnt_exist_in_prefixes(self):
        contexts_uris = [
            'http://purl.org/dc/elements/1.1/',
            'http://dbpedia.org/ontology/',
            'http://unregistered.prefix'
        ]
        computed = filter_and_build_contexts(contexts_uris)
        expected = [
            {'@id': 'http://purl.org/dc/elements/1.1/',
             'title': 'dc',
             'resource_id': '1.1'},
            {'@id': 'http://dbpedia.org/ontology/',
             'title': 'dbpedia',
             'resource_id': 'ontology'}
        ]
        self.assertEqual(computed, expected)

    def test_build_json(self):
        contexts = ["a", "b", "c"]
        params = {"per_page": "3", "page": "0"}
        total_items = 6
        request = MockRequest(uri='http://localhost:5100/')
        computed = build_json(contexts, total_items, params, request)
        self.assertEqual(computed['items'], ["a", "b", "c"])
        self.assertEqual(computed['item_count'], 6)
        expected_links = [
            {'rel': 'self', 'href': 'http://localhost:5100/'},
            {'rel': 'list', 'href': 'http://localhost:5100/'},
            {'rel': 'item', 'href': 'http://localhost:5100/{resource_id}'},
            {'rel': 'create', 'href': 'http://localhost:5100/', 'method': 'POST'},
            {'rel': 'delete', 'href': 'http://localhost:5100/{resource_id}', 'method': 'DELETE'},
            {'rel': 'replace', 'href': 'http://localhost:5100/{resource_id}', 'method': 'PUT'},
            {'rel': 'first', 'href': 'http://localhost:5100/?page=1', 'method': 'GET'},
            {'rel': 'last', 'href': 'http://localhost:5100/?page=2', 'method': 'GET'},
            {'rel': 'next', 'href': 'http://localhost:5100/?page=2', 'method': 'GET'}
        ]
        self.assertEqual(computed['links'], expected_links)
