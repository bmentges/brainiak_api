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


def _query_sparql(query, credentials):
    # will parse the ini file to endpoint_dict
    # will call query_sparql_to_endpoint
    pass


def query_sparql_to_endpoint(query, endpoint_dict):
    # will send the request to the triplestore, using endpoint_dict
    pass


# TODO: compute runtime
# TODO: log query and runtime
def query_sparql(query, *args, **kw):
    """
    Simple interface that given a SPARQL query string returns a string representing a SPARQL results bindings
    in JSON format. For now it only works with Virtuoso, but in futurw we intend to support other databases
    that are SPARQL 1.1 complaint (including SPARQL result bindings format).
    """
    try:
        query_response = run_query(query, *args, **kw)
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


def endpoint_url():
    url = getattr(settings, "SPARQL_ENDPOINT", None)
    if url is None:
        host = settings.SPARQL_ENDPOINT_HOST
        port = settings.SPARQL_ENDPOINT_PORT
        url = "{0}:{1}".format(host, port)
    return url

# This is based on virtuoso_connector app, used by App Semantica, so QA2 Virtuoso Analyser works
format = "POST - %(url)s - %(user_ip)s - %(auth_username)s [tempo: %(time_diff)s] - QUERY - %(query)s"


def run_query(query, *args, **kw):
    method = kw.get("method", "POST")
    params = {
        "query": unicode(query).encode("utf-8"),
        "format": kw.get("result_format", DEFAULT_FORMAT)
    }
    body = urllib.urlencode(params) if method == "POST" else ""
    url = endpoint_url()
    url = url if method == "POST" else url_concat(url, params)

    request_params = {
        "url": url,
        "method": method,
        "headers": {"Content-Type": DEFAULT_CONTENT_TYPE},
        "body": body,
        "auth_username": getattr(settings, "SPARQL_ENDPOINT_USER", None),
        "auth_password": getattr(settings, "SPARQL_ENDPOINT_PASSWORD", None),
        "auth_mode": getattr(settings, "SPARQL_ENDPOINT_AUTH_MODE", "basic"),
    }
    request = HTTPRequest(**request_params)

    time_i = time.time()
    response = greenlet_fetch(request)
    time_f = time.time()

    request_params["time_diff"] = time_f - time_i
    request_params["query"] = query
    request_params["user_ip"] = str(None)
    log_msg = format % request_params
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
            # note that msg is used due to SPARQLWrapper.SPARQLExceptions.py
            # implementation of error messages
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
