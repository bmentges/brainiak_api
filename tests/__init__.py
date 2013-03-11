from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, AsyncHTTPTestCase
from brainiak import server


class TornadoAsyncTestCase(AsyncTestCase):

    # Disabling timeout for debugging purposes
    def wait(self, condition=None, timeout=None):
        return super(TornadoAsyncTestCase, self).wait(condition, timeout)


class TornadoAsyncHTTPTestCase(AsyncHTTPTestCase):

    # Disabling timeout for debugging purposes
    def wait(self, condition=None, timeout=None):
        return super(TornadoAsyncHTTPTestCase, self).wait(condition, timeout)


class TestHandlerBase(AsyncHTTPTestCase):
    brainiak_app = server.Application()

    def get_app(self):
        return self.brainiak_app

    def get_new_ioloop(self):
        return IOLoop.instance()

    # Disabling timeout for debugging purposes
    def wait(self, condition=None, timeout=None):
        return super(TestHandlerBase, self).wait(condition, timeout)
