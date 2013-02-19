# -*- coding: utf-8 -*-

import unittest
from brainiak.schema_resource import query_class_schema, query_cardinalities, query_predicates, query_predicates_without_lang


class QueriesTestCase(unittest.TestCase):

    def test_query_class_schema(self):
        effecive_response = None

        def callback(response):
            global effecive_response
            effecive_response = response

        query_class_schema("http://test.domain.com", callback)
        self.assertEquals(effecive_response, None)

    def test_query_cardinalities(self):
        effecive_response = None

        def callback(response):
            global effecive_response
            effecive_response = response

        query_cardinalities("http://test.domain.com", callback)
        self.assertEquals(effecive_response, None)

    def test_query_predicates(self):
        effecive_response = None

        def callback(response):
            global effecive_response
            effecive_response = response

        query_predicates("http://test.domain.com", callback)
        self.assertEquals(effecive_response, None)

    def test_query_predicates_without_lang(self):
        effecive_response = None

        def callback(response):
            global effecive_response
            effecive_response = response

        query_predicates_without_lang("http://test.domain.com", callback)
        self.assertEquals(effecive_response, None)
