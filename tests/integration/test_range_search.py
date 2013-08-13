# -*- coding: utf-8 -*-
import json
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class TestRangeSearch(TornadoAsyncHTTPTestCase):

    def test_range_search_with_required_params(self):
        response = self.fetch('/_range_search?pattern=12&predicate=Override')
        self.assertEqual(response.code, 200)
        json_received = json.loads(response.body)
        self.assertEqual(json_received, {})

    def test_range_search_without_required_param_predicate(self):
        response = self.fetch('/_range_search?pattern=12')
        self.assertEqual(response.code, 400)
        json_received = json.loads(response.body)
        self.assertEqual(json_received['error'], "HTTP error: 400\nRequired parameter (predicate) was not given, received just: pattern")
