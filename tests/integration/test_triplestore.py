from tests import TornadoAsyncTestCase
from brainiak import triplestore

class TriplestoreTestCase(TornadoAsyncTestCase):

    def is_response_ok(self, response, *args, **kw):
        self.assertEquals(response.code, 200)
        self.stop()

    def is_malformed_query(self, response, *args, **kw):
        self.assertEquals(response.code, 400)
        self.stop()

    def test_query_ok(self):
        SIMPLE_COUNT_CLASSES_QUERY = "SELECT COUNT(*) WHERE {?s a owl:Class}"
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.is_response_ok, SIMPLE_COUNT_CLASSES_QUERY)
        self.wait()

    def test_query_ok_with_get_method(self):
        SIMPLE_COUNT_CLASSES_QUERY = "SELECT COUNT(*) WHERE {?s a owl:Class}"
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.is_response_ok, SIMPLE_COUNT_CLASSES_QUERY, method="GET")
        self.wait()

    def test_query_ok_with_unsupported_method(self):
        SIMPLE_COUNT_CLASSES_QUERY = "SELECT COUNT(*) WHERE {?s a owl:Class}"
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.raises_virtuoso_exception, SIMPLE_COUNT_CLASSES_QUERY, method="UNSUPPORTED")
        self.wait(timeout=1)

    def test_malformed_query(self):
        SIMPLE_COUNT_CLASSES_QUERY = "SELECT A MALFORMED QUERY WHERE {?s a owl:Class}"
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.is_malformed_query, SIMPLE_COUNT_CLASSES_QUERY)
        self.wait()
