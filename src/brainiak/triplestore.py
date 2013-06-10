# -*- coding: utf-8 -*-
import md5
import time
import urllib

import SPARQLWrapper
from tornado.httpclient import HTTPRequest, HTTPError
from tornado.httputil import url_concat
import ujson as json

from brainiak import settings, log
from brainiak.greenlet_tornado import greenlet_fetch


# This is based on virtuoso_connector app, used by App Semantica, so QA2 Virtuoso Analyser works
format = "POST - %(url)s - %(user_ip)s - %(user_name)s [tempo: %(time_diff)s] - QUERY - %(query)s"


# TODO: compute runtime
# TODO: log query and runtime
def query_sparql(query, *args, **kw):
    """
    Simple interface that given a SPARQL query string returns a string representing a SPARQL results bindings
    in JSON format. For now it only works with Virtuoso, but in futurw we intend to support other databases
    that are SPARQL 1.1 complaint (including SPARQL result bindings format).
    """
    connection = VirtuosoConnection()
    try:
        query_response = connection.query(query, *args, **kw)
    except HTTPError as e:
        if e.code == 401:
            message = 'Check triplestore user and password.'
            raise HTTPError(e.code, message=message)
        else:
            raise

    result_dict = json.loads(query_response.body)
    return result_dict


SPARQL_RESULTS_FORMAT = {
    "json": "application/sparql-results+json",
    "turtle": "text/rdf+n3"
}

DEFAULT_FORMAT = SPARQL_RESULTS_FORMAT["json"]

URL_ENCODED = "application/x-www-form-urlencoded"

DEFAULT_CONTENT_TYPE = URL_ENCODED


class VirtuosoConnection(object):

    def __init__(self):
        if hasattr(settings, "SPARQL_ENDPOINT"):
            self.endpoint_url = settings.SPARQL_ENDPOINT
        else:
            self.host = settings.SPARQL_ENDPOINT_HOST
            self.port = settings.SPARQL_ENDPOINT_PORT
            self.endpoint_url = self.host + ":" + str(self.port) + "/sparql"

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
            "query": unicode(query).encode("utf-8"),
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

        time_i = time.time()
        response = greenlet_fetch(request)
        time_f = time.time()

        time_diff = time_f - time_i
        log_msg = format % {
            'url': url,
            'user_ip': str(None),
            'user_name': self.user,
            'time_diff': time_diff,
            'query': query
        }
        log.logger.info(log_msg)

        return response


class VirtuosoException(Exception):
    pass


def status(user=settings.SPARQL_ENDPOINT_USER, password=settings.SPARQL_ENDPOINT_PASSWORD,
           mode=settings.SPARQL_ENDPOINT_AUTH_MODE, realm=settings.SPARQL_ENDPOINT_REALM):

    query = "SELECT COUNT(*) WHERE {?s a owl:Class}"
    endpoint = SPARQLWrapper.SPARQLWrapper(settings.SPARQL_ENDPOINT)
    endpoint.addDefaultGraph("http://semantica.globo.com/person")
    endpoint.setQuery(query)

    failure_msg = "Virtuoso connection %(type)s | FAILED | %(endpoint)s | %(error)s"
    success_msg = 'Virtuoso connection %(type)s | SUCCEED | %(endpoint)s'

    info = {
        "type": "not-authenticated",
        "endpoint": settings.SPARQL_ENDPOINT
    }

    try:
        response = endpoint.query()
        msg = success_msg % info
    except Exception as error:
        if hasattr(error, 'msg'):
            message = error.msg
        else:
            message = str(error)

        info["error"] = message
        msg = failure_msg % info

    password_md5 = md5.new(password).digest()
    info = {
        "type": "authenticated [%s:%s]" % (user, password_md5),
        "endpoint": settings.SPARQL_ENDPOINT
    }

    endpoint.setCredentials(user, password, mode=mode, realm=realm)

    try:
        response = endpoint.query()
        msg = msg + "<br>" + success_msg % info
    except Exception as error:
        if hasattr(error, 'msg'):
            message = error.msg
        else:
            message = str(error)

        info["error"] = message
        msg = msg + "<br>" + failure_msg % info

    return msg
