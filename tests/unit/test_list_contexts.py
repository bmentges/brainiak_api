import unittest
from tornado.web import HTTPError

from brainiak import triplestore
from brainiak.root.get import filter_and_build_contexts, list_all_contexts
from brainiak.root import get
from brainiak.utils import sparql
from brainiak.utils.params import ParamDict
from tests.mocks import MockHandler


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
        self.assertRaises(HTTPError, list_all_contexts, 'irrelevant_params')

    def test_raises_http_error_invalid_page(self):
        triplestore.query_sparql = lambda query: None
        sparql.filter_values = lambda a, b: []

        def mock_filter_and_build_contexts(contexts_uris):
            return []
        get.filter_and_build_contexts = mock_filter_and_build_contexts
        handler = MockHandler()
        params = ParamDict(handler, page='100')
        self.assertRaises(HTTPError, list_all_contexts, params)


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
                    {"graph": {"value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}},  # filtered out because it is standard
                    {"graph": {"value": "http://dbpedia.org/ontology/"}}
                ]}
        }
        triplestore.query_sparql = lambda query: response
        param_dict = {"per_page": "30", "page": "0"}
        base_url = "http://api.semantica.dev.globoi.com/ctx"
        handler = MockHandler(uri=base_url)
        params = ParamDict(handler, **param_dict)
        computed = list_all_contexts(params)
        expected_items = [
            {'@id': 'http://dbpedia.org/ontology/',
             'title': 'dbpedia',
             'resource_id': 'ontology'}
        ]
        self.assertEqual(computed["items"], expected_items)
        self.assertEqual(computed["item_count"], 1)
        expected_links = [
            {'rel': 'self', 'href': base_url, 'method': 'GET'},
            {'rel': 'instances', 'href': base_url + '/{resource_id}', 'method': 'GET'},
            {'rel': 'first', 'href': base_url + '?per_page=30&page=1', 'method': 'GET'},
            {'rel': 'last', 'href': base_url + '?per_page=30&page=1', 'method': 'GET'},
        ]
        self.assertEqual(sorted(computed["links"]), sorted(expected_links))

    def test_build_contexts_that_exist_in_prefixes(self):
        contexts_uris = [
            "http://www.w3.org/2006/time#",
            'http://xmlns.com/foaf/0.1/'  # filtered out because it is standard
        ]
        computed = filter_and_build_contexts(contexts_uris)
        expected = [
            {'@id': 'http://www.w3.org/2006/time#',
             'title': 'time',
             'resource_id': 'time#'},
        ]
        self.assertEqual(computed, expected)

    def test_build_contexts_of_which_one_doesnt_exist_in_prefixes(self):
        contexts_uris = [
            'http://purl.org/dc/elements/1.1/',  # filtered out because it is standard
            'http://dbpedia.org/ontology/',
            'http://unregistered.prefix'
        ]
        computed = filter_and_build_contexts(contexts_uris)
        expected = [
            {'@id': 'http://dbpedia.org/ontology/',
             'title': 'dbpedia',
             'resource_id': 'ontology'}
        ]
        self.assertEqual(computed, expected)
