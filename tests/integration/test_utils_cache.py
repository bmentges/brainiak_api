import logging
import unittest

from mock import patch

from brainiak.utils.cache import create, delete, keys, memoize, ping, purge, retrieve
from tests.mocks import MockRequest


class CacheTestCase(unittest.TestCase):

    def setUp(self):
        self.assertTrue(ping())  # assert Redis is up
        create("key_xubiru", '{"key": "value"}')
        create("key_xubiru2", '{"key": "value"}')
        create("/home", '{"status": "Dishes cleaned up", "meta": {"cache": "HIT"}}')
        create("/grave", '{"status": "Sleeping", "meta": {"cache": "HIT"}}')

    def tearDown(self):
        delete("key_xubiru")
        delete("new_key")
        delete("/home")
        delete("/grave")

    def test_create(self):
        response = create("new_key", "some value")
        self.assertTrue(response)

    def test_retrieve_inexistent(self):
        response = retrieve("inexistent_key")
        self.assertEqual(response, None)

    def test_retrieve(self):
        response = retrieve("key_xubiru")
        self.assertEqual(response, {"key": "value"})

    def test_delete(self):
        response = delete("key_xubiru")
        self.assertTrue(response)

    def test_keys(self):
        response = keys("key_xubiru")
        self.assertEqual(sorted(response), ["key_xubiru", "key_xubiru2"])

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_memoize_cache_enabled_and_hit(self, settings):

        def clean_up():
            return {"status": "Laundry done"}

        params = {'request': MockRequest(uri="/home")}
        answer = memoize(params, clean_up)
        self.assertEqual(answer, {"status": "Dishes cleaned up", "meta": {"cache": "HIT"}})

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_memoize_cache_enabled_and_hit_with_different_key(self, settings):

        def ressurect():
            return {"status": "Ressurected"}

        params = {'request': MockRequest(uri="/home")}
        answer = memoize(params, ressurect, key="/grave")
        self.assertEqual(answer, {"status": "Sleeping", "meta": {"cache": "HIT"}})


class PurgeTestCase(unittest.TestCase):

    def setUp(self):
        self.assertTrue(ping())  # assert Redis is up
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
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    def test_cleanup_inexistent_url(self, logger, info, debug):
        purge("inexistent_url")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with('Cache: 0 key(s), matching the pattern: inexistent_url')
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with('Cache: key(s) to be deleted: []')

    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    def test_cleanup_existent_url(self, logger, info, debug):
        purge("some_url")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with('Cache: purged with success 1 key(s), matching the pattern: some_url')
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with("Cache: key(s) to be deleted: ['some_url']")

    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    def test_cleanup_2_existent_url(self, logger, info, debug):
        purge("some")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with('Cache: purged with success 2 key(s), matching the pattern: some')
        self.assertEqual(debug.call_count, 1)
        try:
            debug.assert_called_with("Cache: key(s) to be deleted: ['some_url', 'some_other_url']")
        except:
            debug.assert_called_with("Cache: key(s) to be deleted: ['some_other_url', 'some_url']")

    @patch("brainiak.utils.cache.delete", return_value=False)
    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    def test_cleanup_fails(self, logger, info, debug, delete):
        purge("problematic_key")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with("Cache: failed purging 1 key(s), matching the pattern: problematic_key")
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with("Cache: key(s) to be deleted: ['problematic_key']")
