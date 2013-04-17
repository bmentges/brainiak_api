import unittest

from brainiak.utils.links import crud_links, get_last_page, get_next_page, get_previous_page, split_into_chunks, add_link, collection_links
from brainiak.utils.params import ParamDict
from tests.mocks import MockHandler


class LinksTestCase(unittest.TestCase):
    maxDiff = None

    def test_add_link(self):
        link_list = []
        expected_link_list = [{'rel': 'rel_key', 'method': 'GET', 'href': 'http://A/B'}]
        add_link(link_list, "rel_key", "http://{a}/{b}", a="A", b="B")
        self.assertEqual(link_list, expected_link_list)

    def test_add_link_with_exact_href(self):
        link_list = []
        expected_link_list = [{'rel': 'rel_key', 'method': 'GET', 'href': 'http://A/B'}]
        add_link(link_list, "rel_key", "http://A/B")
        self.assertEqual(link_list, expected_link_list)

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

    def test_build_links_without_previous_without_next(self):
        total_items = 1
        handler = MockHandler(uri="http://class.uri")
        params = {'page': 1, 'per_page': 1}
        query_params = ParamDict(handler, **params)
        computed = collection_links(query_params, total_items)
        expected = [
            {'href': 'http://class.uri', 'method': 'POST', 'rel': 'create'},
            {'href': 'http://class.uri/{resource_id}', 'method': 'GET', 'rel': 'item'},
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
            {'href': 'http://class.uri', 'method': 'POST', 'rel': 'create'},
            {'href': 'http://class.uri/{resource_id}', 'method': 'GET', 'rel': 'item'},
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
            {'href': 'http://class.uri', 'method': 'POST', 'rel': 'create'},
            {'href': 'http://class.uri/{resource_id}', 'method': 'GET', 'rel': 'item'},
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
            {'href': 'http://class.uri', 'method': 'POST', 'rel': 'create'},
            {'href': 'http://class.uri/{resource_id}', 'method': 'GET', 'rel': 'item'},
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'first'},
            {'href': 'http://class.uri?per_page=1&page=3', 'method': 'GET', 'rel': 'last'},
            {'href': 'http://class.uri?per_page=1&page=3', 'method': 'GET', 'rel': 'next'},
            {'href': 'http://class.uri?per_page=1&page=1', 'method': 'GET', 'rel': 'previous'}]
        self.assertEqual(sorted(computed), sorted(expected))

    # def test_build_links_with_param_instance_prefix(self):
    #     total_items = 3
    #     params = {'instance_prefix': 'base'}
    #     handler = MockHandler(uri="http://class.uri", **params)
    #     query_params = ParamDict(handler, **params)
    #     computed = collection_links(query_params, total_items)
    #     expected = [
    #         {'href': 'http://class.uri', 'method': 'POST', 'rel': 'create'},
    #         {'href': 'http://class.uri/{resource_id}', 'method': 'GET', 'rel': 'item'},
    #         {'href': 'http://class.uri?instance_prefix=base', 'method': 'GET', 'rel': 'first'},
    #         {'href': 'http://class.uri?instance_prefix=base', 'method': 'GET', 'rel': 'last'},
    #         {'href': 'http://class.uri?instance_prefix=base', 'method': 'GET', 'rel': 'next'},
    #         {'href': 'http://class.uri?instance_prefix=base', 'method': 'GET', 'rel': 'previous'}]
    #     self.assertEqual(sorted(computed), sorted(expected))

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


# def test_build_json(self):
#     contexts = ["a", "b", "c"]
#     params = {"per_page": "3", "page": "0"}
#     total_items = 6
#     request = MockRequest(uri='http://localhost:5100/')
#     computed = build_json(contexts, total_items, params, request)
#     self.assertEqual(computed['items'], ["a", "b", "c"])
#     self.assertEqual(computed['item_count'], 6)
#     expected_links = [
#         {'rel': 'self', 'href': 'http://localhost:5100/'},
#         {'rel': 'instances', 'href': 'http://localhost:5100/'},
#         {'rel': 'item', 'href': 'http://localhost:5100/{resource_id}'},
#         {'rel': 'create', 'href': 'http://localhost:5100/', 'method': 'POST'},
#         {'rel': 'delete', 'href': 'http://localhost:5100/{resource_id}', 'method': 'DELETE'},
#         {'rel': 'replace', 'href': 'http://localhost:5100/{resource_id}', 'method': 'PUT'},
#         {'rel': 'first', 'href': 'http://localhost:5100/?page=1', 'method': 'GET'},
#         {'rel': 'last', 'href': 'http://localhost:5100/?page=2', 'method': 'GET'},
#         {'rel': 'next', 'href': 'http://localhost:5100/?page=2', 'method': 'GET'}
#     ]
#     self.assertEqual(computed['links'], expected_links)
