import unittest
from urllib import urlencode
from brainiak import settings
from brainiak.utils.links import *
from brainiak.utils.params import ParamDict, LIST_PARAMS, DefaultParamsDict
from tests.mocks import MockHandler


class LinksTestCase(unittest.TestCase):
    maxDiff = None

    def test_get_previous_page(self):
        self.assertEqual(get_previous_page(1), False)
        self.assertEqual(get_previous_page(5), 4)

    def test_get_next_page(self):
        self.assertEqual(get_next_page(3, 3), False)
        self.assertEqual(get_next_page(9, 20), 10)

    def test_get_last_page_exact_division(self):
        total_items = 7
        per_page = 7
        computed = get_last_page(total_items, per_page)
        expected = 1
        self.assertEqual(computed, expected)

    def test_get_last_page_exact_division(self):
        total_items = 12
        per_page = 4
        computed = get_last_page(total_items, per_page)
        expected = 3
        self.assertEqual(computed, expected)

    def test_get_last_page_different(self):
        total_items = 11
        per_page = 3
        computed = get_last_page(total_items, per_page)
        expected = 4
        self.assertEqual(computed, expected)

    def test_split_into_chunks_empty(self):
        items = []
        computed_chunks = split_into_chunks(items, 1)
        expected_chunks = []
        self.assertEqual(computed_chunks, expected_chunks)

    def test_split_into_chunks_exact(self):
        items = ['a', 'b', 'c', 'd', 'e', 'f']
        computed_chunks = split_into_chunks(items, 2)
        expected_chunks = [['a', 'b'], ['c', 'd'], ['e', 'f']]
        self.assertEqual(computed_chunks, expected_chunks)

    def test_split_into_chunks_non_exact(self):
        items = ['a', 'b', 'c', 'd', 'e']
        computed_chunks = split_into_chunks(items, 3)
        expected_chunks = [['a', 'b', 'c'], ['d', 'e']]
        self.assertEqual(computed_chunks, expected_chunks)

    def test_assemble_url_with_dict_and_url_key(self):
        url = "http://dot.com"
        params = {"some_url": "http://some.url"}
        computed = assemble_url(url, params)
        expected = "http://dot.com?some_url=http%3A%2F%2Fsome.url"
        self.assertEqual(computed, expected)

    def test_assemble_url_with_dict_and_literal_key(self):
        url = "http://dot.com"
        params = {"key": "value"}
        computed = assemble_url(url, params)
        expected = "http://dot.com?key=value"
        self.assertEqual(computed, expected)

    def test_assemble_url_containing_query_string_with_string(self):
        url = "http://dot.com?exists=previously"
        params = {}
        computed = assemble_url(url, params)
        expected = "http://dot.com?exists=previously"
        self.assertEqual(computed, expected)

    def test_filter_query_string_by_key_prefix_return_empty(self):
        query_string = "age=28&weight=60"
        computed = filter_query_string_by_key_prefix(query_string, include_prefixes=[])
        expected = ""
        self.assertEqual(computed, expected)

    def test_filter_query_string_by_key_prefix_one_of_two(self):
        query_string = "age=28&weight=60"
        computed = filter_query_string_by_key_prefix(query_string, include_prefixes=["a"])
        expected = "age=28"
        self.assertEqual(computed, expected)

    def test_filter_query_string_by_key_prefix_all_two(self):
        query_string = "age=28&weight=60"
        computed = filter_query_string_by_key_prefix(query_string, include_prefixes=["a", "weight"])
        expected_items = ["age=28", "weight=60"]
        self.assertEqual(len(computed.split("&")), 2)
        for item in expected_items:
            self.assertIn(item, computed)

    def test_filter_query_string_by_key_prefix_all_three(self):
        query_string = "age_year=28&age_month=10&weight=60"
        computed = filter_query_string_by_key_prefix(query_string, include_prefixes=["a", "weight"])
        expected_items = ["age_year=28", "age_month=10", "weight=60"]
        self.assertEqual(len(computed.split("&")), 3)
        for item in expected_items:
            self.assertIn(item, computed)


class AddLinksTestCase(unittest.TestCase):
    maxDiff = None

    def test_add_link(self):
        link_list = []
        expected_link_list = [{'rel': 'rel_key', 'method': 'GET', 'href': 'http://A/B', 'foo': 'bar'}]
        add_link(link_list, "rel_key", "http://A/B", foo='bar')
        self.assertEqual(link_list, expected_link_list)

    def test_add_link_with_exact_href(self):
        link_list = []
        expected_link_list = [{'rel': 'rel_key', 'method': 'GET', 'href': 'http://A/B'}]
        add_link(link_list, "rel_key", "http://A/B")
        self.assertEqual(link_list, expected_link_list)


class CrudLinksTestCase(unittest.TestCase):
    maxDiff = None

    def test_crud_links_with_params_ok(self):
        params = {'instance_id': 'instance', 'context_name': 'context', 'class_name': 'Class'}
        handler = MockHandler(uri="http://any.uri/context/Class/instance", **params)
        query_params = ParamDict(handler, **params)
        computed = crud_links(query_params)
        expected = [
            {'href': 'http://any.uri/context/Class/instance', 'method': 'DELETE', 'rel': 'delete'},
            {'href': 'http://any.uri/context/Class/instance', 'method': 'PUT', 'rel': 'replace', 'schema': {'$ref': 'http://any.uri/context/Class/_schema'}}]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_build_class_url_without_querystring(self):

        class MockRequest(object):
            protocol = "https"
            host = "dot.net"

        query_params = {
            "request": MockRequest(),
            "context_name": "place",
            "class_name": "City"

        }
        computed = build_class_url(query_params)
        expected = "https://dot.net/place/City"

    def test_build_class_url_with_querystring(self):

        class MockRequest(object):
            protocol = "https"
            host = "dot.net"
            query = "?instance_uri=ignore_me&class_prefix=include_me"

        query_params = {
            "request": MockRequest(),
            "context_name": "place",
            "class_name": "City"

        }
        computed = build_class_url(query_params)
        expected = "https://dot.net/place/City?class_prefix=include_me"

    def test_build_schema_url(self):

        class MockRequest(object):
            protocol = "https"
            host = "dot.net"
            query = "?instance_uri=ignore_me&class_prefix=include_me"

        query_params = {
            "request": MockRequest(),
            "context_name": "place",
            "class_name": "City"

        }
        computed = build_schema_url(query_params)
        expected = "https://dot.net/place/City/_schema?class_prefix=include_me"


class CollectionLinksTestCase(unittest.TestCase):
    maxDiff = None

    def test_build_links_without_previous_without_next(self):
        total_items = 1
        handler = MockHandler(uri="http://class.uri")
        params = {'page': 1, 'per_page': 1}
        query_params = ParamDict(handler, **params)
        computed = collection_links(query_params, total_items)
        expected = [
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'first'},
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'last'},
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'previous'}]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_build_links_without_previous_with_next(self):
        total_items = 2
        params = {'page': 1, 'per_page': 1}
        handler = MockHandler(uri="http://class.uri", **params)
        query_params = ParamDict(handler, **params)
        computed = collection_links(query_params, total_items)
        expected = [
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'first'},
            {'href': 'http://class.uri?per_page=1&page=2', 'method': 'GET', 'rel': 'last'},
            {'href': 'http://class.uri?per_page=1&page=2', 'method': 'GET', 'rel': 'next'}]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_build_links_with_previous_without_next(self):
        total_items = 2
        params = {'page': 2, 'per_page': 1}
        handler = MockHandler(uri="http://class.uri", **params)
        query_params = ParamDict(handler, **params)
        computed = collection_links(query_params, total_items)
        expected = [
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'first'},
            {'href': 'http://class.uri?per_page=1&page=2', 'method': 'GET', 'rel': 'last'},
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'previous'}]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_build_links_with_previous_with_next(self):
        total_items = 3
        params = {'page': 2, 'per_page': 1}
        handler = MockHandler(uri="http://class.uri", **params)
        query_params = ParamDict(handler, **params)
        computed = collection_links(query_params, total_items)
        expected = [
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'first'},
            {'href': 'http://class.uri?per_page=1&page=3', 'method': 'GET', 'rel': 'last'},
            {'href': 'http://class.uri?per_page=1&page=3', 'method': 'GET', 'rel': 'next'},
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'previous'}]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_build_links_with_param_instance_prefix(self):
        total_items = 3
        url_params = DefaultParamsDict(instance_prefix='http://semantica.globo.com/base/')
        params = DefaultParamsDict(context_name='dbpedia',
                                   class_name='People',
                                   instance_id='inst')
        handler = MockHandler(uri="http://class.uri", **url_params)
        query_params = ParamDict(handler, **(LIST_PARAMS + url_params + params))
        computed = collection_links(query_params, total_items)
        all_args = {'per_page': settings.DEFAULT_PER_PAGE,
                    'page': '1'}
        all_args.update(url_params)
        all_args_str = urlencode(all_args, doseq=True)
        expected = [
            {'href': 'http://class.uri?{0}'.format(all_args_str), 'method': 'GET', 'rel': 'first'},
            {'href': 'http://class.uri?{0}'.format(all_args_str), 'method': 'GET', 'rel': 'last'}]

        self.assertEqual(sorted(computed), sorted(expected))
