# -*- coding: utf-8 -*-
import ujson as json
from mock import patch, ANY

from dad.mom import MiddlewareError

from brainiak import server, settings
from brainiak import handlers
from brainiak.event_bus import NotificationFailure
from tests.mocks import mock_schema

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
        self.original_log = handlers.logger
        self.original_do_notify_bus = settings.NOTIFY_BUS
        settings.NOTIFY_BUS = True

    def tearDown(self):
        settings.NOTIFY_BUS = self.original_do_notify_bus

    @patch("brainiak.handlers.notify_bus")
    @patch("brainiak.handlers.logger")
    @patch("brainiak.event_bus.logger")
    @patch("brainiak.instance.edit_instance.get_cached_schema", return_value=mock_schema({"rdfs:label": "string", "rdfs:comment": "string", "http://tatipedia.org/speak": "string"}, "http://tatipedia.org/Place"))
    def test_notify_event_bus_on_put(self, mock_schema, log, log2, mock_notify_bus):
        expected_message = {
            "instance": "http://tatipedia.org/new_york",
            "klass": "http://tatipedia.org/Place",
            "graph": u"http://somegraph.org/",
            "action": "PUT",
            "instance_data": ANY
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
        mock_notify_bus.assert_called_with(**expected_message)

    @patch("brainiak.handlers.notify_bus")
    @patch("brainiak.event_bus.logger")
    @patch("brainiak.handlers.logger")
    def test_notify_event_bus_on_delete(self, log, log2, mock_notify_bus):
        expected_message = {
            "instance": "http://tatipedia.org/new_york",
            "klass": "http://tatipedia.org/Place",
            "graph": "http://somegraph.org/",
            "action": "DELETE"
        }

        deleted_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='DELETE')
        self.assertEqual(deleted_new_york.code, 204)
        mock_notify_bus.assert_called_with(**expected_message)

    @patch("brainiak.handlers.notify_bus")
    @patch("brainiak.event_bus.logger")
    @patch("brainiak.handlers.logger")
    @patch("brainiak.instance.create_instance.get_cached_schema", return_value=mock_schema({"rdfs:label": "string", "http://tatipedia.org/stadium": "string"}, "http://tatipedia.org/SoccerClub"))
    def test_notify_event_bus_on_post(self, mock_schema, log, log2, mock_notify_bus):
        CSA_FOOTBALL_TEAM = {
            "@context": {
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "tpedia": "http://tatipedia.org/"
            },
            u"rdfs:label": u"Centro Sportivo Alagoano",
            u"tpedia:stadium": u"Estádio Rei Pelé"
        }

        expected_message = {
            "klass": "http://tatipedia.org/SoccerClub",
            "graph": "http://somegraph.org/",
            "action": "POST",
            "instance": ANY,
            "instance_data": ANY
        }
        response = self.fetch('/tpedia/SoccerClub/?class_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/', method='POST', body=json.dumps(CSA_FOOTBALL_TEAM))
        self.assertEqual(response.code, 201)
        mock_notify_bus.assert_called_with(**expected_message)

    @patch("brainiak.handlers.logger")
    @patch("brainiak.event_bus.logger")
    @patch("brainiak.handlers.notify_bus", side_effect=MiddlewareError('Mocked failure'))
    def test_notify_bus_not_connected_exception(self, fake_send, log, log2):
        deleted_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='DELETE')
        self.assertEqual(deleted_new_york.code, 500)

    @patch("brainiak.event_bus.logger")
    @patch("brainiak.handlers.logger")
    @patch("brainiak.handlers.notify_bus", side_effect=NotificationFailure('Mocked failure'))
    def test_notify_bus_connection_closed_exception(self, fake_send, log, log2):
        deleted_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='DELETE')
        self.assertEqual(deleted_new_york.code, 500)

    @patch("brainiak.event_bus.logger")
    @patch("brainiak.handlers.logger")
    @patch("brainiak.handlers.notify_bus", side_effect=MiddlewareError('Mocked failure'))
    def test_notify_bus_protocol_exception(self, fake_send, log, log2):
        deleted_new_york = self.fetch(
            '/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
            method='DELETE')
        self.assertEqual(deleted_new_york.code, 500)
