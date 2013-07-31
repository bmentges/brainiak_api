from unittest import TestCase
from mock import patch
from brainiak.utils.config_parser import parse_section


class ConfigParserTestCase(TestCase):

    def test_parse_existent_section(self):
        local_ini = "config/local/triplestore.ini"
        response = parse_section(local_ini, "default")
        expected_response = {
            'url': 'http://localhost:8890/sparql-auth',
            'app_name': 'Brainiak',
            'auth_mode': 'digest',
            'auth_username': 'api-semantica',
            'auth_password': 'api-semantica'
        }
        self.assertEqual(response, expected_response)

    def test_parse_inexistent_section(self):
        self.assertRaises(Exception, parse_section, "xubiru")
