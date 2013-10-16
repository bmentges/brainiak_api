# -*- coding: utf-8 -*-
import md5
import time
import urllib

import SPARQLWrapper
from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.web import HTTPError
import ujson as json

from brainiak import log
from brainiak.greenlet_tornado import greenlet_fetch
from brainiak.utils.config_parser import parse_section


def query_sparql(query, triplestore_config):
    """
    Simple interface that given a SPARQL query string returns a string representing a SPARQL results bindings
    in JSON format. For now it only works with Virtuoso, but in futurw we intend to support other databases
    that are SPARQL 1.1 complaint (including SPARQL result bindings format).
    """
    try:
        query_response = run_query(query, triplestore_config)
    except ClientHTTPError as e:
        if e.code == 401:
            message = 'Check triplestore user and password.'
            raise HTTPError(e.code, message=message)
        else:
            raise e

    result_dict = json.loads(query_response.body)
    return result_dict

# This is based on virtuoso_connector app, used by App Semantica, so QA2 Virtuoso Analyser works
format_post = u"POST - %(url)s - %(user_ip)s - %(auth_username)s [tempo: %(time_diff)s] - QUERY - %(query)s"


def run_query(query, triplestore_config):
    params = {
        "query": unicode(query).encode("utf-8"),
        "format": "application/sparql-results+json"
    }
    body = urllib.urlencode(params)

    request_params = {
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "body": body
    }

    request_params.update(triplestore_config)
    # app_name (from triplestore.ini) can't be passed forward to HTTPRequest
    # it raises exception
    request_params.pop("app_name")

    request = HTTPRequest(**request_params)
    time_i = time.time()
    response = greenlet_fetch(request)
    time_f = time.time()

    request_params["time_diff"] = time_f - time_i
    request_params["query"] = unicode(query)
    request_params["user_ip"] = str(None)
    log_msg = format_post % request_params
    log.logger.info(log_msg)

    return response


class VirtuosoException(Exception):
    pass


def status(**kw):
    endpoint_dict = parse_section()
    user = kw.get("user") or endpoint_dict["auth_username"]
    password = kw.get("password") or endpoint_dict["auth_password"]
    mode = kw.get("mode") or endpoint_dict["auth_mode"]
    url = kw.get("url") or endpoint_dict["url"]

    query = "SELECT COUNT(*) WHERE {?s a owl:Class}"
    endpoint = SPARQLWrapper.SPARQLWrapper(url)
    endpoint.addDefaultGraph("http://semantica.globo.com/person")
    endpoint.setQuery(query)

    # Do not cast to unicode these lines
    failure_msg = "Virtuoso connection %(type)s | FAILED | %(endpoint)s | %(error)s"
    success_msg = 'Virtuoso connection %(type)s | SUCCEED | %(endpoint)s'

    info = {
        "type": "not-authenticated",
        "endpoint": url
    }

    try:
        endpoint.query()
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

    password_md5 = md5.new(password).digest()  # do not cast to unicode here
    info = {
        "type": "authenticated [%s:%s]" % (user, password_md5),
        "endpoint": url
    }

    endpoint.setCredentials(user, password, mode=mode, realm="SPARQL")

    try:
        endpoint.query()
        msg = msg + "<br>" + success_msg % info
    except Exception as error:
        if hasattr(error, 'msg'):
            message = error.msg
        else:
            message = str(error)

        info["error"] = message
        msg = msg + "<br>" + failure_msg % info

    return msg
