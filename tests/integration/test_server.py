from unittest import TestCase
from mock import patch
from brainiak.server import Application


class ServerTestCase(TestCase):

    @patch("brainiak.server.log.initialize", side_effect=RuntimeError())
    @patch("brainiak.server.event_bus.initialize")
    @patch("brainiak.server.sys.exit")
    def test_init_raises_exception(self, mocked_exit, mocked_event_bus_initialize, mocked_log_initialize):
        Application()
        mocked_exit.assert_called_with(1)
