import urllib

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat


from brainiak import settings, utils


def query_sparql(callback, query, *args, **kw):
    """
    Simple interface that given a SPARQL query string returns a string representing a SPARQL results bindings
    in JSON format. For now it only works with Virtuoso, but in futurw we intend to support other databases
    that are SPARQL 1.1 complaint (including SPARQL result bindings format).
    """
    connection = VirtuosoConnection()
    connection.query(callback, query, *args, **kw)

SPARQL_RESULTS_FORMAT = {
    "json": "application/sparql-results+json",
    "turtle": "text/rdf+n3"
}

DEFAULT_FORMAT = SPARQL_RESULTS_FORMAT["json"]

URL_ENCODED = "application/x-www-form-urlencoded"

DEFAULT_CONTENT_TYPE = URL_ENCODED


class VirtuosoConnection(object):

    def __init__(self, io_loop=None):
        if hasattr(settings, "SPARQL_ENDPOINT"):
            self.endpoint_url = settings.SPARQL_ENDPOINT
        else:
            self.host = settings.SPARQL_ENDPOINT_HOST
            self.port = settings.SPARQL_ENDPOINT_PORT
            self.endpoint_url = self.host + ":" + str(self.port) + "/sparql"

        self.io_loop = io_loop or IOLoop.instance()
        self.client = utils.get_tornado_async_client(self.io_loop)

    @gen.engine
    def query(self, callback, query, *args, **kw):
        method = kw.get("method", "POST")
        result_format = kw.get("result_format", DEFAULT_FORMAT)
        content_type = DEFAULT_CONTENT_TYPE

        headers = {
            "Content-Type": content_type,
        }

        params = {
            "query": query,
            "format": result_format
        }

        url = self.endpoint_url

        if method == "GET":
            url = url_concat(url, params)
            body = None
        elif method == "POST":
            body = urllib.urlencode(params)

        request = HTTPRequest(url=url,
                              method=method,
                              headers=headers,
                              body=body,
                              auth_username=settings.SPARQL_ENDPOINT_USER, # TODO test authentication
                              auth_password=settings.SPARQL_ENDPOINT_PASSWORD,
                              auth_mode=settings.SPARQL_ENDPOINT_AUTH_MODE
                              )
        response = yield gen.Task(self.client.fetch, request)
        callback(response, *args, **kw)


class VirtuosoException(Exception):
    pass
