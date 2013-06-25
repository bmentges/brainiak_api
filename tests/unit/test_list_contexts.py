import unittest
from tornado.web import HTTPError
from mock import patch

from brainiak import triplestore
from brainiak.root.get import filter_and_build_contexts, list_all_contexts
from brainiak.utils.params import ParamDict
from tests.mocks import MockHandler


class MockedTestCase(unittest.TestCase):

    @patch('brainiak.triplestore.query_sparql')
    @patch('brainiak.utils.sparql.filter_values', return_value=[])
    @patch('brainiak.root.get.filter_and_build_contexts', return_value=[])
    def test_raises_http_error(self, mock1, mock2, mock3):
        self.assertRaises(HTTPError, list_all_contexts, 'irrelevant_params')

    @patch('brainiak.triplestore.query_sparql')
    @patch('brainiak.utils.sparql.filter_values', return_value=[])
    @patch('brainiak.root.get.filter_and_build_contexts', return_value=[])
    def test_raises_http_error_empty_page(self, mock1, mock2, mock3):
        handler = MockHandler()
        params = ParamDict(handler, page='100')
        self.assertRaises(HTTPError, list_all_contexts, params)

    @patch('brainiak.triplestore.query_sparql')
    @patch('brainiak.utils.sparql.filter_values')
    @patch('brainiak.root.get.filter_and_build_contexts', return_value=[])
    def test_raises_http_error_invalid_page(self, mock1, mock2, mock3):
        handler = MockHandler()
        params = ParamDict(handler, page='100')
        self.assertRaises(HTTPError, list_all_contexts, params)


class GetContextTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        response = {
            "results":
                {"bindings": [
                    {"graph": {"value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}},  # filtered out because it is standard
                    {"graph": {"value": "http://dbpedia.org/ontology/"}}
                ]}
        }
        triplestore.query_sparql = lambda query: response

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    def test_list_contexts(self):
        param_dict = {"per_page": "30", "page": "0"}
        root_url = "http://api.semantica.dev.globoi.com"
        base_url = "http://api.semantica.dev.globoi.com/ctx"
        handler = MockHandler(uri=base_url)
        params = ParamDict(handler, **param_dict)
        computed = list_all_contexts(params)
        expected_items = [
            {'@id': 'http://dbpedia.org/ontology/',
             'title': 'dbpedia',
             'resource_id': 'dbpedia'}
        ]
        self.assertEqual(computed["items"], expected_items)
        expected_links = [
            {'href': 'http://api.semantica.dev.globoi.com/_status', 'method': 'GET', 'rel': 'status'},
            {'rel': 'self', 'href': base_url, 'method': 'GET'},
            {'rel': 'list', 'href': base_url + '/{resource_id}', 'method': 'GET'},
            {'rel': 'context', 'href': base_url + '/{resource_id}', 'method': 'GET'},
            {'rel': 'next', 'href': 'http://api.semantica.dev.globoi.com/ctx?per_page=30&page=2', 'method': 'GET'},
            {'rel': 'first', 'href': base_url + '?per_page=30&page=1', 'method': 'GET'},
        ]
        self.assertEqual(sorted(computed["links"]), sorted(expected_links))

    def test_with_item_count(self):
        base_url = "http://api.semantica.dev.globoi.com/ctx"
        param_dict = {"do_item_count": "1", "per_page": "30", "page": "0"}
        handler = MockHandler(uri=base_url)
        params = ParamDict(handler, **param_dict)
        computed = list_all_contexts(params)
        self.assertEqual(int(computed["item_count"]), 1)

    def test_without_item_count(self):
        base_url = "http://api.semantica.dev.globoi.com/ctx"
        param_dict = {"do_item_count": "0", "per_page": "30", "page": "0"}
        handler = MockHandler(uri=base_url)
        params = ParamDict(handler, **param_dict)
        computed = list_all_contexts(params)
        self.assertTrue("item_count" not in computed)

    def test_build_contexts_that_exist_in_prefixes(self):
        contexts_uris = [
            "http://www.w3.org/2006/time#",
            'http://xmlns.com/foaf/0.1/'  # filtered out because it is standard
        ]
        computed = filter_and_build_contexts(contexts_uris)
        expected = [
            {'@id': 'http://www.w3.org/2006/time#',
             'title': 'time',
             'resource_id': 'time'},
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
             'resource_id': 'dbpedia'}
        ]
        self.assertEqual(computed, expected)
