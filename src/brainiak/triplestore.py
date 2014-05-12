# -*- coding: utf-8 -*-
import copy
import time
import urllib

import requests
from requests.auth import HTTPDigestAuth
import ujson as json

from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.web import HTTPError

from brainiak import log
from brainiak.greenlet_tornado import greenlet_fetch
from brainiak.utils.config_parser import parse_section


def do_run_query(request_params, async):
    # app_name (from triplestore.ini) can't be passed forward to tornado.httpclient.HTTPRequest .
    # It raises an exception
    # Similarly, there are parameters that make requests.request fail
    request_params.pop("app_name", None)

    time_i = time.time()
    if async:
        request = HTTPRequest(**request_params)
        try:
            response = greenlet_fetch(request)
        except ClientHTTPError as e:
            if e.code == 401:
                message = 'Check triplestore user and password.'
                raise HTTPError(e.code, message=message)
            else:
                raise e
    else:
        request_params.pop("auth_mode", None)
        request_params.pop("auth_username", None)
        request_params.pop("auth_password", None)

        response = requests.request(**request_params)
    time_f = time.time()
    diff = time_f - time_i

    return response, diff


def log_request(log_params):
    """
        Just logs the request
    """
    log_params["user_ip"] = unicode(None)
    log_msg = format_post % log_params
    log.logger.info(log_msg)


def process_json_triplestore_response(response, async):
    """
        Returns a python dict with triplestore response.
        Unifying tornado and requests response.
    """
    if async:
        result_dict = json.loads(unicode(response.body))
    else:
        result_dict = response.json()
    return result_dict


def query_sparql(query, triplestore_config, async=True):
    """
    Simple interface that given a SPARQL query string returns a string representing a SPARQL results bindings
    in JSON format. For now it only works with Virtuoso, but in futurw we intend to support other databases
    that are SPARQL 1.1 complaint (including SPARQL result bindings format).
    """
    request_params = build_request_params(query, triplestore_config, async)
    log_params = copy.copy(request_params)

    response, time_diff = do_run_query(request_params, async)

    log_params["query"] = unicode(query)
    log_params["time_diff"] = time_diff
    log_request(log_params)

    result_dict = process_json_triplestore_response(response, async)
    return result_dict

# This is based on virtuoso_connector app, used by App Semantica, so QA2 Virtuoso Analyser works
format_post = u"POST - %(url)s - %(user_ip)s - %(auth_username)s [tempo: %(time_diff)s] - QUERY - %(query)s"


def build_request_params(query, triplestore_config, async):
    """
        This function creates a dict according to the param async.
        If True, a dict with args for tornado.httpclient.HTTPRequest is created.
        If False, a dict with args for requests.request interface is created.
    """
    body_params = {
        "query": unicode(query).encode("utf-8"),
        "format": "application/sparql-results+json"
    }

    body_string = urllib.urlencode(body_params)
    body_dict = {"body": body_string}

    request_params = {
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
        },
    }

    request_params.update(triplestore_config)
    if async:
        request_params.update(body_dict)
    else:
        # Considering all DIGEST authencations
        auth_credentials = HTTPDigestAuth(triplestore_config["auth_username"],
                                          triplestore_config["auth_password"])
        request_params.update({"auth": auth_credentials, "url": triplestore_config["url"]})
        request_params.update({"data": body_params})

    return request_params


class VirtuosoException(Exception):
    pass


def status(**kw):
    endpoint_dict = parse_section()
    user = kw.get("user") or endpoint_dict["auth_username"]
    password = kw.get("password") or endpoint_dict["auth_password"]
    url = kw.get("url") or endpoint_dict["url"]
    graph = u"http://semantica.globo.com/person"
    query = u"SELECT COUNT(*) WHERE {?s a owl:Class}"

    # Do not cast to unicode these lines
    failure_msg = u"Virtuoso connection %(type)s | FAILED | %(endpoint)s | %(error)s"
    success_msg = u'Virtuoso connection %(type)s | SUCCEED | %(endpoint)s'

    info = {
        "type": u"not-authenticated",
        "endpoint": url
    }

    response = sync_query(url, query, default_graph=graph)
    if response.status_code == 200:
        msg = success_msg % info
    else:
        info["error"] = u"Status code: {0}. Body: {1}".format(response.status_code, response.text)
        msg = failure_msg % info

    info = {
        "type": u"authenticated [%s:%s]" % (user, password),
        "endpoint": url
    }

    response = sync_query(url, query, default_graph=graph, auth=(user, password))

    if response.status_code == 200:
        auth_msg = success_msg % info
    else:
        info["error"] = u"Status code: {0}. Body: {1}".format(response.status_code, response.text)
        auth_msg = failure_msg % info
    msg = u"{0}<br>{1}".format(msg, auth_msg)

    return msg


def sync_query(endpoint, query, default_graph=None, auth=None):
    quoted_query = urllib.quote(query)
    url = u"{0}?query={1}&format=application%2Fjson".format(endpoint, quoted_query)
    if default_graph:
        url = url + u"&default-graph-uri={0}".format(default_graph)
    if auth:
        auth = requests.auth.HTTPDigestAuth(*auth)
    response = requests.get(url, auth=auth)

    return response
