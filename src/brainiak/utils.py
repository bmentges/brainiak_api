from tornado.httpclient import AsyncHTTPClient


def get_async_client(self):
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    return AsyncHTTPClient()
