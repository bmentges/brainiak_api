# -*- coding: utf-8 -*-

import unittest
from brainiak.sparql_queries import query_class_schema


class QueriesTestCase(unittest.TestCase):

    def test_query_class_schema(self):
        effecive_response = None

        def callback(response):
            global effecive_response
            effecive_response = response

        query_class_schema("http://test.domain.com", callback)
        self.assertEquals(effecive_response, None)
