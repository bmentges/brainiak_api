import json
import urllib
from mock import patch
from brainiak import triplestore, settings
from brainiak.collection import get_collection
from brainiak.collection.get_collection import query_filter_instances, Query

from tests.mocks import Params
from tests.sparql import QueryTestCase
from tests.utils import URLTestCase
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class TestFilterInstanceResource(TornadoAsyncHTTPTestCase, URLTestCase):

    maxDiff = None

    def setUp(self):
        self.original_filter_instances = get_collection.filter_instances
        TornadoAsyncHTTPTestCase.setUp(self)

    def tearDown(self):
        get_collection.filter_instances = self.original_filter_instances

    @patch("brainiak.handlers.logger")
    def test_filter_with_invalid_query_string(self, log):
        response = self.fetch('/person/Gender/?love=u', method='GET')
        self.assertEqual(response.code, 400)

    def test_filter_without_predicate_and_object(self):
        response = self.fetch('/person/Gender/?expand_uri=1', method='GET')
        expected_items = [
            {
                u'title': u'Feminino',
                u'@id': settings.URI_PREFIX + 'person/Gender/Female',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'resource_id': u'Female'
            },
            {
                u'title': u'Masculino',
                u'@id': settings.URI_PREFIX + u'person/Gender/Male',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'resource_id': u'Male'
            },
            {
                u'title': u'Transg\xeanero',
                u'@id': settings.URI_PREFIX + u'person/Gender/Transgender',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'resource_id': u'Transgender'
            }
        ]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(sorted(received_response['items']), sorted(expected_items))

    def test_list_by_page(self):
        response = self.fetch('/person/Gender/?page=1&per_page=2', method='GET')
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(len(received_response['items']), 2)
        self.assertFalse('item_count' in received_response)

    def test_list_by_page_with_count(self):
        response = self.fetch('/person/Gender/?page=1&per_page=2&do_item_count=1', method='GET')

        self.assertEqual(response.code, 200)
        received_response = json.loads(response.body)

        self.assertEqual(len(received_response), 10)
        keys = received_response.keys()
        self.assertIn("items", keys)
        self.assertIn("item_count", keys)
        self.assertIn('_base_url', keys)
        self.assertIn('_first_args', keys)
        self.assertIn('_last_args', keys)
        self.assertIn('_next_args', keys)
        self.assertIn('_class_prefix', keys)
        self.assertIn('_schema_url', keys)
        self.assertIn('@context', keys)
        self.assertIn('@id', keys)

        self.assertEqual(len(received_response['items']), 2)

    def test_list_links_prev_and_next(self):
        response = self.fetch('/person/Gender/?page=2&per_page=1&do_item_count=1', method='GET')
        received_response = json.loads(response.body)
        self.assertQueryStringArgsEqual(received_response["_previous_args"], "page=1&per_page=1&do_item_count=1")
        self.assertQueryStringArgsEqual(received_response["_next_args"], "page=3&per_page=1&do_item_count=1")

    def test_list_by_page_sort_first_page(self):
        response = self.fetch('/person/Gender/?page=1&per_page=2&sort_by=rdfs:label&expand_uri=1', method='GET')
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        expected_items = [
            {
                u'@id': settings.URI_PREFIX + u'person/Gender/Female',
                u'resource_id': u'Female',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'title': u'Feminino'
            },
            {
                u'@id': settings.URI_PREFIX + u'person/Gender/Male',
                u'resource_id': u'Male',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'title': u'Masculino'
            }
        ]
        self.assertEqual(received_response['items'], expected_items)

    def test_list_by_page_sort_second_page(self):
        response = self.fetch('/person/Gender/?page=2&per_page=2&sort_by=rdfs:label&expand_uri=1', method='GET')
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        expected_items = [
            {
                u'@id': settings.URI_PREFIX + u'person/Gender/Transgender',
                u'resource_id': u'Transgender',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'title': u'Transg\xeanero'
            }
        ]
        self.assertEqual(received_response['items'], expected_items)

    def test_list_by_page_sort_first_page_desc(self):
        response = self.fetch('/person/Gender/?page=1&per_page=2&sort_by=rdfs:label&sort_order=desc&expand_uri=1', method='GET')
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        expected_items = [
            {
                u'@id': settings.URI_PREFIX + u'person/Gender/Transgender',
                u'resource_id': u'Transgender',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'title': u'Transg\xeanero'
            },
            {
                u'@id': settings.URI_PREFIX + u'person/Gender/Male',
                u'resource_id': u'Male',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'title': u'Masculino'
            }
        ]
        self.assertEqual(received_response['items'], expected_items)

    def test_filter_with_object_as_string(self):
        response = self.fetch('/person/Gender/?o=Masculino&lang=pt', method='GET')
        expected_items = [
            {
                u'title': u'Masculino',
                u'@id': settings.URI_PREFIX + u'person/Gender/Male',
                u'resource_id': u'Male',
                u'class_prefix': u'person:',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'p': [u'upper:name', u'rdfs:label']
            }
        ]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(sorted(received_response['items']), sorted(expected_items))

    def test_filter_with_predicate_as_uri(self):
        url = urllib.quote("http://www.w3.org/2000/01/rdf-schema#label")
        response = self.fetch('/person/Gender/?lang=pt&p=%s&&expand_uri=1' % url, method='GET')
        expected_items = [
            {
                u'title': u'Feminino',
                u'@id': settings.URI_PREFIX + u'person/Gender/Female',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'resource_id': u'Female'
            },
            {
                u'title': u'Masculino',
                u'@id': settings.URI_PREFIX + u'person/Gender/Male',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'resource_id': u'Male'
            },
            {
                u'title': u'Transg\xeanero',
                u'@id': settings.URI_PREFIX + u'person/Gender/Transgender',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'resource_id': u'Transgender'
            }
        ]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(sorted(received_response['items']), sorted(expected_items))

    def test_filter_with_predicate_as_compressed_uri_and_object_as_label_with_expand_uri_1(self):
        url = urllib.quote("rdfs:label")
        response = self.fetch('/person/Gender/?o=Feminino&lang=pt&p=%s&expand_uri=1' % url, method='GET')
        expected_items = [
            {
                u'title': u'Feminino',
                u'@id': settings.URI_PREFIX + u'person/Gender/Female',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'resource_id': u'Female'}
        ]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertItemsEqual(received_response['items'], expected_items)

    def test_filter_with_predicate_as_compressed_uri_and_object_as_label_with_expand_uri_0(self):
        url = urllib.quote("rdfs:label")
        response = self.fetch('/person/Gender/?o=Feminino&lang=pt&p=%s&expand_uri=0' % url, method='GET')
        expected_items = [
            {
                u'title': u'Feminino',
                u'@id': settings.URI_PREFIX + u'person/Gender/Female',
                u'class_prefix': u'http://semantica.globo.com/person/',
                u'instance_prefix': u'http://semantica.globo.com/person/Gender/',
                u'resource_id': u'Female'}
        ]
        received_response = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertItemsEqual(received_response['items'], expected_items)

    @patch("brainiak.handlers.logger")
    def test_filter_with_no_results(self, log):
        response = self.fetch('/person/Gender/?o=Xubiru&lang=pt', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        expected_body = {
            u'items': [],
            u'warning': u'Instances of class (http://semantica.globo.com/person/Gender) in graph (http://semantica.globo.com/person/) with o=(Xubiru), language=(pt) and in page=(1) were not found.'
        }
        self.assertEqual(body, expected_body)

    @patch("brainiak.handlers.logger")
    def test_class_does_not_exist(self, log):
        response = self.fetch('/person/Xubiru', method='GET')
        self.assertEqual(response.code, 404)

    @patch("brainiak.handlers.logger")
    def test_filter_with_no_results_and_multiple_predicates(self, log):
        get_collection.filter_instances = lambda params: None
        response = self.fetch('/person/Gender/?o=object&p=rdfs:label&o1=object1&lang=pt', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        expected_body = {
            u'items': [],
            u'warning': u'Instances of class (http://semantica.globo.com/person/Gender) in graph (http://semantica.globo.com/person/) with p=(rdfs:label) with o=(object) with o1=(object1), language=(pt) and in page=(1) were not found.'
        }
        self.assertEqual(body, expected_body)


class MultipleGraphsResource(TornadoAsyncHTTPTestCase, QueryTestCase):
    fixtures_by_graph = {
        "http://brmedia.com/sports": ["tests/sample/sports.n3"],
        "http://brmedia.com/politics": ["tests/sample/politics.n3"],
        "http://brmedia.com/entertainment": ["tests/sample/entertainment.n3"]
    }
    maxDiff = None
    allow_triplestore_connection = True

    def test_news_filtered_by_sports_graph(self):
        response = self.fetch('/dbpedia/News/?graph_uri=http://brmedia.com/sports', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        computed_items = body["items"]
        expected_items = [{
            u'resource_id': u'news_cricket',
            u'instance_prefix': u'http://brmedia.com/',
            u'class_prefix': u'dbpedia:',
            u'@id': u'http://brmedia.com/news_cricket',
            u'title': u'Cricket becomes the most popular sport of Brazil'
        }]
        self.assertEqual(computed_items, expected_items)

    def test_news_filtered_by_politics_graph(self):
        response = self.fetch('/dbpedia/News/?do_item_count=1&graph_uri=http://brmedia.com/politics', method='GET')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)

        keys = body.keys()
        self.assertEqual(len(keys), 9)
        self.assertIn("items", keys)
        self.assertIn("item_count", keys)
        self.assertIn('_base_url', keys)
        self.assertIn('_first_args', keys)
        self.assertIn('_last_args', keys)
        self.assertIn('_class_prefix', keys)
        self.assertIn('_schema_url', keys)
        self.assertIn('@context', keys)
        self.assertIn('@id', keys)

        computed_items = body["items"]
        expected_items = [{
            u'resource_id': u'news_president_answer',
            u'instance_prefix': u'http://brmedia.com/',
            u'class_prefix': u'dbpedia:',
            u'@id': u'http://brmedia.com/news_president_answer',
            u'title': u"President explains the reason for the war - it is 42"
        }]
        self.assertEqual(computed_items, expected_items)


class MixTestFilterInstanceResource(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    allow_triplestore_connection = True
    fixtures = ["tests/sample/instances.n3"]
    graph_uri = "http://tatipedia.org/"

    @patch("brainiak.handlers.logger")
    def test_json_returns_object_per_item(self, log):
        response = self.fetch('/tpedia/Person/?p=http://tatipedia.org/likes&graph_uri=http://tatipedia.org/&class_prefix=http://tatipedia.org/', method='GET')
        self.assertEqual(response.code, 200)
        computed_items = json.loads(response.body)["items"]
        expected_items = [
            {
                u'http://tatipedia.org/likes': [u'http://tatipedia.org/JiuJitsu', u'http://tatipedia.org/Capoeira'],
                u'instance_prefix': u'http://tatipedia.org/',
                u'class_prefix': u'http://tatipedia.org/',
                u'resource_id': u'mary',
                u'@id': u'http://tatipedia.org/mary',
                u'title': u'Mary Land'
            },
            {
                u'http://tatipedia.org/likes': [u'http://tatipedia.org/JiuJitsu', u'Aikido'],
                u'instance_prefix': u'http://tatipedia.org/',
                u'class_prefix': u'http://tatipedia.org/',
                u'resource_id': u'john',
                u'@id': u'http://tatipedia.org/john',
                u'title': u'John Jones'
            }
        ]
        sorted_computed_items = sorted(computed_items)
        sorted_expected_items = sorted(expected_items)
        self.assertEqual(sorted_computed_items, sorted_expected_items)

    @patch("brainiak.handlers.logger")
    def test_multiple_predicates(self, log):
        response = self.fetch('/tpedia/Person/?o=http://tatipedia.org/JiuJitsu&p1=http://tatipedia.org/isAlive&o1=Yes&graph_uri=http://tatipedia.org/&class_prefix=http://tatipedia.org/&lang=en', method='GET')
        self.assertEqual(response.code, 200)
        computed_items = json.loads(response.body)["items"]
        expected_items = [
            {
                u'p': u'http://tatipedia.org/likes',
                u'class_prefix': u'http://tatipedia.org/',
                u'instance_prefix': u'http://tatipedia.org/',
                u'resource_id': u'john',
                u'@id': u'http://tatipedia.org/john',
                u'title': u'John Jones'
            }
        ]
        self.assertItemsEqual(computed_items, expected_items)

    @patch("brainiak.handlers.logger")
    def test_multiple_unknown_predicates(self, log):
        response = self.fetch('/tpedia/Person/?o=http://tatipedia.org/JiuJitsu&o1=Yes&graph_uri=http://tatipedia.org/&class_prefix=http://tatipedia.org/&lang=en', method='GET')
        self.assertEqual(response.code, 200)
        computed_items = json.loads(response.body)["items"]
        expected_items = [
            {
                u'p': u'http://tatipedia.org/likes',
                u'p1': 'http://tatipedia.org/isAlive',
                u'class_prefix': u'http://tatipedia.org/',
                u'instance_prefix': u'http://tatipedia.org/',
                u'resource_id': u'john',
                u'@id': u'http://tatipedia.org/john',
                u'title': u'John Jones'
            }
        ]
        self.assertItemsEqual(computed_items, expected_items)

    @patch("brainiak.handlers.logger")
    def test_multiple_unknown_objects(self, log):
        response = self.fetch('/tpedia/Person/?p=http://tatipedia.org/likes&p1=http://tatipedia.org/isAlive&graph_uri=http://tatipedia.org/&class_prefix=http://tatipedia.org/&lang=en', method='GET')
        self.assertEqual(response.code, 200)
        computed_items = json.loads(response.body)["items"]
        expected_items = [
            {
                u'@id': u'http://tatipedia.org/john',
                u'class_prefix': u'http://tatipedia.org/',
                u'http://tatipedia.org/isAlive': u'Yes',
                u'http://tatipedia.org/likes': [
                    u'http://tatipedia.org/JiuJitsu',
                    u'Aikido'],
                u'instance_prefix': u'http://tatipedia.org/',
                u'resource_id': u'john',
                u'title': u'John Jones'
            },
            {
                u'@id': u'http://tatipedia.org/mary',
                u'class_prefix': u'http://tatipedia.org/',
                u'http://tatipedia.org/isAlive': u'No',
                u'http://tatipedia.org/likes': [
                    u'http://tatipedia.org/JiuJitsu',
                    u'http://tatipedia.org/Capoeira'],
                u'instance_prefix': u'http://tatipedia.org/',
                u'resource_id': u'mary',
                u'title': u'Mary Land'
            }
        ]
        self.assertItemsEqual(computed_items, expected_items)

    @patch("brainiak.handlers.logger")
    def test_json_returns_sortby_per_item(self, log):
        response = self.fetch('/tpedia/Person/?sort_by=dbpedia:nickname&graph_uri=http://tatipedia.org/&class_prefix=http://tatipedia.org/', method='GET')
        self.assertEqual(response.code, 200)
        computed_items = json.loads(response.body)["items"]
        expected_items = [
            {
                u'dbpedia:nickname': u'JJ',
                u'resource_id': u'john',
                u'class_prefix': u'http://tatipedia.org/',
                u'instance_prefix': u'http://tatipedia.org/',
                u'@id': u'http://tatipedia.org/john',
                u'title': u'John Jones'
            },
            {
                u'dbpedia:nickname': u'ML',
                u'resource_id': u'mary',
                u'class_prefix': u'http://tatipedia.org/',
                u'instance_prefix': u'http://tatipedia.org/',
                u'@id': u'http://tatipedia.org/mary',
                u'title': u'Mary Land'
            }
        ]
        self.assertEqual(computed_items, expected_items)

    @patch("brainiak.handlers.logger")
    def test_json_returns_sortby_include_empty_value(self, log):
        response = self.fetch('/tpedia/SoccerClub/?graph_uri=http://tatipedia.org/&class_prefix=http://tatipedia.org/&sort_by=http://tatipedia.org/stadium', method='GET')
        self.assertEqual(response.code, 200)
        computed_items = json.loads(response.body)["items"]
        expected_items = [
            {
                u"title": u"Clube de Regatas do Flamengo",
                u"instance_prefix": u"http://tatipedia.org/",
                u'class_prefix': u'http://tatipedia.org/',
                u"@id": u"http://tatipedia.org/CRF",
                u"resource_id": u"CRF"
            },
            {
                u"title": u'S\xe3o Paulo Futebol Clube',
                u"instance_prefix": u"http://tatipedia.org/",
                u'class_prefix': u'http://tatipedia.org/',
                u"@id": u"http://tatipedia.org/SPFC",
                u"http://tatipedia.org/stadium": u"Morumbi",
                u"resource_id": u"SPFC"
            },
            {
                u"title": u"Cruzeiro Esporte Clube",
                u"instance_prefix": u"http://tatipedia.org/",
                u'class_prefix': u'http://tatipedia.org/',
                u"@id": u"http://tatipedia.org/CEC",
                u"http://tatipedia.org/stadium": u"Toca da Raposa",
                u"resource_id": u"CEC"
            }
        ]
        self.assertEqual(computed_items, expected_items)

    @patch("brainiak.handlers.logger")
    def test_json_returns_sortby_exclude_empty_value(self, log):
        response = self.fetch('/tpedia/SoccerClub/?graph_uri=http://tatipedia.org/&class_prefix=http://tatipedia.org/&sort_by=http://tatipedia.org/stadium&sort_include_empty=0', method='GET')
        self.assertEqual(response.code, 200)
        computed_items = json.loads(response.body)["items"]
        expected_items = [
            {
                u"title": u'S\xe3o Paulo Futebol Clube',
                u"instance_prefix": u"http://tatipedia.org/",
                u'class_prefix': u'http://tatipedia.org/',
                u"@id": u"http://tatipedia.org/SPFC",
                u"http://tatipedia.org/stadium": u"Morumbi",
                u"resource_id": u"SPFC"
            },
            {
                u"title": u"Cruzeiro Esporte Clube",
                u"instance_prefix": u"http://tatipedia.org/",
                u'class_prefix': u'http://tatipedia.org/',
                u"@id": u"http://tatipedia.org/CEC",
                u"http://tatipedia.org/stadium": u"Toca da Raposa",
                u"resource_id": u"CEC"
            }
        ]
        self.assertEqual(computed_items, expected_items)


class FilterInstancesQueryTestCase(QueryTestCase):
    allow_triplestore_connection = True
    fixtures = ["tests/sample/instances.n3"]
    graph_uri = "http://tatipedia.org/"

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql
        triplestore.query_sparql = lambda query, params: query
        self.original_query_filter_instances = get_collection.query_filter_instances
        self.original_query_count_filter_instances = get_collection.query_count_filter_instances

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql
        get_collection.query_filter_instances = self.original_query_filter_instances
        get_collection.query_count_filter_instances = self.original_query_count_filter_instances

    def test_sort_by(self):
        params = Params({
            "class_uri": 'http://tatipedia.org/SoccerClub',
            "p": "?p",
            "o": "?o",
            "sort_by": 'http://tatipedia.org/stadium',
            "sort_order": "asc",
            "sort_include_empty": "1",
            "lang": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
        })
        query = Query(params).to_string()
        computed = self.query(query)["results"]["bindings"]
        expected = [
            {
                u'label': {u'type': u'literal', u'value': u'Clube de Regatas do Flamengo'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/CRF'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'S\xe3o Paulo Futebol Clube'},
                u'sort_object': {u'type': u'literal', u'value': u'Morumbi'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/SPFC'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Cruzeiro Esporte Clube'},
                u'sort_object': {u'type': u'literal', u'value': u'Toca da Raposa'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/CEC'}
            }
        ]
        self.assertEqual(computed, expected)

    def test_sort_by_multiple_predicates(self):
        params = Params({
            "class_uri": 'http://tatipedia.org/SoccerClub',
            "p1": "?p",
            "o1": u'Cruzeiro Esporte Clube',
            "sort_by": 'http://tatipedia.org/stadium',
            "sort_order": "asc",
            "sort_include_empty": "1",
            "lang": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
        })
        query = Query(params).to_string()
        computed = self.query(query)["results"]["bindings"]
        expected = [
            {
                u'label': {u'type': u'literal', u'value': u'Cruzeiro Esporte Clube'},
                u'p': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                u'sort_object': {u'type': u'literal', u'value': u'Toca da Raposa'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/CEC'}
            }
        ]
        self.assertEqual(computed, expected)

    def test_sort_by_exclude_empty_values(self):
        params = Params({
            "class_uri": 'http://tatipedia.org/SoccerClub',
            "p": "?p",
            "o": "?o",
            "sort_by": 'http://tatipedia.org/stadium',
            "sort_order": "asc",
            "sort_include_empty": "0",
            "lang": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
        })
        query = Query(params).to_string()
        computed = self.query(query)["results"]["bindings"]
        expected = [
            {
                u'label': {u'type': u'literal', u'value': u'S\xe3o Paulo Futebol Clube'},
                u'sort_object': {u'type': u'literal', u'value': u'Morumbi'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/SPFC'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Cruzeiro Esporte Clube'},
                u'sort_object': {u'type': u'literal', u'value': u'Toca da Raposa'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/CEC'}
            }
        ]
        self.assertEqual(computed, expected)

    def test_sort_by_p(self):
        params = Params({
            "class_uri": 'http://tatipedia.org/SoccerClub',
            "p": 'http://tatipedia.org/stadium',
            "o": '?o',
            "sort_by": "http://tatipedia.org/stadium",
            "sort_order": "asc",
            "lang": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
        })
        query = Query(params).to_string()
        computed = self.query(query)["results"]["bindings"]
        expected = [
            {
                u'label': {u'type': u'literal', u'value': u'S\xe3o Paulo Futebol Clube'},
                u'o': {u'type': u'literal', u'value': u'Morumbi'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/SPFC'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Cruzeiro Esporte Clube'},
                u'o': {u'type': u'literal', u'value': u'Toca da Raposa'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/CEC'}
            }
        ]
        self.assertEqual(expected, computed)

    def test_sort_by_label_with_different_p(self):
        params = Params({
            "class_uri": 'http://tatipedia.org/SoccerClub',
            "p": 'http://tatipedia.org/stadium',
            "o": '?o',
            "sort_by": "rdfs:label",
            "sort_order": "asc",
            "lang": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
        })
        query = Query(params).to_string()
        computed = self.query(query)["results"]["bindings"]
        expected = [
            {
                u'label': {u'type': u'literal', u'value': u'Cruzeiro Esporte Clube'},
                u'o': {u'type': u'literal', u'value': u'Toca da Raposa'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/CEC'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'S\xe3o Paulo Futebol Clube'},
                u'o': {u'type': u'literal', u'value': u'Morumbi'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/SPFC'}
            }
        ]
        self.assertEqual(expected, computed)

    def test_count_query(self):
        params = Params({
            "class_uri": "http://tatipedia.org/Species",
            "p": "http://tatipedia.org/order",
            "o": "http://tatipedia.org/Monotremata",
            "lang": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
            "sort_by": ""
        })
        query = Query(params).to_string(count=True)
        computed = self.query(query)["results"]["bindings"]
        expected = [{u'total': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer', u'type': u'typed-literal', u'value': u'3'}}]
        self.assertEqual(computed, expected)

    def test_instance_filter_query_by_predicate_and_object(self):
        params = Params({
            "class_uri": "http://tatipedia.org/Person",
            "p": "http://tatipedia.org/likes",
            "o": "http://tatipedia.org/Capoeira",
            "graph_uri": self.graph_uri,
            "lang": "",
            "per_page": "10",
            "page": "0",
            "sort_by": "",
            "sort_order": "asc"
        })
        query = Query(params).to_string()
        computed = self.query(query)["results"]["bindings"]

        expected = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'},
                    u'label': {u'type': u'literal', u'value': u'Mary Land'}}]

        self.assertEqual(computed, expected)

    def test_instance_filter_query_by_object(self):
        params = Params({
            "class_uri": "http://tatipedia.org/Person",
            "p": "?p",
            "o": "http://tatipedia.org/BungeeJump",
            "graph_uri": self.graph_uri,
            "lang": "",
            "per_page": "10",
            "page": "0",
            "sort_by": ""
        })
        query = Query(params).to_string()
        computed = self.query(query)["results"]["bindings"]

        expected = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'},
                     u'label': {u'type': u'literal', u'value': u'Mary Land'},
                     u'p': {u'type': u'uri', u'value': u'http://tatipedia.org/dislikes'}}]
        self.assertEqual(computed, expected)

    def test_instance_filter_query_by_predicate(self):
        params = Params({
            "class_uri": "http://tatipedia.org/Person",
            "graph_uri": self.graph_uri,
            "lang": "",
            "per_page": "10",
            "page": "0",
            "p": "http://tatipedia.org/dislikes",
            "o": "?o",
            "sort_by": "",
        })
        query = Query(params).to_string()
        computed = self.query(query)["results"]["bindings"]
        expected = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'},
                     u'label': {u'type': u'literal', u'value': u'Mary Land'},
                     u'o': {u'type': u'uri', u'value': u'http://tatipedia.org/BungeeJump'}}]

        self.assertEqual(computed, expected)

    def test_instance_filter_query_by_predicate_with_multiple_response(self):
        params = Params({
            "class_uri": "http://tatipedia.org/Person",
            "lang": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
            "p": "http://tatipedia.org/likes",
            "o": "?o",
            "sort_by": ""
        })
        query = Query(params).to_string()
        computed = self.query(query)['results']['bindings']
        expected = [
            {
                u'label': {u'type': u'literal', u'value': u'Mary Land'},
                u'o': {u'type': u'uri', u'value': u'http://tatipedia.org/JiuJitsu'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'John Jones'},
                u'o': {u'type': u'uri', u'value': u'http://tatipedia.org/JiuJitsu'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'Mary Land'},
                u'o': {u'type': u'uri', u'value': u'http://tatipedia.org/Capoeira'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'}
            },
            {
                u'label': {u'type': u'literal', u'value': u'John Jones'},
                u'o': {u'type': u'literal', u'value': u'Aikido'},
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'}
            }
        ]
        self.assertEqual(len(computed), 4)
        self.assertEqual(sorted(computed), sorted(expected))

    def test_instance_filter_query_by_object_represented_as_string(self):
        params = Params({
            "class_uri": "http://tatipedia.org/Person",
            "p": "?p",
            "o": "Aikido",
            "lang": "",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
            "sort_by": ""
        })

        query = query_filter_instances(params)
        computed = self.query(query)["results"]["bindings"]
        expected = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'},
                     u'label': {u'type': u'literal', u'value': u'John Jones'},
                     u'p': {u'type': u'uri', u'value': u'http://tatipedia.org/likes'}
                     }]

        self.assertEqual(computed, expected)

    # def test_instance_filter_in_inexistent_graph(self):
    #     params = {
    #         "class_uri": "http://tatipedia.org/test/Person",
    #         "p": "?p",
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
        params = Params({
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "Ingles",
            "lang": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
            "sort_by": ""
        })
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
        params = Params({
            "class_uri": "http://tatipedia.org/Species",
            "p": "http://tatipedia.org/order",
            "o": "http://tatipedia.org/Monotremata",
            "lang": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
            "sort_by": ""
        })
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
        params = Params({
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "Ingles",
            "lang": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "1",
            "page": "0",
            "sort_by": ""
        })
        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        self.assertEqual(len(computed_bindings), 1)

    def test_query_page_1(self):
        params = Params({
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "Ingles",
            "lang": "pt",
            "graph_uri": self.graph_uri,
            "per_page": "1",
            "page": "1",
            "sort_by": ""
        })
        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        self.assertEqual(len(computed_bindings), 1)

    def test_query_filter_instances_with_language_restriction_to_en(self):
        params = Params({
            "class_uri": "http://tatipedia.org/Place",
            "p": "http://tatipedia.org/speak",
            "o": "?test_filter_with_object_as_string",
            "lang": "en",
            "graph_uri": self.graph_uri,
            "per_page": "10",
            "page": "0",
            "sort_by": ""
        })
        query = query_filter_instances(params)

        computed_bindings = self.query(query)["results"]["bindings"]
        expected_bindings = [
            {
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/london'},
                u'label': {u'xml:lang': u'en', u'type': u'literal', u'value': u'London'},
                u'test_filter_with_object_as_string': {u'type': u'literal', u'value': u'Ingles', u'xml:lang': u'pt'}
            },
            {
                u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/new_york'},
                u'label': {u'xml:lang': u'en', u'type': u'literal', u'value': u'New York'},
                u'test_filter_with_object_as_string': {u'type': u'literal', u'value': u'Ingles', u'xml:lang': u'pt'}
            }
        ]
        self.assertEqual(len(computed_bindings), 2)
        self.assertEqual(sorted(computed_bindings), sorted(expected_bindings))

    @patch("brainiak.collection.get_collection.query_filter_instances", return_value={"results": {"bindings": []}})
    @patch("brainiak.collection.get_collection.query_count_filter_instances", return_value={"results": {"bindings": []}})
    @patch("brainiak.collection.get_collection.class_exists", return_value=True)
    def test_filter_instances_result_is_empty_raises_404(self, mocked_class_exists, mocked_query_count, mocked_query):
        params = Params({
            "o": "",
            "p": "",
            "class_uri": "",
            "sort_by": "",
            'offset': '0',
            'page': '1',
            'per_page': '10'
        })
        result = get_collection.filter_instances(params)
        self.assertEqual(result, None)


class GetCollectionDirectObjectTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):
    fixtures_by_graph = {
        "http://example.onto/": ["tests/sample/animalia.n3"]
    }
    maxDiff = None
    allow_triplestore_connection = True

    @patch("brainiak.collection.get_collection.settings", DEFAULT_RULESET_URI="http://example.onto/ruleset")
    def test_get_collection_includes_indirect_instances(self, settings):
        response = self.fetch('/_/_/?graph_uri=http://example.onto/&class_uri=http://example.onto/Animal', method='GET')
        self.assertEqual(response.code, 200)
        computed_items = json.loads(response.body)["items"]
        expected_items = [
            {
                "resource_id": "Nina",
                "instance_prefix": "http://example.onto/",
                "@id": "http://example.onto/Nina",
                "class_prefix": "_",
                "title": "Nina Fox"
            }
        ]
        self.assertEqual(computed_items, expected_items)

    @patch("brainiak.collection.get_collection.settings", DEFAULT_RULESET_URI="http://example.onto/ruleset")
    def test_get_collection_includes_only_direct_instances(self, settings):
        response = self.fetch('/_/_/?graph_uri=http://example.onto/&class_uri=http://example.onto/Animal&direct_instances_only=1', method='GET')
        self.assertEqual(response.code, 200)
