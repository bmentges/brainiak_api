import unittest

from mock import patch

from brainiak.utils.decorator import memoize
from tests.mocks import MockRequest


class MemoizeDecoratorTestCase(unittest.TestCase):

    @patch("brainiak.utils.decorator.settings", ENABLE_CACHE=False)
    @patch("brainiak.utils.decorator.redis_server.set")
    @patch("brainiak.utils.decorator.redis_server.get")
    def test_memoize_cache_disabled(self, redis_get, redis_set, settings):

        @memoize
        def clean_up(params):
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = clean_up(params)

        self.assertEquals(answer, {"status": "Laundry done"})
        self.assertEquals(redis_get.call_count, 0)
        self.assertEquals(redis_set.call_count, 0)

    @patch("brainiak.utils.decorator.settings", ENABLE_CACHE=True)
    @patch("brainiak.utils.decorator.redis_server.set", return_value=True)
    @patch("brainiak.utils.decorator.redis_server.get", return_value=None)
    def test_memoize_cache_enabled_but_without_cache(self, redis_get, redis_set, settings):

        @memoize
        def clean_up(params):
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = clean_up(params)

        self.assertEquals(answer, {"status": "Laundry done"})
        self.assertEquals(redis_get.call_count, 1)
        self.assertEquals(redis_set.call_count, 1)

    @patch("brainiak.utils.decorator.settings", ENABLE_CACHE=True)
    @patch("brainiak.utils.decorator.redis_server.set", return_value=True)
    @patch("brainiak.utils.decorator.redis_server.get", return_value='{"status": "Dishes cleaned up"}')
    def test_memoize_cache_enabled_but_with_cache(self, redis_get, redis_set, settings):

        @memoize
        def clean_up(params):
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = clean_up(params)

        self.assertEquals(answer, {"status": "Dishes cleaned up"})
        self.assertEquals(redis_get.call_count, 1)
        self.assertEquals(redis_set.call_count, 0)
