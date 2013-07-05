from unittest import TestCase
from mock import patch
import re
from brainiak import get_version, version
from brainiak.server import Application


class ServerTestCase(TestCase):

    @patch("brainiak.server.log.initialize", side_effect=RuntimeError())
    @patch("brainiak.server.event_bus.initialize")
    @patch("brainiak.server.sys.exit")
    def test_init_raises_exception(self, mocked_exit, mocked_event_bus_initialize, mocked_log_initialize):
        Application()
        mocked_exit.assert_called_with(1)

    # def test_version(self):
    #     pat = re.compile("\w+\s+\|\s+\w+")
    #     m = pat.match(get_version())
    #     self.assertIsNotNone(m)

    @patch("brainiak.get_code_version", return_value='1.0')
    @patch("brainiak.is_available", return_value=True)
    def test_mock_git_available(self, mock1, mock2):
        self.assertEqual(get_version(), '1.0')

    @patch("brainiak.get_code_version", return_value='1.0')
    @patch("brainiak.is_available", return_value=False)
    def test_mock_git_available(self, mock1, mock2):
        self.assertEqual(get_version(), version.RELEASE)
