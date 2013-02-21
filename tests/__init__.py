from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, AsyncHTTPTestCase


class TornadoAsyncTestCase(AsyncTestCase):

    def setUp(self):
        self.io_loop = self.get_new_ioloop()

    def tearDown(self):
        if (not IOLoop.initialized() or self.io_loop is not IOLoop.instance()):
            self.io_loop.close(all_fds=True)
        super(AsyncTestCase, self).tearDown()

    # Disabling timeout for debugging purposes
    def wait(self, condition=None, timeout=None):
        return super(TornadoAsyncTestCase, self).wait(condition, timeout)


class TornadoAsyncHTTPTestCase(AsyncHTTPTestCase):

    def setUp(self):
        self.io_loop = self.get_new_ioloop()

    def tearDown(self):
        if (not IOLoop.initialized() or self.io_loop is not IOLoop.instance()):
            self.io_loop.close(all_fds=True)
        super(AsyncHTTPTestCase, self).tearDown()

    # Disabling timeout for debugging purposes
    def wait(self, condition=None, timeout=None):
        return super(TornadoAsyncHTTPTestCase, self).wait(condition, timeout)
