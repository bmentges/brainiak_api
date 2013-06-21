import unittest

import redis

from mock import MagicMock, patch

from brainiak.utils.cache import CacheError, connect, memoize, ping, safe_redis, status
from tests.mocks import MockRequest


def raise_exception():
    raise CacheError


def raise_connection_exception():
    raise redis.connection.ConnectionError


class StrictRedisMock(object):

    def __init__(host=None, port=None, db=None):
        pass


class MemoizeTestCase(unittest.TestCase):

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=False)
    @patch("brainiak.utils.cache.create")
    @patch("brainiak.utils.cache.retrieve")
    @patch("brainiak.utils.cache.redis", StrictRedisMock=StrictRedisMock)
    def test_memoize_cache_disabled(self, strict_redis, redis_get, redis_set, settings):

        def clean_up(params):
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = memoize(clean_up, params)

        self.assertEqual(answer["body"], {"status": "Laundry done"})
        self.assertTrue(answer["meta"])
        self.assertEqual(redis_get.call_count, 0)
        self.assertEqual(redis_set.call_count, 0)

    @patch("brainiak.utils.cache.current_time", return_value='Fri, 11 May 1984 20:00:00 -0300')
    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    @patch("brainiak.utils.cache.create", return_value=True)
    @patch("brainiak.utils.cache.retrieve", return_value=None)
    @patch("brainiak.utils.cache.redis", StrictRedisMock=StrictRedisMock)
    def test_memoize_cache_enabled_but_without_cache(self, strict_redis, redis_get, redis_set, settings, isoformat):

        def clean_up(params):
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = memoize(clean_up, params)

        expected = {
            'body': {"status": "Laundry done"},
            'meta': {
                'last_modified': 'Fri, 11 May 1984 20:00:00 -0300',
                'cache': 'MISS'
            }
        }
        self.assertEqual(answer, expected)
        self.assertEqual(redis_get.call_count, 1)
        self.assertEqual(redis_set.call_count, 1)

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    @patch("brainiak.utils.cache.create", return_value=True)
    @patch("brainiak.utils.cache.retrieve", return_value={"status": "Dishes cleaned up", "meta": {}})
    @patch("brainiak.utils.cache.redis", StrictRedisMock=StrictRedisMock)
    def test_memoize_cache_enabled_but_miss(self, strict_redis, redis_get, redis_set, settings):

        def clean_up(params):
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = memoize(clean_up, params)

        self.assertEqual(answer, {"status": "Dishes cleaned up", "meta": {"cache": "HIT"}})
        self.assertEqual(redis_get.call_count, 1)
        self.assertEqual(redis_set.call_count, 0)


class GeneralFunctionsTestCase(unittest.TestCase):

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
