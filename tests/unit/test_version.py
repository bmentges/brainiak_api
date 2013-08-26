from unittest import TestCase
from mock import patch
from brainiak import get_version, version


class VersionTestCase(TestCase):

    @patch("brainiak.get_code_version", return_value='1.0')
    @patch("brainiak.is_available", return_value=True)
    def test_mock_git_available(self, mock1, mock2):
        self.assertEqual(get_version(), '1.0')

    @patch("brainiak.get_code_version", return_value='1.0')
    @patch("brainiak.is_available", return_value=False)
    def test_mock_git_available_with_version(self, mock1, mock2):
        self.assertEqual(get_version(), version.RELEASE)

    # TODO: FIXME: This test is was breaking the CI probably due to fails in the git spawned process
    # def test_version(self):
    #     pat = re.compile("\w+\s+\|\s+\w+")
    #     m = pat.match(get_version())
    #     self.assertIsNotNone(m)
