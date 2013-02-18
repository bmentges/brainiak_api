from tornado.httpclient import AsyncHTTPClient


def get_tornado_async_client():
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    return AsyncHTTPClient()
