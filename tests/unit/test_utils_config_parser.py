from unittest import TestCase
from mock import patch
from brainiak.utils.config_parser import parse_section


class ConfigParserTestCase(TestCase):

    def test_parse_existent_section(self):
        local_ini = "config/local/triplestore.ini"
        response = parse_section(local_ini, "default")
        expected_response = {
            'endpoint': 'http://localhost:8890',
            'realm': 'SPARQL',
            'app_name': 'Brainiak',
            'auth_mode': 'digest',
            'user': 'api-semantica',
            'password': 'api-semantica'
        }
        self.assertEqual(response, expected_response)

    def test_parse_inexistent_section(self):
        self.assertRaises(Exception, parse_section, "xubiru")
