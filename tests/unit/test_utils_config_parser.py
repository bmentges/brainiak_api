from unittest import TestCase
from brainiak.utils.config_parser import ConfigParserNoSectionError, parse_section


class ConfigParserTestCase(TestCase):

    def test_parse_default_config_file_and_default_section(self):
        response = parse_section()
        expected_response = {
            'url': 'http://localhost:8890/sparql-auth',
            'app_name': 'Brainiak',
            'auth_mode': 'digest',
            'auth_username': 'dba',
            'auth_password': 'dba'
        }
        self.assertEqual(response, expected_response)

    def test_parse_config_file_and_other_section(self):
        local_ini = "src/brainiak/triplestore.ini"
        response = parse_section(local_ini, "other")
        expected_response = {
            'url': 'http://localhost:8890/sparql-auth',
            'app_name': 'Other',
            'auth_mode': 'digest',
            'auth_username': 'one_user',
            'auth_password': 'one_password'
        }
        self.assertEqual(response, expected_response)

    def test_parse_inexistent_section(self):
        self.assertRaises(ConfigParserNoSectionError, parse_section, "xubiru")
