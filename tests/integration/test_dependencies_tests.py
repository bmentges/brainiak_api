import unittest

import redis
import requests
from dad.mom import Middleware
from requests.auth import HTTPDigestAuth

from brainiak import settings
from brainiak import event_bus


class ServicesTestCase(unittest.TestCase):

    def test_elasticsearch(self):
        response = requests.get("http://{0}/".format(settings.ELASTICSEARCH_ENDPOINT))
        self.assertEqual(response.status_code, 200)
        version_number = response.json()["version"]["number"]
        self.assertEqual(version_number, "0.90.12")

    def test_virtuoso(self):
        response = requests.get(
            "http://0.0.0.0:8890/sparql-auth",
            auth=HTTPDigestAuth('dba', 'dba'))
        self.assertTrue("Virtuoso version 06.01.3127", response.text)

    def test_activemq(self):
        middleware = Middleware(host=settings.EVENT_BUS_HOST, port=settings.EVENT_BUS_PORT)
        expected = 'ActiveMQ connection not-authenticated | SUCCEED | localhost:61613'
        computed = middleware.status()
        self.assertEqual(computed, expected)

    def test_redis(self):
        redis_client = redis.StrictRedis(host=settings.REDIS_ENDPOINT, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, db=0)
        computed = redis_client.ping()
        self.assertTrue(computed)

