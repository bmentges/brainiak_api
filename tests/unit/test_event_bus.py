from mock import patch
from unittest import TestCase

from dad.mom import MiddlewareError

from brainiak import event_bus
from brainiak.event_bus import NotificationFailure


class EventBusTestCase(TestCase):

    @patch("brainiak.event_bus.logger")
    @patch("brainiak.event_bus.settings", NOTIFY_BUS=True)
    @patch("dad.mom.Middleware.__init__", side_effect=MiddlewareError("mocked failure"))
    def test_initialize_raises_exception(self, mocked_init, mocked_settings, mocked_logger):
        self.assertRaises(NotificationFailure, event_bus.initialize)

    @patch("brainiak.event_bus.logger")
    @patch("brainiak.event_bus.settings", NOTIFY_BUS=True)
    @patch("brainiak.event_bus.middleware")
    def test_notify_bus(self, mocked, mocked_settings, mocked_logger):
        event_bus.notify_bus(action="1", klass="2", graph="3", instance="4")
        self.assertTrue(mocked.notify.called)

    @patch("brainiak.event_bus.logger")
    @patch("brainiak.event_bus.settings", NOTIFY_BUS=True)
    @patch("brainiak.event_bus.middleware.notify", side_effect=MiddlewareError("mocked failure"))
    @patch("brainiak.event_bus.middleware")
    def test_notify_raises_exception(self, mocked_middleware, mocked_notify, mocked_settings, mocked_logger):
        self.assertRaises(NotificationFailure, event_bus.notify_bus, action="1", klass="2", graph="3", instance="4")
