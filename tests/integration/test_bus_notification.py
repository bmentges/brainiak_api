from mock import patch
import ujson as json
from brainiak import server
from brainiak.event_bus import event_bus_connection, EVENT_BUS_TOPIC

from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase

messageQueue = []


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
        event_bus_connection.set_listener("listener", BusListener())
        event_bus_connection.start()
        event_bus_connection.connect()
        event_bus_connection.subscribe(destination=EVENT_BUS_TOPIC, ack='auto')

    def tearDown(self):
        global messageQueue
        messageQueue = []

    @patch("brainiak.handlers.log")
    def test_edit_instance_200_adding_predicate(self, log):
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
        self.assertEqual(messageQueue[0], json.dumps(expected_message))


class BusListener(object):

    def on_message(self, headers, message):
        messageQueue.append(message)
