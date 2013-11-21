# -*- coding: utf-8 -*-
import unittest
import redis
import sys
from brainiak import settings


class FlushAllTestCase(unittest.TestCase):

    def setUp(self):
        self.redis_client = redis.StrictRedis(host=settings.REDIS_ENDPOINT,
                                              port=settings.REDIS_PORT,
                                              password=settings.REDIS_PASSWORD,
                                              db=0)
        try:
            del sys.modules['brainiak.utils.cache']
        except:
            pass

    def test_flushall_after_import_cache(self):
        self.redis_client.set('any_key', 1)
        self.assertEqual(self.redis_client.get('any_key'), '1')
        from brainiak.utils import cache
        self.assertEqual(self.redis_client.keys('*'), [])

    def test_reimport_cache_without_flushall(self):
        self.redis_client.set('any_key', 1)
        import brainiak.utils.cache
        self.assertEqual(self.redis_client.keys('*'), [])
        self.redis_client.set('any_key', 1)
        import brainiak.utils.cache
        self.assertEqual(self.redis_client.get('any_key'), '1')
