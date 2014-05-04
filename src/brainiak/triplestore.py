# -*- coding: utf-8 -*-
import md5
import simplejson
import time
import urllib

#import SPARQLWrapper
import requests
import ujson as json
from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.web import HTTPError

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

    result_dict = json.loads(unicode(query_response.body))
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
    request_params["user_ip"] = unicode(None)
    log_msg = format_post % request_params
    log.logger.info(log_msg)

    return response


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

    #password_md5 = md5.new(password).digest()  # do not cast to unicode here
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
