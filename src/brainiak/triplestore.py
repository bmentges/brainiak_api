from tornado import gen
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest
from tornado.escape import url_escape

from brainiak import settings, utils


def query_sparql(callback, query, **kw):
    """
    Simple interface that given a SPARQL query string returns a string representing a SPARQL results bindings
    in JSON format. For now it only works with Virtuoso, but in futurw we intend to support other databases
    that are SPARQL 1.1 complaint (including SPARQL result bindings format).
    """
    connection = VirtuosoConnection()
    connection.query(callback, query, **kw)

SPARQL_RESULTS_FORMAT = {
    "json": "application/sparql-results+json",
    "turtle": "text/rdf+n3"
}

DEFAULT_FORMAT = SPARQL_RESULTS_FORMAT["json"]

URL_ENCODED = "application/x-www-form-urlencoded"

DEFAULT_CONTENT_TYPE = URL_ENCODED


class VirtuosoConnection(object):

    def __init__(self, io_loop=None):
        if hasattr(settings, "SPARQL_ENDPOINT_FULL_URL"):
            self.endpoint_url = settings.SPARQL_ENDPOINT_FULL_URL
        else:
            self.host = settings.SPARQL_ENDPOINT_HOST
            self.port = settings.SPARQL_ENDPOINT_PORT
            self.endpoint_url = self.host + ":" + str(self.port) + "/sparql"

        self.io_loop = io_loop or IOLoop.instance()
        self.client = utils.get_tornado_async_client(self.io_loop)

    @gen.engine
    def query(self, callback, query, method="POST", result_format=DEFAULT_FORMAT, content_type=DEFAULT_CONTENT_TYPE, **kw):
        body_encoded = url_escape("query=" + query)
        headers = {
            "Accept": result_format,
            "Content-Type": content_type
            #"format": result_format
        }
        request = HTTPRequest(url=self.endpoint_url,
                              method="POST",
                              headers=headers,
                              body=body_encoded)
        response = yield gen.Task(self.client.fetch, request)
        callback(response, **kw)
