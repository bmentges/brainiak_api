import unittest

from mock import patch

from brainiak.utils.cache import CacheError, connect, create, delete, keys, memoize, ping, purge, retrieve, safe_redis, status


class GeneralFunctionsTestCase(unittest.TestCase):

    def setUp(self):
        self.assertTrue(ping())  # assert Redis is up
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
