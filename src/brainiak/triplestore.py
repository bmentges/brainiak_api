# -*- coding: utf-8 -*-
import copy
import time
import urllib

import requests
from requests.auth import HTTPDigestAuth
import ujson as json
from simplejson import JSONDecodeError

from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.web import HTTPError

from brainiak import log
from brainiak.greenlet_tornado import greenlet_fetch
from brainiak.utils.config_parser import parse_section


JSON_DECODE_ERROR_MESSAGE = "Could not decode JSON:\n  {0}"
UNAUTHORIZED_MESSAGE = 'Check triplestore user and password.'

DEFAULT_VIRTUOSO_REQUEST_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded"
}
DEFAULT_RESPONSE_FORMAT = "application/sparql-results+json"
DEFAULT_HTTP_METHOD = "POST"


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
                raise HTTPError(e.code, message=UNAUTHORIZED_MESSAGE)
            else:
                raise e
    else:
        request_params.pop("auth_mode", None)
        request_params.pop("auth_username", None)
        request_params.pop("auth_password", None)

        response = requests.request(**request_params)
        if response.status_code == 401:
            raise HTTPError(401, message=UNAUTHORIZED_MESSAGE)

    time_f = time.time()
    diff = time_f - time_i

    return response, diff


def log_request(log_params):
    """
        Just logs the request
    """
    log_params["user_ip"] = unicode(None)
    log_params["auth_username"] = log_params.get("auth_username", None)
    log_msg = format_post % log_params
    log.logger.info(log_msg)


def _process_json_triplestore_response(response, async=True):
    """
        Returns a python dict with triplestore response.
        Unifying tornado and requests response.
    """
    if async:
        result_dict = json.loads(unicode(response.body))
    else:
        try:
            result_dict = response.json()
        except JSONDecodeError:
            raise ClientHTTPError(400, JSON_DECODE_ERROR_MESSAGE.format(response.text))
    return result_dict


def query_sparql(query, triplestore_config, async=True):
    """
    Simple interface that given a SPARQL query string returns a string representing a SPARQL results bindings
    in JSON format. For now it only works with Virtuoso, but in futurw we intend to support other databases
    that are SPARQL 1.1 complaint (including SPARQL result bindings format).
    """
    request_params = _build_request_params(query, triplestore_config, async)
    log_params = copy.copy(request_params)

    response, time_diff = do_run_query(request_params, async)

    log_params["query"] = unicode(query)
    log_params["time_diff"] = time_diff
    log_request(log_params)

    result_dict = _process_json_triplestore_response(response, async)
    return result_dict

# This is based on virtuoso_connector app, used by App Semantica, so QA2 Virtuoso Analyser works
format_post = u"POST - %(url)s - %(user_ip)s - %(auth_username)s [tempo: %(time_diff)s] - QUERY - %(query)s"


def _build_request_params(query, triplestore_config, async):
    """
        This function creates a dict according to the param async.
        If True, a dict with args for tornado.httpclient.HTTPRequest is created.
        If False, a dict with args for requests.request interface is created.
    """
    body_params = {
        "query": unicode(query).encode("utf-8"),
        "format": DEFAULT_RESPONSE_FORMAT
    }

    body_string = urllib.urlencode(body_params)
    body_dict = {"body": body_string}

    request_params = {
        "method": DEFAULT_HTTP_METHOD,
        "headers": DEFAULT_VIRTUOSO_REQUEST_HEADERS,
    }

    request_params.update(triplestore_config)
    if async:
        request_params.update(body_dict)
    else:
        request_params.update({
            "data": body_params,
            "url": triplestore_config["url"]})
        if "auth_mode" in triplestore_config and \
           "auth_username" in triplestore_config and  \
           "auth_password" in triplestore_config:
            # Considering all DIGEST authencations
            auth_credentials = HTTPDigestAuth(triplestore_config["auth_username"],
                                              triplestore_config["auth_password"])
            request_params.update({"auth": auth_credentials})

    return request_params


class VirtuosoException(Exception):
    pass


VIRTUOSO_FAILURE_MESSAGE = u"Virtuoso connection %(type)s | FAILED | %(endpoint)s | %(error)s"
VIRTUOSO_SUCCESS_MESSAGE = u'Virtuoso connection %(type)s | SUCCEED | %(endpoint)s'


def status():

    endpoint_dict = parse_section()
    unauthorized_endpoint_dict = copy.copy(endpoint_dict)

    query = u"""
        SELECT COUNT(*)
        FROM <http://semantica.globo.com/person>
        WHERE {?s a owl:Class}
    """

    info = {
        "type": u"authenticated [%s:%s]" % (endpoint_dict["auth_username"],
                                            endpoint_dict["auth_password"]),
        "endpoint": endpoint_dict["url"]
    }

    auth_msg = _run_status_request(query, endpoint_dict, info)

    unauthorized_endpoint_dict.pop("auth_mode", None)

    info.update({
        "type": u"not-authenticated",
    })

    non_auth_msg = _run_status_request(query, unauthorized_endpoint_dict, info)

    msg = u"{0}<br>{1}".format(auth_msg, non_auth_msg)

    return msg


def _run_status_request(query, endpoint_dict, info):
    try:
        query_sparql(query, endpoint_dict, async=False)
    except (ClientHTTPError, HTTPError) as e:
        # Reason for this: ClientHTTPError has one pattern and HTTPError for status code attribute
        code = hasattr(e, "status_code") and e.status_code
        if not code:
            code = hasattr(e, "code") and e.code

        info["error"] = u"Status code: {0}. Message: {1}".format(code, e.message)
        message = VIRTUOSO_FAILURE_MESSAGE % info
    else:
        message = VIRTUOSO_SUCCESS_MESSAGE % info
    return message
