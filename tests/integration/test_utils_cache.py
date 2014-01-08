import logging
import unittest
import json

from mock import patch, Mock

from brainiak import server
from brainiak.utils.cache import create, delete, keys, memoize, ping, purge, purge_all_instances, retrieve, redis_client, update_if_present
from tests.mocks import MockRequest
from tests.tornado_cases import TornadoAsyncHTTPTestCase


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
        ttl = redis_client.ttl("new_key")
        self.assertGreater(ttl, 80000)

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

    def test_update_if_present_when_it_is_not_present(self):
        response = update_if_present("inexistent_key", "unused_value")
        self.assertIsNone(response)

    def test_update_if_present_when_it_is_present(self):
        response = create("to_update_key", '{"key": "old value"}')
        self.assertTrue(response)

        response = retrieve("to_update_key")
        self.assertEqual(response, {"key": "old value"})

        response = update_if_present("to_update_key", '{"key": "up-to-date value"}')
        self.assertTrue(response)

        response = retrieve("to_update_key")
        self.assertEqual(response["body"], u'{"key": "up-to-date value"}')

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_memoize_cache_enabled_and_hit(self, settings):

        def clean_up():
            return {"status": "Laundry done"}

        params = Mock(request=MockRequest(uri="/home"))
        answer = memoize(params, clean_up)
        self.assertEqual(answer['status'], "Dishes cleaned up")
        self.assertEqual(answer['meta']['cache'], "HIT")

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    def test_memoize_cache_enabled_and_hit_with_different_key(self, settings):

        def ressurect():
            return {"status": "Ressurected"}

        params = {'request': MockRequest(uri="/home")}
        answer = memoize(params, ressurect, key="/grave")
        self.assertEqual(answer["status"], "Sleeping")
        self.assertEqual(answer['meta']['cache'], "HIT")


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

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    def test_cleanup_inexistent_url(self, logger, info, debug, settings):
        purge("inexistent_url")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with('Cache: 0 key(s), matching the pattern: inexistent_url')
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with('Cache: key(s) to be deleted: []')

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    def test_cleanup_existent_url(self, logger, info, debug, settings):
        purge("some_url")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with('Cache: purged with success 1 key(s), matching the pattern: some_url')
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with("Cache: key(s) to be deleted: ['some_url']")

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    def test_cleanup_2_existent_url(self, logger, info, debug, settings):
        purge("some")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with('Cache: purged with success 2 key(s), matching the pattern: some')
        self.assertEqual(debug.call_count, 1)
        try:
            debug.assert_called_with("Cache: key(s) to be deleted: ['some_url', 'some_other_url']")
        except:
            debug.assert_called_with("Cache: key(s) to be deleted: ['some_other_url', 'some_url']")

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.utils.cache.delete", return_value=False)
    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    def test_cleanup_fails(self, logger, info, debug, delete, settings):
        purge("problematic_key")
        self.assertEqual(info.call_count, 1)
        info.assert_called_with("Cache: failed purging 1 key(s), matching the pattern: problematic_key")
        self.assertEqual(debug.call_count, 1)
        debug.assert_called_with("Cache: key(s) to be deleted: ['problematic_key']")


class PurgeAllInstancesTestCase(unittest.TestCase):

    def setUp(self):
        self.assertTrue(ping())  # assert Redis is up
        create("non_default_key", {})
        create("_@@_@@inst_a##instance", {})
        create("_@@_@@inst_b@@a=1&b=2##instance", {})
        create("_##json_schema", {})
        create("_##root", {})
        create("some_graph@@some_instance##class", {})

    def tearDown(self):
        delete("non_default_key")
        delete("_@@_@@inst_a##instance")
        delete("_@@_@@inst_b@@a=1&b=2##instance")
        delete("_##json_schema")
        delete("_##root")
        delete("some_graph@@some_instance##class")

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    @patch("brainiak.utils.cache.log.logger.debug")
    @patch("brainiak.utils.cache.log.logger.info")
    @patch("brainiak.utils.cache.log", logger=logging.getLogger("xubiru"))
    def test_purge_all_instances(self, logger, info, debug, settings):
        purge_all_instances()
        self.assertEqual(retrieve("non_default_key"), {})
        self.assertEqual(retrieve("_@@_@@inst_a##instance"), None)
        self.assertEqual(retrieve("_@@_@@inst_b@@a=1&b=2##instance"), None)
        self.assertEqual(retrieve("_##json_schema"), {})
        self.assertEqual(retrieve("_##root"), {})
        self.assertEqual(retrieve("some_graph@@some_instance##class"), {})



class BaseCyclePurgeTestCase(TornadoAsyncHTTPTestCase):


    def get_app(self):
        return server.Application()

    def createInstance(self, url_suffix, data_dict):
        payload = json.dumps(data_dict)
        return self.fetch(url_suffix, method="PUT", body=payload)

    def deleteInstance(self, url_suffix):
        return self.fetch(url_suffix, method='DELETE')

    def checkInstanceIsCached(self, url_suffix):
        response = self.fetch(url_suffix)
        self.assertEqual(response.code, 200)
        self.assertTrue(response.headers['X-Cache'].startswith('HIT'))

    def checkInstanceIsNotCached(self, url_suffix):
        response = self.fetch(url_suffix)
        self.assertEqual(response.code, 200)
        self.assertTrue(response.headers['X-Cache'].startswith('MISS'))

    def setUp(self):
        super(BaseCyclePurgeTestCase, self).setUp()

    def tearDown(self):
        super(BaseCyclePurgeTestCase, self).tearDown()


class FullCycleTestCase(BaseCyclePurgeTestCase):

    dummy_city_1 = {"http://semantica.globo.com/upper/name": "Dummy city 1"}
    dummy_city_2 = {"http://semantica.globo.com/upper/name": "Dummy city 2"}

    DUMMY_CITY_1_URL_SUFFIX = '/place/City/dummyCity1'
    DUMMY_CITY_2_URL_SUFFIX = '/place/City/dummyCity2'

    def setUp(self):
        super(FullCycleTestCase, self).setUp()
        response = self.createInstance(self.DUMMY_CITY_1_URL_SUFFIX, self.dummy_city_1)
        self.assertEqual(response.code, 201)
        response = self.createInstance(self.DUMMY_CITY_2_URL_SUFFIX, self.dummy_city_2)
        self.assertEqual(response.code, 201)

    def tearDown(self):
        response = self.deleteInstance(self.DUMMY_CITY_1_URL_SUFFIX)
        self.assertEqual(response.code, 204)
        response = self.deleteInstance(self.DUMMY_CITY_2_URL_SUFFIX)
        self.assertEqual(response.code, 204)
        super(FullCycleTestCase, self).tearDown()

    @patch("brainiak.utils.cache.settings", ENABLE_CACHE=True)
    @patch("brainiak.handlers.settings", ENABLE_CACHE=True)
    @patch("brainiak.handlers.logger")
    def test_purge_dummy1_but_keep_dummy2(self, mock_log, mock_cache, mock_cache2):
        self.checkInstanceIsNotCached(self.DUMMY_CITY_1_URL_SUFFIX)
        self.checkInstanceIsNotCached(self.DUMMY_CITY_2_URL_SUFFIX)

        # Check that both instances are retrived from cache
        self.checkInstanceIsCached(self.DUMMY_CITY_1_URL_SUFFIX)
        self.checkInstanceIsCached(self.DUMMY_CITY_2_URL_SUFFIX)

        # Purge just instance 1
        response = self.fetch(self.DUMMY_CITY_1_URL_SUFFIX, method='PURGE')
        self.assertEqual(response.code, 200)

        # Validate that instance 1 is fresh and 2 is still cached
        self.checkInstanceIsNotCached(self.DUMMY_CITY_1_URL_SUFFIX)
        self.checkInstanceIsCached(self.DUMMY_CITY_2_URL_SUFFIX)
