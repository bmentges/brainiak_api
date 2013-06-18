import unittest

import redis

from mock import MagicMock, patch

from brainiak.utils.cache import CacheError, connect, create, delete, keys, memoize, ping, purge, retrieve, safe_redis, status
from tests.mocks import MockRequest


def raise_exception():
    raise CacheError


def raise_connection_exception():
    raise redis.connection.ConnectionError


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


class GeneralFunctionsTestCase(unittest.TestCase):

    def setUp(self):
        create("key_xubiru", "value")
        create("key_xubiru2", "value")

    def tearDown(self):
        delete("key_xubiru")
        delete("new_key")

    def test_create(self):
        response = create("new_key", "some value")
        self.assertTrue(response)

    def test_retrieve(self):
        response = retrieve("key_xubiru")
        self.assertEqual(response, "value")

    def test_delete(self):
        response = delete("key_xubiru")
        self.assertTrue(response)

    def test_keys(self):
        response = keys("key_xubiru")
        self.assertEqual(sorted(response), ["key_xubiru", "key_xubiru2"])

    def test_connect(self):
        response = connect()
        self.assertIsInstance(response, redis.client.StrictRedis)

    @patch("brainiak.utils.cache.redis_client.ping", return_value=True)
    def test_ping(self, ping_):
        self.assertEqual(ping(), True)

    @patch("brainiak.utils.cache.ping", return_value=True)
    def test_status_success(self, ping):
        response = status()
        expected = 'Redis connection authenticated [:j\xdf\x97\xf8:\xcfdS\xd4\xa6\xa4\xb1\x07\x0f7T] | SUCCEED | localhost:6379'
        self.assertEqual(response, expected)

    @patch("brainiak.utils.cache.ping", return_value=False)
    def test_status_fail(self, ping):
        response = status()
        expected = 'Redis connection authenticated [:j\xdf\x97\xf8:\xcfdS\xd4\xa6\xa4\xb1\x07\x0f7T] | FAILED | localhost:6379 | Ping failed'
        self.assertEqual(response, expected)

    @patch("brainiak.utils.cache.ping", side_effect=raise_exception)
    def test_status_exception(self, ping):
        response = status()
        expected = "Redis connection authenticated [:j\xdf\x97\xf8:\xcfdS\xd4\xa6\xa4\xb1\x07\x0f7T] | FAILED | localhost:6379 | Traceback (most recent call last)"
        self.assertIn(expected, response)

    @patch("brainiak.utils.cache.ping", side_effect=raise_connection_exception)
    def test_status_exception_connection(self, ping):
        response = status()
        expected = "Redis connection authenticated [:j\xdf\x97\xf8:\xcfdS\xd4\xa6\xa4\xb1\x07\x0f7T] | FAILED | localhost:6379 | Traceback (most recent call last)"
        self.assertIn(expected, response)


class SafeRedisTestCase(unittest.TestCase):

    def setUp(self):
        self.ncalls = 0

    @patch("brainiak.utils.cache.connect")
    @patch("brainiak.utils.cache.redis_client.ping", return_value=True)
    def test_safe_redis_fails_first_time_passes_second(self, ping, connect):

        @safe_redis
        def some_function(self):
            if not self.ncalls:
                self.ncalls += 1
                raise CacheError
            else:
                return "xubi"

        response = some_function(self)
        self.assertEqual(response, "xubi")

    @patch("brainiak.utils.cache.connect")
    @patch("brainiak.utils.cache.redis_client.ping", return_value=True)
    def test_safe_redis_passes_first_time(self, ping, connect):

        @safe_redis
        def some_function(self):
            return "ru"

        response = some_function(self)
        self.assertEqual(response, "ru")

    @patch("brainiak.utils.cache.log.logger.error")
    @patch("brainiak.utils.cache.connect")
    @patch("brainiak.utils.cache.redis_client.ping", return_value=True)
    def test_safe_redis_fails_all_times(self, ping, connect, error):

        @safe_redis
        def some_function(self):
            raise CacheError

        response = some_function(self)
        self.assertIsNone(response)
        self.assertIn('CacheError: Second try returned Traceback', str(error.call_args))
