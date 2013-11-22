# -*- coding: utf-8 -*-

from unittest import TestCase
from brainiak.utils.client import fetch_all_pages, extract_keys


API_ENDPOINT = "http://brainiak.semantica.dev.globoi.com"


class AcceptListContexts(TestCase):

    def test_successful_list_context(self):
        response_items = fetch_all_pages(API_ENDPOINT, 'items')
        titles = extract_keys(response_items, "title")
        self.assertIn(u'glb', titles)
        self.assertIn(u'base', titles)
        self.assertIn(u'upper', titles)
        self.assertIn(u'place', titles)
        self.assertIn(u'person', titles)
        self.assertIn(u'organization', titles)
