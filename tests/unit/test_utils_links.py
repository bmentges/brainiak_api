import unittest
from brainiak.utils.links import *
from brainiak.utils.params import ParamDict
from tests.mocks import MockHandler, MockRequest
from tests.utils import URLTestCase


class SetContentTypeProfileTestCase(unittest.TestCase):
    maxDiff = None

    def test_set_content_type_profile(self):
        self.assertEqual(content_type_profile("http://domain.com?a=1"), "application/json; profile=http://domain.com?a=1")
        self.assertEqual(content_type_profile("http://domain.com#beta?a=1"), "application/json; profile=http://domain.com#beta?a=1")


class TestBuildSchema(unittest.TestCase):

    def test_build_schema(self):
        params = {'page': 1, 'per_page': 2}
        handler = MockHandler(uri="http://any.uri")
        query_params = ParamDict(handler, **params)
        computed = build_schema_url(query_params)
        expected = 'http://any.uri/_schema_list'
        self.assertEqual(expected, computed)

    def test_self_url(self):
        params = {'page': 1, 'per_page': 2}
        handler = MockHandler(uri="http://any.uri")
        query_params = ParamDict(handler, **params)
        computed = self_url(query_params)
        expected = 'http://any.uri'
        self.assertEqual(expected, computed)

    def test_self_url_no_host(self):
        handler = MockHandler(uri="https://127.0.0.1/")
        query_params = ParamDict(handler)
        computed = self_url(query_params)
        expected = 'https://127.0.0.1/'
        self.assertEqual(expected, computed)


class TestLastLink(unittest.TestCase):

    def test_last_link(self):
        params = {'page': 1, 'per_page': 2}
        handler = MockHandler(uri="http://any.uri")
        query_params = ParamDict(handler, **params)
        computed = last_link(query_params, 10)
        expected = [{'href': 'http://any.uri?per_page=2&page=5', 'method': 'GET', 'rel': 'last'}]
        self.assertEqual(computed, expected)


class TestPaginationItems(URLTestCase):

    def test_last_link(self):
        # "page" is related to Virtuoso index (starts in 0)
        params = {'page': 1, 'per_page': 2}
        handler = MockHandler(uri="http://any.uri/", querystring="page=2&per_page=2")
        query_params = ParamDict(handler, **params)
        computed = pagination_items(query_params, 10)
        self.assertEqual(len(computed), 3)
        self.assertQueryStringArgsEqual(computed['_first_args'], 'per_page=2&page=1')
        self.assertQueryStringArgsEqual(computed['_previous_args'], 'per_page=2&page=1')
        self.assertQueryStringArgsEqual(computed['_next_args'], 'page=3&per_page=2')

    def test_pagination_includes_do_item_count(self):
        params = {'page': 1, 'per_page': 2, 'do_item_count': '1'}
        handler = MockHandler(uri="http://any.uri/", querystring="page=2&per_page=2&do_item_count=1")
        query_params = ParamDict(handler, **params)
        computed = pagination_items(query_params, 4)
        self.assertEqual(len(computed), 3)
        self.assertQueryStringArgsEqual(computed['_first_args'], 'per_page=2&page=1&do_item_count=1')
        self.assertQueryStringArgsEqual(computed['_last_args'], 'per_page=2&page=2&do_item_count=1')
        self.assertQueryStringArgsEqual(computed['_previous_args'], 'per_page=2&page=1&do_item_count=1')

    def test_pagination_without_previous_page(self):
        params = {'page': 0, 'per_page': 3}
        handler = MockHandler(uri="http://any.uri/", querystring="page=1&per_page=3")
        query_params = ParamDict(handler, **params)
        computed = pagination_items(query_params, 3)
        self.assertEqual(len(computed), 2)
        self.assertQueryStringArgsEqual(computed['_first_args'], 'per_page=3&page=1')
        self.assertQueryStringArgsEqual(computed['_next_args'], 'per_page=3&page=2')


class TestMergeSchemas(unittest.TestCase):

    def test_merge_schemas(self):
        mutable = {'properties': {'a': 1}, 'links': [1]}
        other = {'properties': {'b': 2}, 'links': [2]}
        expected = {'properties': {'a': 1, 'b': 2}, 'links': [1, 2]}
        merge_schemas(mutable, other)
        self.assertEqual(mutable, expected)


class LinksTestCase(URLTestCase):
    maxDiff = None

    def test_get_previous_page(self):
        self.assertEqual(get_previous_page(1), False)
        self.assertEqual(get_previous_page(5), 4)

    def test_get_next_page(self):
        self.assertEqual(get_next_page(3), 4)

    def test_get_next_page_direct(self):
        self.assertEqual(get_next_page(3, 4), 4)

    def test_get_next_page_false(self):
        self.assertEqual(get_next_page(3, 3), False)

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
        expected = 'http://dot.com?some_url=http://some.url'
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
        expected_items = {"age": ["28"], "weight": ["60"]}
        self.assertQueryStringArgsEqual(computed, expected_items)

    def test_filter_query_string_by_key_prefix_all_three(self):
        query_string = "age_year=28&age_month=10&weight=60"
        computed = filter_query_string_by_key_prefix(query_string, include_prefixes=["a", "weight"])
        expected_items = ["age_year=28", "age_month=10", "weight=60"]
        self.assertEqual(len(computed.split("&")), 3)
        for item in expected_items:
            self.assertIn(item, computed)

    def test_pagination_schema(self):
        computed = pagination_schema("/")
        expected = {
            'links': [
                {
                    'href': '?{+_first_args}',
                    'method': 'GET',
                    'rel': 'first'
                },
                {
                    'href': '?{+_previous_args}',
                    'method': 'GET',
                    'rel': 'previous'
                },
                {
                    'href': '?{+_next_args}',
                    'method': 'GET',
                    'rel': 'next'
                },
                {
                    'href': '?{+_last_args}',
                    'method': 'GET',
                    'rel': 'last'
                }
            ],
            'properties': {
                '_first_args': {'type': 'string'},
                '_next_args': {'type': 'string'},
                '_previous_args': {'type': 'string'},
                '_last_args': {'type': 'string'}
            }
        }
        self.assertEqual(computed, expected)

    def test_self_url(self):
        request = MockRequest(uri="/relative_url")
        request.host = "some.host"
        request.protocol = "http"
        computed = self_url({"request": request})
        expected = 'http://some.host/relative_url'
        self.assertEqual(computed, expected)

    def test_remove_last_slash_when_it_exists(self):
        computed = remove_last_slash("http://last.slash/")
        expected = "http://last.slash"
        self.assertEqual(computed, expected)

    def test_remove_last_slash_when_it_doesnt_exist(self):
        computed = remove_last_slash("http://withoutlast.slash")
        expected = "http://withoutlast.slash"
        self.assertEqual(computed, expected)


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

    def test_crud_links_without_params_ok(self):
        params = {'instance_id': 'instance', 'context_name': 'context', 'class_name': 'Class'}
        handler = MockHandler(uri="http://any.uri/context/Class/instance", **params)
        query_params = ParamDict(handler, **params)
        computed = crud_links(query_params)
        expected = [
            {'href': 'http://any.uri/context/Class/{_resource_id}', 'method': 'DELETE', 'rel': 'delete'},
            {'href': 'http://any.uri/context/Class/{_resource_id}', 'method': 'PUT', 'rel': 'update', 'schema': {'$ref': 'http://any.uri/context/Class/_schema'}}]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_crud_links_with_params_ok(self):
        params = {'instance_id': 'instance', 'context_name': 'context', 'class_name': 'Class'}
        handler = MockHandler(uri="http://any.uri/context/Class/instance", querystring="lang=en", **params)
        query_params = ParamDict(handler, **params)
        computed = crud_links(query_params)
        expected = [
            {'href': 'http://any.uri/context/Class/{_resource_id}?instance_prefix={_instance_prefix}&lang=en', 'method': 'DELETE', 'rel': 'delete'},
            {'href': 'http://any.uri/context/Class/{_resource_id}?instance_prefix={_instance_prefix}&lang=en', 'method': 'PUT', 'rel': 'update', 'schema': {'$ref': 'http://any.uri/context/Class/_schema'}}]
        self.assertEqual(sorted(computed), sorted(expected))

    def test_crud_links_with_schema_url(self):
        params = {'instance_id': 'instance', 'context_name': 'context', 'class_name': 'Class'}
        handler = MockHandler(uri="/something", **params)
        query_params = ParamDict(handler, **params)
        response = crud_links(query_params, "/_something_schema")
        expected = [
            {
                'href': ':///context/Class/{_resource_id}',
                'method': 'DELETE',
                'rel': 'delete'
            },
            {
                'href': ':///context/Class/{_resource_id}',
                'method': 'PUT',
                'rel': 'update',
                'schema': {'$ref': '/_something_schema'}
            }
        ]
        self.assertEqual(response, expected)


class BuildClassUrlTestCase(unittest.TestCase):
    maxDiff = None

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
        self.assertEqual(computed, expected)

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
        computed = build_class_url(query_params, include_query_string=True)
        expected = "https://dot.net/place/City?class_prefix=include_me"
        self.assertEqual(computed, expected)

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
        computed = build_schema_url_for_instance(query_params)
        expected = "https://dot.net/place/City/_schema?class_prefix=include_me"
        self.assertEqual(computed, expected)

    def test_build_schema_url_with_class_uri(self):

        class MockRequest(object):
            protocol = "https"
            host = "dot.net"
            query = "?instance_uri=ignore_me"

        query_params = {
            "request": MockRequest(),
            "context_name": "place",
            "class_name": "_",
            "class_uri": "place:City"
        }
        computed = build_schema_url_for_instance(query_params)
        expected = "https://dot.net/place/_/_schema?class_uri=place:City"
        self.assertEqual(computed, expected)

    def test_build_schema_url_with_graph_uri_and_class_uri(self):

        class MockRequest(object):
            protocol = "https"
            host = "dot.net"
            query = "?instance_uri=ignore_me"

        query_params = {
            "request": MockRequest(),
            "context_name": "_",
            "graph_uri": "place",
            "class_name": "_",
            "class_uri": "place:City"
        }
        computed = build_schema_url_for_instance(query_params)
        expected = "https://dot.net/_/_/_schema?graph_uri=place&class_uri=place:City"
        self.assertEqual(computed, expected)
