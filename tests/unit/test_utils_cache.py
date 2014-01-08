import logging
import unittest

import redis
from mock import patch, Mock

from brainiak.utils.cache import build_key_for_class, CacheError, connect, memoize, ping, purge_by_path, safe_redis, status, build_instance_key
from brainiak.utils.params import ParamDict
from tests.mocks import MockRequest, MockHandler


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
    @patch("brainiak.utils.cache.redis", StrictRedis=StrictRedisMock)
    def test_memoize_cache_disabled(self, strict_redis, redis_get, redis_set, settings):

        def clean_up():
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = memoize(params, clean_up)

        self.assertEqual(answer["body"], {"status": "Laundry done"})
        self.assertTrue(answer["meta"])
        self.assertEqual(redis_get.call_count, 0)
        self.assertEqual(redis_set.call_count, 0)

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=False)
    @patch("brainiak.utils.cache.create")
    @patch("brainiak.utils.cache.retrieve")
    @patch("brainiak.utils.cache.redis", StrictRedis=StrictRedisMock)
    def test_memoize_cache_disabled_delegatee_receive_params(self, strict_redis, redis_get, redis_set, settings):

        def clean_up(param_value):
            return {"status": param_value}

        params = {'request': MockRequest(uri="/home")}
        param_to_clean_up = 'It was received by the wrapped function'
        answer = memoize(params, clean_up, function_arguments=param_to_clean_up)

        self.assertEqual(answer["body"], {"status": param_to_clean_up})
        self.assertTrue(answer["meta"])
        self.assertEqual(redis_get.call_count, 0)
        self.assertEqual(redis_set.call_count, 0)

    @patch("brainiak.utils.cache.current_time", return_value='Fri, 11 May 1984 20:00:00 -0300')
    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    @patch("brainiak.utils.cache.create", return_value=True)
    @patch("brainiak.utils.cache.retrieve", return_value=None)
    @patch("brainiak.utils.cache.redis", StrictRedis=StrictRedisMock)
    def test_memoize_cache_enabled_but_without_cache(self, strict_redis, redis_get, redis_set, settings, isoformat):

        def clean_up():
            return {"status": "Laundry done"}

        params = Mock(request=MockRequest(uri="/home"))
        answer = memoize(params, clean_up)

        expected = {
            'body': {"status": "Laundry done"},
            'meta': {
                'cache': 'MISS',
                'last_modified': 'Fri, 11 May 1984 20:00:00 -0300'
            }
        }
        self.assertEqual(answer, expected)
        self.assertEqual(redis_get.call_count, 1)
        self.assertEqual(redis_set.call_count, 1)

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    @patch("brainiak.utils.cache.create", return_value=True)
    @patch("brainiak.utils.cache.retrieve", return_value={"status": "Dishes cleaned up", "meta": {}})
    @patch("brainiak.utils.cache.redis", StrictRedis=StrictRedisMock)
    def test_memoize_cache_enabled_and_hit(self, strict_redis, redis_get, redis_set, settings):

        def clean_up():
            return {"status": "Laundry done"}

        params = Mock(request=MockRequest(uri="/home"))
        answer = memoize(params, clean_up)
        self.assertEqual(answer['status'], "Dishes cleaned up")
        self.assertEqual(redis_get.call_count, 1)


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
        expected = 'Redis connection authenticated [:\xf3\xf9\x8c]A\xd7\xc9\x92\xa6\xfbcy\x9fp\x0f+] | SUCCEED | localhost:6379'
        self.assertEqual(response, expected)

    @patch("brainiak.utils.cache.ping", return_value=False)
    def test_status_fail(self, ping):
        response = status()
        expected = 'Redis connection authenticated [:\xf3\xf9\x8c]A\xd7\xc9\x92\xa6\xfbcy\x9fp\x0f+] | FAILED | localhost:6379 | Ping failed'
        self.assertEqual(response, expected)

    @patch("brainiak.utils.cache.ping", side_effect=raise_exception)
    def test_status_exception(self, ping):
        response = status()
        expected = "Redis connection authenticated [:\xf3\xf9\x8c]A\xd7\xc9\x92\xa6\xfbcy\x9fp\x0f+] | FAILED | localhost:6379 | Traceback (most recent call last)"
        self.assertIn(expected, response)

    @patch("brainiak.utils.cache.ping", side_effect=raise_connection_exception)
    def test_status_exception_connection(self, ping):
        response = status()
        expected = "Redis connection authenticated [:\xf3\xf9\x8c]A\xd7\xc9\x92\xa6\xfbcy\x9fp\x0f+] | FAILED | localhost:6379 | Traceback (most recent call last)"
        self.assertIn(expected, response)


class SafeRedisTestCase(unittest.TestCase):

    def setUp(self):
        self.ncalls = 0

    @patch("brainiak.utils.cache.log.logger.error")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    @patch("brainiak.utils.cache.connect")
    @patch("brainiak.utils.cache.redis_client.ping", return_value=True)
    def test_safe_redis_fails_first_time_passes_second(self, ping, connect, logger, error):

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

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.utils.cache.log.logger.error")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    @patch("brainiak.utils.cache.connect")
    @patch("brainiak.utils.cache.redis_client.ping", return_value=True)
    def test_safe_redis_fails_all_times(self, ping, connect, logger, error, settings):

        @safe_redis
        def some_function(self):
            raise CacheError

        response = some_function(self)
        self.assertIsNone(response)
        self.assertIn('CacheError: Second try returned Traceback', str(error.call_args))


class CacheUtilsTestCase(unittest.TestCase):

    def test_build_key_for_class(self):
        params = {
            "graph_uri": "graph",
            "class_uri": "Class"
        }
        computed = build_key_for_class(params)
        expected = "graph@@Class##class"
        self.assertEqual(computed, expected)

    def test_build_key_for_instance(self):
        url_params = dict(graph_uri="graph", class_uri="Class", instance_uri="instance")
        handler = MockHandler(**url_params)
        params = ParamDict(handler, **url_params)
        computed = build_instance_key(params)
        expected = "_@@_@@instance@@class_name=Class&class_prefix=/&class_uri=Class&expand_uri=0&graph_uri=graph&instance_prefix=&instance_uri=instance&lang=pt##instance"
        self.assertEqual(computed, expected)

    @patch("brainiak.utils.cache.delete")
    @patch("brainiak.utils.cache.purge")
    def test_purge_by_path(self, mock_purge, mock_delete):
        purge_by_path(u"_##json_schema", False)
        self.assertFalse(mock_purge.called)
        self.assertTrue(mock_delete.called)
        mock_delete.assert_called_with(u"_##json_schema")

    @patch("brainiak.utils.cache.purge_all_instances")
    @patch("brainiak.utils.cache.delete")
    @patch("brainiak.utils.cache.flushall")
    def test_purge_by_path_all(self, mock_flushall, mock_delete, mock_purge_all):
        purge_by_path(u"_##root", True)
        self.assertFalse(mock_delete.called)
        self.assertTrue(mock_flushall.called)

    @patch("brainiak.utils.cache.purge_all_instances")
    @patch("brainiak.utils.cache.delete")
    @patch("brainiak.utils.cache.purge")
    def test_purge_by_path_recursive(self, mock_purge, mock_delete, mock_purge_all):
        purge_by_path(u"graph@@class##type", True)
        self.assertFalse(mock_delete.called)
        self.assertTrue(mock_purge.called)
        self.assertTrue(mock_purge_all.called)
        mock_purge.assert_called_with(u"graph@@class")

    @patch("brainiak.utils.cache.delete")
    @patch("brainiak.utils.cache.purge")
    def test_purge_by_path_recursive(self, mock_purge, mock_delete):
        purge_by_path(u"graph@@class##type", False)
        self.assertFalse(mock_purge.called)
        self.assertTrue(mock_delete.called)
        mock_delete.assert_called_with(u"graph@@class##type")
