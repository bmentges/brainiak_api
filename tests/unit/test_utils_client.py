# -*- coding: utf-8 -*-

from unittest import TestCase
from brainiak.utils.client import extract_keys, requests, fetch_page, fetch_all_pages
from brainiak.utils import client


class MockRequest(object):

    def __init__(self, status_code, json):
        self.status_code = status_code
        self._json = json

    def __call__(self, *args, **kw):
        return self

    def json(self):
        return self._json


class ClientTestCase(TestCase):

    def setUp(self):
        self.original_get = requests.get

    def tearDown(self):
        requests.get = self.original_get

    def test_extract_keys(self):
        expected_response = [1, 2, 3]
        response = extract_keys([{'a': 1}, {'a': 2}, {'a': 3}], 'a')
        self.assertEqual(expected_response, response)

    def test_fetch_page(self):
        expected_json_dict = {"a", 1}
        requests.get = MockRequest(status_code=200, json=expected_json_dict)
        status_code, json_response = fetch_page("http://localhost:5100")
        self.assertEqual(status_code, 200)
        self.assertEqual(json_response, expected_json_dict)


class MockFetchPage(object):
    def __init__(self, status_code, max_pages):
        self.count = 0
        self.status_code = status_code
        self.max_pages = max_pages
    def __call__(self, *args, **kw):
        self.count += 1
        if self.count >= self.max_pages:
            links = []
        else:
            links = [{'href': "/?page=1", 'method': "GET", 'rel': "next"}]
        return self.status_code, {"items": [self.count], "links":links}


class AllPagesTestCase(TestCase):

    def setUp(self):
        self.original_fetch_page = client.fetch_page

    def tearDown(self):
        client.fetch_page = self.original_fetch_page

    def test_fetch_all(self):
        client.fetch_page = MockFetchPage(200, 5)
        expected_items = fetch_all_pages("http://localhost:5100", "items")
        self.assertEqual(expected_items, [1, 2, 3, 4, 5])

    def test_fetch_all_fails(self):
        client.fetch_page = MockFetchPage(500, 5)
        self.assertRaises(Exception, fetch_all_pages, "http://anyurl.com", "any_key")
