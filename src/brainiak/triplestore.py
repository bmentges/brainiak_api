import md5
import urllib

import SPARQLWrapper
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat

from brainiak import settings
from brainiak.greenlet_tornado import greenlet_fetch, greenlet_set_ioloop


AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


# TODO: compute runtime
# TODO: log query and runtime
def query_sparql(query, *args, **kw):
    """
    Simple interface that given a SPARQL query string returns a string representing a SPARQL results bindings
    in JSON format. For now it only works with Virtuoso, but in futurw we intend to support other databases
    that are SPARQL 1.1 complaint (including SPARQL result bindings format).
    """
    connection = VirtuosoConnection()
    return connection.query(query, *args, **kw)


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

        greenlet_set_ioloop(io_loop)
        self._set_credentials()

    def _set_credentials(self):
        try:
            self.user = settings.SPARQL_ENDPOINT_USER
            self.password = settings.SPARQL_ENDPOINT_PASSWORD
            self.auth_mode = settings.SPARQL_ENDPOINT_AUTH_MODE
        except AttributeError:
            self.user = self.password = self.auth_mode = None

    def query(self, query, *args, **kw):
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
                              auth_username=self.user,
                              auth_password=self.password,
                              auth_mode=self.auth_mode)
        response = greenlet_fetch(request)
        return response


class VirtuosoException(Exception):
    pass


def status(user=settings.SPARQL_ENDPOINT_USER, password=settings.SPARQL_ENDPOINT_PASSWORD,
           mode=settings.SPARQL_ENDPOINT_AUTH_MODE, realm=settings.SPARQL_ENDPOINT_REALM):

    query = "SELECT COUNT(*) WHERE {?s a owl:Class}"
    endpoint = SPARQLWrapper.SPARQLWrapper(settings.SPARQL_ENDPOINT)
    endpoint.addDefaultGraph("http://semantica.globo.com/person")
    endpoint.setQuery(query)

    try:
        response = endpoint.query()
        msg = "accessed without auth"
    except Exception, error:
        msg = "didn't access without auth because: %s" % error.msg

    endpoint.setCredentials(user, password, mode=mode, realm=realm)

    password_md5 = md5.new(password).digest()

    try:
        response = endpoint.query()
        msg += "<br>accessed with auth (%s : %s)" % (user, password_md5)
    except Exception as error:
        msg += "<br>didn't access with auth (%s : %s) because: %s" % (user, password_md5, error.msg)

    return msg
