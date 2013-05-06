# -*- coding: utf-8 -*-
import time
import ujson as json
import stomp
from mock import patch
from stomp.exception import NotConnectedException, ConnectionClosedException, \
    ProtocolException

from brainiak import server
from brainiak import handlers
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

        self.original_send = event_bus_connection.send
        self.original_log = handlers.logger

        class MockLogger(object):
            @staticmethod
            def error(*args, **kw):
                pass
        handlers.log = MockLogger()

    def tearDown(self):
        event_bus_connection.stop()
        self.connection_message_queue_solr.stop()
        self.connection_message_queue_elastic.stop()
        event_bus_connection.send = self.original_send
        handlers.logger = self.original_log

    @patch("brainiak.handlers.logger")
    @patch("brainiak.event_bus.logger")
    def test_notify_event_bus_on_put(self, log, log2):
        expected_message = {
            "instance": "http://tatipedia.org/new_york",
            "class": "http://tatipedia.org/Place",
            "graph": "http://somegraph.org/",
            "action": "PUT"
        }

        actual_new_york = self.fetch('/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
                                     method='GET')
        self.assertEqual(actual_new_york.code, 200)
        actual_new_york_dict = json.loads(actual_new_york.body)
        actual_new_york_dict["rdfs:comment"] = "Some random comment"

        modified_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='PUT',
            body=json.dumps(actual_new_york_dict))
        self.assertEqual(modified_new_york.code, 200)
        self.assertEqual(message_queue_solr[0], json.dumps(expected_message))
        self.assertEqual(message_queue_elastic[0], json.dumps(expected_message))

    @patch("brainiak.event_bus.logger")
    @patch("brainiak.handlers.logger")
    def test_notify_event_bus_on_delete(self, log, log2):
        expected_message = {
            "instance": "http://tatipedia.org/new_york",
            "class": "http://tatipedia.org/Place",
            "graph": "http://somegraph.org/",
            "action": "DELETE"
        }

        deleted_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='DELETE')
        self.assertEqual(deleted_new_york.code, 204)

        self.assertEqual(message_queue_solr[0], json.dumps(expected_message))
        self.assertEqual(message_queue_elastic[0], json.dumps(expected_message))

    @patch("brainiak.event_bus.logger")
    @patch("brainiak.handlers.logger")
    def test_notify_event_bus_on_post(self, log, log2):
        CSA_FOOTBALL_TEAM = {
            "@context": {
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "tpedia": "http://tatipedia.org/"
            },
            u"rdfs:label": u"Centro Sportivo Alagoano",
            u"tpedia:stadium": u"Estádio Rei Pelé"
        }

        part_of_expected_message = {  # there is no "instance" because POST generates it
            "class": "http://tatipedia.org/SoccerClub",
            "graph": "http://somegraph.org/",
            "action": "POST"
        }

        modified_new_york = self.fetch(
            '/tpedia/SoccerClub/?class_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='POST',
            body=json.dumps(CSA_FOOTBALL_TEAM))
        self.assertEqual(modified_new_york.code, 201)
        self.assertDictContainsSubset(part_of_expected_message, json.loads(message_queue_solr[0]))
        self.assertDictContainsSubset(part_of_expected_message, json.loads(message_queue_elastic[0]))

    @patch("brainiak.handlers.logger")
    @patch("brainiak.event_bus.logger")
    def test_notify_bus_not_connected_exception(self, log, log2):
        config = {"side_effect": NotConnectedException}
        patcher = patch("brainiak.event_bus.event_bus_connection.send", **config)
        patcher.start()

        deleted_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='DELETE')
        self.assertEqual(deleted_new_york.code, 500)
        patcher.stop()

    @patch("brainiak.event_bus.logger")
    @patch("brainiak.handlers.logger")
    def test_notify_bus_connection_closed_exception(self, log, log2):
        #config = {"side_effect": ConnectionClosedException}
        #patcher = patch("brainiak.event_bus.event_bus_connection.send", **config)
        #patcher.start()
        def mock_send(*args, **kw):
            raise ConnectionClosedException()
        event_bus_connection.send = mock_send
        try:
            deleted_new_york = self.fetch(
                '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
                method='DELETE')
            self.assertEqual(deleted_new_york.code, 500)

        finally:
            event_bus_connection.send = self.original_send
        #patcher.stop()

    @patch.object(event_bus_connection, "send", side_effect=ProtocolException())
    @patch("brainiak.event_bus.logger")
    @patch("brainiak.handlers.logger")
    def test_notify_bus_protocol_exception(self, log, log2, mock_method):
        deleted_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='DELETE')
        self.assertEqual(deleted_new_york.code, 500)


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
