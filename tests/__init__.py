from tornado.testing import AsyncTestCase, AsyncHTTPTestCase
from brainiak import server, greenlet_tornado


class TornadoAsyncTestCase(AsyncTestCase):

    def setUp(self):
        super(TornadoAsyncTestCase, self).setUp()
        greenlet_tornado.greenlet_set_ioloop(self.io_loop)

    # Disabling timeout for debugging purposes
    def wait(self, condition=None, timeout=None):
        return super(TornadoAsyncTestCase, self).wait(condition, timeout)


class TornadoAsyncHTTPTestCase(AsyncHTTPTestCase):

    def setUp(self):
        super(TornadoAsyncHTTPTestCase, self).setUp()
        greenlet_tornado.greenlet_set_ioloop(self.io_loop)

    def get_app(self):
        return server.Application()

    # Disabling timeout for debugging purposes
    def wait(self, condition=None, timeout=None):
        return super(TornadoAsyncHTTPTestCase, self).wait(condition, timeout)
