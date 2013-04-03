from mock import patch

from tests import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class ListClassesResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/schemas.n3"]
    graph_uri = "http://example.onto/"

    maxDiff = None

    @patch("brainiak.handlers.log")
    def test_get_instance_400(self, log):
        response = self.fetch('/test?wrong_param=1', method='GET')
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.log")
    def test_get_instance_500(self, log):
        config = {"side_effect": NotImplementedError}
        patcher = patch("brainiak.handlers.list_classes", ** config)
        patcher.start()

        response = self.fetch('/test', method='GET')
        self.assertEqual(response.code, 500)
        patcher.stop()

    # TODO 404 ou lista vazia
#    @patch("brainiak.handlers.log")
#    def test_get_instance_404(self, log):
