import unittest

from brainiak import triplestore
from brainiak.domain.get import build_domains, build_json, list_domains
from brainiak.utils import sparql


class GetDomainTestCase(unittest.TestCase):

    def setUp(self):
        self.original_filter_values = sparql.filter_values
        self.original_query_sparql = triplestore.query_sparql

    def tearDown(self):
        sparql.filter_values = self.original_filter_values
        triplestore.query_sparql = self.original_query_sparql

    def test_list_domains(self):
        response = {"results":
            {"bindings": [
                {"graph": {"value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}},
                {"graph": {"value": "http://www.w3.org/2002/07/owl#"}}
            ]}
        }
        triplestore.query_sparql = lambda query: response
        params = {"per_page": "30", "page": "0"}
        computed = list_domains(params)
        expected_items = [
            {'@id': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'title': 'rdf',
            'resource_id': 'rdf'},
            {'@id': 'http://www.w3.org/2002/07/owl#',
            'title': 'owl',
            'resource_id': 'owl'}
        ]
        self.assertEqual(computed["items"], expected_items)
        self.assertEqual(computed["item_count"], 2)
        self.assertEqual(computed["links"], {})

    def test_build_domains_that_exist_in_prefixes(self):
        domains_uris = [
            "http://www.w3.org/2006/time#",
            'http://xmlns.com/foaf/0.1/'
        ]
        computed = build_domains(domains_uris)
        expected = [
            {'@id': 'http://www.w3.org/2006/time#',
            'title': 'time',
            'resource_id': 'time'},
            {'@id': 'http://xmlns.com/foaf/0.1/',
            'title': 'foaf',
            'resource_id': 'foaf'}
        ]
        self.assertEqual(computed, expected)

    def test_build_domains_of_which_one_doesnt_exist_in_prefixes(self):
        domains_uris = [
            'http://purl.org/dc/elements/1.1/',
            'http://dbpedia.org/ontology/',
            'http://unregistered.prefix'
        ]
        computed = build_domains(domains_uris)
        expected = [
            {'@id': 'http://purl.org/dc/elements/1.1/',
            'title': 'dc',
            'resource_id': 'dc'},
            {'@id': 'http://dbpedia.org/ontology/',
            'title': 'dbpedia',
            'resource_id': 'dbpedia'}
        ]
        self.assertEqual(computed, expected)

    def test_build_json(self):
        domains = ["a", "b", "c"]
        computed = build_json(domains)
        self.assertEqual(computed['items'], ["a", "b", "c"])
        self.assertEqual(computed['item_count'], 3)
        self.assertEqual(computed['links'], {})
