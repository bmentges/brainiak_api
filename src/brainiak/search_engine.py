import json
import time
import urllib

from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPError as ClientHTTPError
from tornado.web import HTTPError

from brainiak import log
from brainiak.greenlet_tornado import greenlet_fetch
from brainiak.settings import ELASTICSEARCH_ENDPOINT


format_post = u"ELASTICSEARCH - %(method)s - %(url)s - %(status)s - [time: %(time_diff)s] - BODY - %(body)s"

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

    response, time_diff = _do_request(request_params)
    request_params["status"] = response.code
    request_params["time_diff"] = time_diff

    log_msg = format_post % request_params
    log.logger.info(log_msg)

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

    response, time_diff = _do_request(request_params)

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

    response, time_diff = _do_request(request_params)
    request_params["status"] = response.code
    request_params["time_diff"] = time_diff

    log_msg = format_post % request_params
    log.logger.info(log_msg)

    if response.code in (200, 201):
        creation_msg = u"Instance saved in Elastic Search.\n" +\
            u"  URL: {0}".format(request_url)
        log.logger.info(creation_msg)
        return response.code
    else:
        exception_msg = "Error on Elastic Search when saving an instance.\n  {0} {1} - {2} \n  Body: {3}"
        exception_msg = exception_msg.format(
            request_params["method"],
            request_params["url"],
            response.code,
            response.body)
        raise HTTPError(response.code, log_message=exception_msg)


def _do_request(request_params):
    request = HTTPRequest(**request_params)
    time_i = time.time()
    response = greenlet_fetch(request)
    time_f = time.time()
    time_diff = time_f - time_i
    return (response, time_diff)
