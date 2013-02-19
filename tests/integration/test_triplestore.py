from tornado.testing import AsyncTestCase
from tornado.ioloop import IOLoop

from brainiak import triplestore


class TriplestoreTestCase(AsyncTestCase):

    def setUp(self):
        self.io_loop = self.get_new_ioloop()

    def tearDown(self):
        if (not IOLoop.initialized() or self.io_loop is not IOLoop.instance()):
            self.io_loop.close(all_fds=True)
        super(AsyncTestCase, self).tearDown()

    def is_response_ok(self, response):
        self.assertEquals(response.code, 200)
        self.stop()

    def test_query_ok(self):
        SIMPLE_COUNT_CLASSES_QUERY = "SELECT COUNT(*) WHERE {?s a owl:Class}"
        virtuoso_connection = triplestore.VirtuosoConnection(self.io_loop)
        virtuoso_connection.query(self.is_response_ok, SIMPLE_COUNT_CLASSES_QUERY)
        self.wait(timeout=None)  # disable timeout for debugging purposes
