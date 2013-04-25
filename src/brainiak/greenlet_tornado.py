# This file was obtained from
# wget https://github.com/mopub/greenlet-tornado/raw/master/greenlet_tornado.py
# and then modified by rodrigo.senra@corp.globo.com

# Copyright (c) 2012 The greenlet-tornado Authors.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# Author: Simon Radford <simon@mopub.com>
# Derived from this blog article:
#   http://blog.joshhaas.com/2011/06/marrying-boto-to-tornado-greenlets-bring-them-together/

"""
These functions allow you to seamlessly use Greenlet with Tornado.
This allows you to write code as if it were synchronous, and not worry about callbacks at all.
You also don't have to use any special patterns, such as writing everything as a generator.
"""

import greenlet
import tornado.httpclient
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient

import tornado.web
from functools import wraps

# singleton objects
_io_loop = None

# Use cURL
AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


def greenlet_set_ioloop(io_loop=None):
    global _io_loop
    if io_loop is None:
        _io_loop = IOLoop.instance()
    else:
        _io_loop = io_loop


def greenlet_fetch(request, **kwargs):
    """
    Uses the tornado AsyncHTTPClient to execute a request, but blocks until the request
    is complete, yet still allows the tornado IOLoop to do other things in the meantime.

    To use this function, it must be called (either directly or indirectly) from a method
    wrapped by the greenlet_asynchronous decorator.

    The request arg may be either a string URL or an HTTPRequest object.
    If it is a string, any additional kwargs will be passed directly to AsyncHTTPClient.fetch().

    Returns an HTTPResponse object, or raises a tornado.httpclient.HTTPError exception
    on error (such as a timeout).
    """
    gr = greenlet.getcurrent()
    assert gr.parent is not None, "greenlet_fetch() can only be called (possibly indirectly) from a RequestHandler method wrapped by the greenlet_asynchronous decorator."

    def callback(response):
        gr.switch(response)
    http_client = tornado.httpclient.AsyncHTTPClient(io_loop=_io_loop)
    http_client.fetch(request, callback, **kwargs)

    # Now, yield control back to the master greenlet, and wait for data to be sent to us.
    response = gr.parent.switch()

    # Raise the exception, if any.
    response.rethrow()
    return response


def greenlet_asynchronous(wrapped_method):
    """
    Decorator that allows you to make async calls as if they were synchronous, by pausing the callstack and resuming it later.

    This decorator is meant to be used on the get() and post() methods of tornado.web.RequestHandler subclasses.

    It does not make sense to use the tornado.web.asynchronous decorator as well as this decorator.
    The returned wrapper method will be asynchronous, but the wrapped method will be synchronous.
    The request will be finished automatically when the wrapped method returns.
    """
    @tornado.web.asynchronous
    @wraps(wrapped_method)
    def wrapper(self, *args, **kwargs):

        def greenlet_base_func():
            wrapped_method(self, *args, **kwargs)
            self.finish()

        gr = greenlet.greenlet(greenlet_base_func)
        gr.switch()

    return wrapper


def greenlet_test(wrapped_method):
    """
    Decorator that allows you to make async calls as if they were synchronous, by pausing the callstack and resuming it later.

    This decorator is meant to be used on the functions that implement primitives of the API.
    """
    @wraps(wrapped_method)
    def wrapper(self, *args, **kwargs):

        def greenlet_base_func():
            wrapped_method(self, *args, **kwargs)
            self.stop()

        gr = greenlet.greenlet(greenlet_base_func)
        gr.switch()
        self.wait()

    return wrapper
