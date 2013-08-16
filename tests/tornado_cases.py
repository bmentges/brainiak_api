# -*- coding: utf-8 -*-

from tornado.httpclient import HTTPRequest
from tornado.testing import AsyncTestCase, AsyncHTTPTestCase
from brainiak import server, greenlet_tornado


TIMEOUT = 20


class TornadoAsyncTestCase(AsyncTestCase):

    def setUp(self):
        super(TornadoAsyncTestCase, self).setUp()
        greenlet_tornado.greenlet_set_ioloop(self.io_loop)

    # Disabling timeout for debugging purposes
    def wait(self, condition=None, timeout=None):
        return super(TornadoAsyncTestCase, self).wait(condition, TIMEOUT)


class TornadoAsyncHTTPTestCase(AsyncHTTPTestCase):

    def setUp(self):
        super(TornadoAsyncHTTPTestCase, self).setUp()
        greenlet_tornado.greenlet_set_ioloop(self.io_loop)

    def get_app(self):
        return server.Application()

    # Disabling timeout for debugging purposes
    def wait(self, condition=None, timeout=None):
        return super(TornadoAsyncHTTPTestCase, self).wait(None, TIMEOUT)

    def fetch(self, path, **kwargs):
        kwargs['url'] = self.get_url(path)
        body = kwargs.pop('body', '')
        request = HTTPRequest(**kwargs)
        request.body = body
        request.allow_nonstandard_methods = True
        self.http_client.fetch(request, self.stop, **kwargs)
        return self.wait()
