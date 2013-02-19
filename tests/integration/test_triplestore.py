from tests import TornadoAsyncTestCase
from brainiak import triplestore


class TriplestoreTestCase(TornadoAsyncTestCase):

    def is_response_ok(self, response):
        self.assertEquals(response.code, 200)
        self.stop()

    def test_query_ok(self):
        SIMPLE_COUNT_CLASSES_QUERY = "SELECT COUNT(*) WHERE {?s a owl:Class}"
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.is_response_ok, SIMPLE_COUNT_CLASSES_QUERY)
        self.wait()
