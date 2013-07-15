from unittest import TestCase
from mock import patch

from brainiak.utils.config_parser import parse_section
from ConfigParser import NoSectionError

class ConfigParserTestCase(TestCase):

    @patch("brainiak.utils.config_parser.ConfigParser.read")
    @patch("brainiak.utils.config_parser.ConfigParser.options", return_value=["some_key"])
    @patch("brainiak.utils.config_parser.ConfigParser.get", return_value="some_value")
    def test_config_file_with_default_section(self, mocked_get, mocked_options, mocked_read):
        expected_dict = {"some_key": "some_value"}
        self.assertEqual(expected_dict, parse_section("filename"))

    @patch("brainiak.utils.config_parser.ConfigParser.read")
    @patch("brainiak.utils.config_parser.ConfigParser.options", side_effect=NoSectionError(""))
    def test_config_file_no_default_section(self, mocked_options, mocked_read):
        self.assertRaises(RuntimeError, parse_section, "filename")
