from tornado.httpclient import AsyncHTTPClient


def get_tornado_async_client(io_loop=None):
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    return AsyncHTTPClient(io_loop=io_loop)
