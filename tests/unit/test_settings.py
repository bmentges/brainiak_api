import logging
import unittest

from brainiak import settings


class TestCase(unittest.TestCase):

    def test_default_local_variables(self):
        self.assertEqual(settings.CORS_HEADERS, 'Content-Type, Authorization')
        self.assertEqual(settings.DEBUG, True)
        self.assertEqual(settings.DEFAULT_LANG, 'pt')
        self.assertEqual(settings.DEFAULT_PAGE, '0')
        self.assertEqual(settings.DEFAULT_PER_PAGE, '10')
        self.assertEqual(settings.DEFAULT_RULESET_URI, "http://semantica.globo.com/ruleset")
        self.assertEqual(settings.DEFAULT_URI_EXPANSION, '0')
        self.assertEqual(settings.GRAPHS_WITHOUT_INSTANCES, ["http://semantica.globo.com/upper/"])
        self.assertEqual(settings.ELASTICSEARCH_ENDPOINT, 'localhost:9200')
        self.assertEqual(settings.ENABLE_CACHE, False)
        self.assertEqual(settings.EVENT_BUS_HOST, 'localhost')
        self.assertEqual(settings.EVENT_BUS_PORT, 61613)
        self.assertEqual(settings.ES_ANALYZER, 'default')
        self.assertEqual(settings.LOG_FILEPATH, '/tmp/brainiak.log')
        self.assertEqual(settings.LOG_LEVEL, logging.DEBUG)
        self.assertEqual(settings.LOG_NAME, 'brainiak')
        self.assertEqual(settings.NOTIFY_BUS, True)
        self.assertEqual(settings.REDIS_ENDPOINT, 'localhost')
        self.assertEqual(settings.REDIS_PORT, 6379)
        self.assertEqual(settings.SERVER_PORT, 5100)
        self.assertEqual(settings.TRIPLESTORE_CONFIG_FILEPATH, 'src/brainiak/triplestore.ini')
        self.assertEqual(settings.URI_PREFIX, "http://semantica.globo.com/")
