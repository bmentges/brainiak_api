# -*- coding: utf-8 -*-
import unittest
from brainiak.utils import cache

class FlushAllTestCase(unittest.TestCase):

    def test_flushall_after_import_cache(self):
        cache.create('any_key', 1)
        self.assertEqual(cache.retrieve('any_key'), 1)
        cache.flushall()
        self.assertEqual(cache.keys('*'), [])
