from mock import patch
import time

import ujson as json
import stomp

from brainiak import server
from brainiak.event_bus import event_bus_connection
from brainiak.settings import EVENT_BUS_HOST, EVENT_BUS_PORT

from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase

message_queue_solr = []
message_queue_elastic = []


class BusNotificationTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    # The class variables below are handled by QueryTestCase
    allow_triplestore_connection = True
    graph_uri = "http://somegraph.org/"
    fixtures = ["tests/sample/instances.n3"]

    def get_app(self):
        return server.Application()

    def setUp(self):
        super(BusNotificationTestCase, self).setUp()
        event_bus_connection.start()
        event_bus_connection.connect()
        event_bus_connection.set_listener("listener", NotifierListener())

        self.connection_message_queue_solr = stomp.Connection(host_and_ports=[(EVENT_BUS_HOST, EVENT_BUS_PORT)])
        self.connection_message_queue_solr.start()
        self.connection_message_queue_solr.connect()
        global message_queue_solr
        self.connection_message_queue_solr.set_listener("listener", SolrQueueListener())
        self.connection_message_queue_solr.subscribe(destination="/queue/solr", ack='auto')

        self.connection_message_queue_elastic = stomp.Connection(host_and_ports=[(EVENT_BUS_HOST, EVENT_BUS_PORT)])
        self.connection_message_queue_elastic.start()
        self.connection_message_queue_elastic.connect()
        global message_queue_elastic
        self.connection_message_queue_elastic.set_listener("listener", ElasticQueueListener())
        self.connection_message_queue_elastic.subscribe(destination="/queue/elasticsearch", ack='auto')

    def tearDown(self):
        event_bus_connection.stop()
        self.connection_message_queue_solr.stop()
        self.connection_message_queue_elastic.stop()

    @patch("brainiak.handlers.log")
    def test_notify_event_bus_on_put_instance(self, log):
        expected_message = {
            "instance": "http://tatipedia.org/new_york",
            "class": "http://tatipedia.org/Place",
            "graph": "http://somegraph.org/",
            "action": "PUT"
        }
        modified_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='PUT',
            body=json.dumps({}))
        self.assertEqual(modified_new_york.code, 200)
        self.assertEqual(message_queue_solr[0], json.dumps(expected_message))
        self.assertEqual(message_queue_elastic[0], json.dumps(expected_message))

    @patch("brainiak.handlers.log")
    def test_notify_event_bus_on_delete_instance(self, log):
        expected_message = {
            "instance": "http://tatipedia.org/new_york",
            "class": "http://tatipedia.org/Place",
            "graph": "http://somegraph.org/",
            "action": "DELETE"
        }

        modified_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='PUT',
            body=json.dumps({}))
        self.assertEqual(modified_new_york.code, 200)

        deleted_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='DELETE')
        self.assertEqual(deleted_new_york.code, 204)

        self.assertEqual(message_queue_solr[0], json.dumps(expected_message))
        self.assertEqual(message_queue_elastic[0], json.dumps(expected_message))


class NotifierListener(object):

    def on_send(self, headers, body):
        # necessary for the subscribers to read the sent message
        time.sleep(2)


class SolrQueueListener(object):

    def on_message(self, headers, message):
        global message_queue_solr
        message_queue_solr = []
        message_queue_solr.append(message)


class ElasticQueueListener(object):

    def on_message(self, headers, message):
        global message_queue_elastic
        message_queue_elastic = []
        message_queue_elastic.append(message)
