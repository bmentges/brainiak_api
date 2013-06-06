from mock import patch
from unittest import TestCase

from dad.mom import MiddlewareError

from brainiak import event_bus


class EventBusTestCase(TestCase):

    @patch("brainiak.event_bus.logger")
    @patch("brainiak.event_bus.settings", NOTIFY_BUS=True)
    @patch("dad.mom.Middleware.__init__", side_effect=MiddlewareError("mocked failure"))
    def test_initialize_raises_exception(self, mocked_init, mocked_logger, mocked_settings):
        self.assertRaises(MiddlewareError, event_bus.initialize)


    @patch("brainiak.event_bus.settings", NOTIFY_BUS=True)
    @patch("brainiak.event_bus.logger")
    @patch("dad.mom.Middleware.notify")
    def test_notify_bus(self, mocked_middleware_notify, mocked_logger, mocked_settings):
        event_bus.notify_bus(action="1", klass="2", graph="3", instance="4")
        self.assertTrue(mocked_middleware_notify.called)

    @patch("brainiak.event_bus.logger")
    @patch("dad.mom.Middleware.notify", side_effect=MiddlewareError("mocked failure"))
    @patch("brainiak.event_bus.settings", NOTIFY_BUS=True)
    def test_notify_raises_exception(self, mocked_middleware_notify, mocked_notify_bus, mocked_logger):
        self.assertRaises(MiddlewareError, event_bus.notify_bus, action="1", klass="2", graph="3", instance="4")
