import json
import time
import urllib

from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPError

from brainiak import log
from brainiak.greenlet_tornado import greenlet_fetch
from brainiak.settings import ELASTICSEARCH_ENDPOINT


REQUEST_LOG_FORMAT = u"ELASTICSEARCH - %(method)s - %(url)s - %(status)s - [time: %(time_diff)s] - BODY - %(body)s"

class ElasticSearchException(Exception):
    pass

def run_search(body, indexes=None):
    request_url = _build_elasticsearch_request_url(indexes)

    request_params = {
        "url": unicode(request_url),
        "method": u"POST",
        "headers": {u"Content-Type": u"application/x-www-form-urlencoded"},
        "body": unicode(json.dumps(body))
    }

    response = _get_response(request_params)

    return json.loads(response.body)


def _build_elasticsearch_request_url(indexes):
    request_url = "http://" + ELASTICSEARCH_ENDPOINT + "/"

    if indexes is not None:
        request_url += ",".join(indexes) + "/"
    else:
        request_url += "semantica.*/"

    request_url += "_search"

    return request_url


def run_analyze(target, analyzer, indexes):
    request_url = _build_elasticsearch_analyze_url(indexes, analyzer, target)
    request_params = {
        "url": unicode(request_url),
        "method": u"GET",
        "headers": {u"Content-Type": u"application/x-www-form-urlencoded"},
    }

    response = _get_response(request_params)

    return json.loads(response.body)


def _build_elasticsearch_analyze_url(indexes, analyzer, target):
    index_path = ",".join(indexes) if isinstance(indexes, list) else indexes

    if isinstance(target, unicode):
        target = urllib.quote_plus(target.encode('utf-8'))
    else:
        target = urllib.quote_plus(target)

    if analyzer != "default":
        request_url = "http://{0}/{1}/_analyze?analyzer={2}&text={3}".format(
            ELASTICSEARCH_ENDPOINT, index_path, analyzer, target)
    else:
        request_url = "http://{0}/{1}/_analyze?text={2}".format(
            ELASTICSEARCH_ENDPOINT, index_path, target)
    return request_url


def save_instance(entry, index_name, type_name, instance_id):
    request_url = "http://{0}/{1}/{2}/{3}".format(
        ELASTICSEARCH_ENDPOINT, index_name, type_name, instance_id
        )

    request_params = {
        "url": unicode(request_url),
        "method": u"PUT",
        "body": unicode(json.dumps(entry))
    }

    response = _get_response(request_params)

    return response.code

def get_instance(index_name, type_name, instance_id):
    request_url = "http://{0}/{1}/{2}/{3}".format(
        ELASTICSEARCH_ENDPOINT, index_name, type_name, instance_id
        )

    request_params = {
        "url": unicode(request_url),
        "method": u"GET"
    }

    response = _get_response(request_params)

    return json.loads(response.body)


def _do_request(request_params):
    request = HTTPRequest(**request_params)
    time_i = time.time()
    response = greenlet_fetch(request)
    time_f = time.time()
    time_diff = time_f - time_i

    request_params["status"] = response.code
    request_params["time_diff"] = time_diff
    request_params["body"] = response.body

    log_msg = REQUEST_LOG_FORMAT % request_params
    log.logger.info(log_msg)

    return response


def _get_response(request_params):
    try:
        response = _do_request(request_params)
        return response
    except HTTPError as e:
        # Throwing explictly tornado.httpclient.HTTPError so that
        #   handler can detect it as a backend service error
        raise e
