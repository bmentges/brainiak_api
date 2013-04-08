from mock import patch
import json

from tests import TornadoAsyncHTTPTestCase
from brainiak.prefixes import ROOT_CONTEXT


class TestListPrefixesResource(TornadoAsyncHTTPTestCase):

    maxDiff = None

    @patch("brainiak.handlers.log")
    def test_prefixes_200(self, log):
        response = self.fetch('/prefixes', method='GET')
        self.assertEqual(response.code, 200)
        response_dict = json.loads(response.body)
        self.assertIn("root_context", response_dict)
        self.assertEqual(ROOT_CONTEXT, response_dict["root_context"])
        self.assertIn("upper", response_dict["@context"])
        self.assertIn("base", response_dict["@context"])
        self.assertIn("owl", response_dict["@context"])

    @patch("brainiak.handlers.log")
    def test_prefixes_400(self, log):
        response = self.fetch('/prefixes?root_context=wrong_param', method='GET')
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.log")
    def test_prefixes_500(self, log):
        config = {"side_effect": RuntimeError}
        patcher = patch("brainiak.handlers.list_prefixes", ** config)
        patcher.start()

        response = self.fetch('/prefixes', method='GET')
        self.assertEqual(response.code, 500)
        patcher.stop()
