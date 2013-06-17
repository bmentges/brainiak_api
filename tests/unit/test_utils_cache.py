import unittest

from mock import MagicMock, patch

from brainiak.utils.cache import create, delete, keys, memoize, purge
from tests.mocks import MockRequest


class StrictRedisMock(object):

    def __init__(host=None, port=None, db=None):
        pass


class MemoizeDecoratorTestCase(unittest.TestCase):

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=False)
    @patch("brainiak.utils.cache.create")
    @patch("brainiak.utils.cache.retrieve")
    @patch("brainiak.utils.cache.redis", StrictRedisMock=StrictRedisMock)
    def test_memoize_cache_disabled(self, strict_redis, redis_get, redis_set, settings):

        @memoize
        def clean_up(params):
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = clean_up(params)

        self.assertEquals(answer, {"status": "Laundry done"})
        self.assertEquals(redis_get.call_count, 0)
        self.assertEquals(redis_set.call_count, 0)

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    @patch("brainiak.utils.cache.create", return_value=True)
    @patch("brainiak.utils.cache.retrieve", return_value=None)
    @patch("brainiak.utils.cache.redis", StrictRedisMock=StrictRedisMock)
    def test_memoize_cache_enabled_but_without_cache(self, strict_redis, redis_get, redis_set, settings):

        @memoize
        def clean_up(params):
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = clean_up(params)

        self.assertEquals(answer, {"status": "Laundry done"})
        self.assertEquals(redis_get.call_count, 1)
        self.assertEquals(redis_set.call_count, 1)

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    @patch("brainiak.utils.cache.create", return_value=True)
    @patch("brainiak.utils.cache.retrieve", return_value='{"status": "Dishes cleaned up"}')
    @patch("brainiak.utils.cache.redis", StrictRedisMock=StrictRedisMock)
    def test_memoize_cache_enabled_but_with_cache(self, strict_redis, redis_get, redis_set, settings):

        @memoize
        def clean_up(params):
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = clean_up(params)

        self.assertEquals(answer, {"status": "Dishes cleaned up"})
        self.assertEquals(redis_get.call_count, 1)
        self.assertEquals(redis_set.call_count, 0)


class PurgeTestCase(unittest.TestCase):

    def setUp(self):
        delete("inexistent_url")
        create("some_url", "any value")
        create("some_other_url", "another value")
        create("problematic_key", "another value")

    def tearDown(self):
        delete("problematic_key")
        delete("some_other_url")
        delete("some_url")

    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    def test_cleanup_inexistent_url(self, info, debug):
        purge("inexistent_url")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with('Cache: 0 key(s), matching the pattern: inexistent_url')
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with('Cache: key(s) to be deleted: []')

    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    def test_cleanup_existent_url(self, info, debug):
        purge("some_url")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with('Cache: purged with success 1 key(s), matching the pattern: some_url')
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with("Cache: key(s) to be deleted: ['some_url']")

    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    def test_cleanup_2_existent_url(self, info, debug):
        purge("some")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with('Cache: purged with success 2 key(s), matching the pattern: some')
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with("Cache: key(s) to be deleted: ['some_url', 'some_other_url']")

    @patch("brainiak.utils.cache.delete", return_value=False)
    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    def test_cleanup_fails(self, info, debug, delete):
        purge("problematic_key")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with("Cache: failed purging 1 key(s), matching the pattern: problematic_key")
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with("Cache: key(s) to be deleted: ['problematic_key']")
